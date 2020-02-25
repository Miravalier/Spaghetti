#!/usr/bin/env python3.7

import asyncio
import ssl
import websockets
import json
import psycopg2
import threading
import uuid
from collections import deque, OrderedDict, namedtuple
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from google.oauth2 import id_token
from google.auth.transport import requests


###########
# GLOBALS #
###########

# Configuration
STARTING_BALANCE = 15
DAILY_INCOME = 10
SAVINGS_APR = 0.015

# Constants
SECONDS_PER_DAY = 86400
MINUTES_PER_YEAR = 525600 # HOW DO YOU MEASURE A YEAR IN THE LIFE
NOW = datetime.now()

CHECKING = 0
SAVINGS = 1

SUCCESS = {"type": "success"}
INVALID_PARAMETERS = {"type": "error", "reason": "invalid parameters"}


###########
# CLASSES #
###########

class LRU(OrderedDict):
    def __init__(self, maxsize=128, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


def add_transaction(date, source, destination, amount):
    transaction = (date, source.account_id, destination.account_id, amount)
    source.transactions.append(transaction)
    destination.transactions.append(transaction)
    psql.execute("""
        INSERT INTO transactions (transaction_time, from_id, to_id, amount)
        VALUES (%s, %s, %s, %s)
    """, transaction)


class Account:
    cache = LRU(4096)

    def __init__(self, account_id, account_uuid, account_type, name, balance, update_time):
        self.account_id = account_id
        self.uuid = account_uuid
        self.type = account_type
        self.name = name
        self.balance = balance
        self.update_time = update_time
        self.transactions = psql.query("""
            SELECT transaction_time, from_id, to_id, amount
            FROM transactions WHERE from_id=%s OR to_id=%s
        """, (account_id, account_id))

    def grant_funds(self, amount, date=None):
        if date is None:
            date = NOW
        add_transaction(date, None, self, amount)
        self.add_balance(amount)

    def transfer_to(self, destination, amount, date=None):
        if date is None:
            date = NOW
        add_transaction(date, self, destination, amount)
        destination.add_balance(amount)
        self.subtract_balance(amount)

    def transfer_from(self, source, amount, date=None):
        if date is None:
            date = NOW
        add_transaction(date, source, self, amount)
        source.subtract_balance(amount)
        self.add_balance(amount)

    def add_balance(self, amount):
        self.update_balance(self.balance + amount)

    def subtract_balance(self, amount):
        self.update_balance(self.balance - amount)

    def update_balance(self, amount):
        self.balance = amount
        psql.execute("""
            UPDATE accounts SET account_balance=%s WHERE account_id=%s
        """, (amount, self.account_id))

    def advance_time(self):
        seconds_advanced = (NOW - self.update_time).total_seconds()
        if seconds_advanced < 60:
            return

        if self.type == CHECKING:
            self.add_balance(DAILY_INCOME * seconds_advanced / SECONDS_PER_DAY)
        elif self.type == SAVINGS:
            minutes_advanced = round(seconds_advanced / 60)
            mpr = SAVINGS_APR / MINUTES_PER_YEAR
            interest_rate = mpr ** minutes_advanced
            self.add_balance(self.balance * interest_rate)

        self.update_time = NOW
        psql.execute("""
            UPDATE accounts SET update_time=%s WHERE account_id=%s
        """, (self.update_time, self.account_id))

    @classmethod
    def lookup(cls, account_id):
        account = cls.cache.get(account_id, None)
        if account is not None:
            account.advance_time()
            return account

        account_type, name, account_uuid, balance, update_time = psql.single_query("""
            SELECT account_type, account_name, account_uuid, account_balance, update_time
            FROM accounts WHERE account_id=%s
        """, (account_id,))

        account = cls(account_id, account_uuid, account_type, name, balance, update_time)
        cls.cache[account_id] = account
        account.advance_time()
        return account


class User:
    cache = LRU(1024)

    def __init__(self, google_id, email):
        self.google_id = google_id
        self.email = email

        user_id = psql.single_query("SELECT user_id FROM users WHERE google_id=%s", (google_id,))
        if user_id:
            self.user_id = user_id
        else:
            self.user_id = psql.execute_and_return("""
                INSERT INTO users (google_id, email)
                VALUES (%s, %s)
                RETURNING user_id
            """, (google_id, email))

        account_ids = psql.query("""
            SELECT account_id, account_name
            FROM accounts WHERE user_id=%s
        """, (self.user_id,))

        self.accounts = set()
        for account_id, name in account_ids:
            Account.lookup(account_id)
            self.accounts.add(account_id)

    def create_account(self, name="Checking", type=CHECKING, balance=0):
        account_uuid = str(uuid.uuid4())
        account_id = psql.execute_and_return("""
            INSERT INTO accounts (
                account_uuid, account_name, account_type,
                account_balance, user_id, update_time
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING account_id
        """, (account_uuid, name, type, balance, self.user_id, NOW))
        self.accounts.add(account_id)
        return Account.lookup(account_id)

    @classmethod
    def lookup(cls, google_id, email):
        user = cls.cache.get(google_id, None)
        if user is not None:
            return user

        user = cls(google_id, email)
        cls.cache[google_id] = user
        return user


#######
# SQL #
#######

class PSQL:
    def __init__(self, connection_string):
        self.running = True
        self.write_semaphore = threading.Semaphore(0)
        self.write_lock = threading.Lock()
        self.pending_writes = deque()
        # Open connectons to DB
        self.read_connection = psycopg2.connect(connection_string)
        self.write_connection = psycopg2.connect(connection_string)
        # Start worker thread
        self.worker = threading.Thread(target=sql_write_worker, args=(self,))
        self.worker.start()

    def close(self):
        self.running = False
        self.read_connection.close()
        self.write_connection.close()
        self.worker.join()

    @contextmanager
    def read_write_cursor(self):
        cur = self.read_connection.cursor()
        try:
            yield cur
        finally:
            cur.close()
            self.read_connection.commit()

    @contextmanager
    def write_cursor():
        cur = self.write_connection.cursor()
        try:
            yield cur
        finally:
            cur.close()
            self.write_connection.commit()

    @contextmanager
    def read_cursor():
        cur = self.read_connection.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def execute_and_return(*args, **kwargs):
        with self.read_write_cursor() as cur:
            cur.execute(*args, **kwargs)
            result = cur.fetchone()
            if result and len(result) == 1:
                return result[0]
            else:
                return result

    def execute(*args, **kwargs):
        with self.write_lock:
            self.pending_writes.append((args, kwargs))
        self.write_semaphore.release()

    def query(*args, **kwargs):
        with self.read_cursor() as cur:
            cur.execute(*args, **kwargs)
            return cur.fetchall()

    def single_query(*args, **kwargs):
        with self.read_cursor() as cur:
            cur.execute(*args, **kwargs)
            result = cur.fetchone()
            if result and len(result) == 1:
                return result[0]
            else:
                return result


def sql_write_worker(psql):
    while psql.running:
        psql.write_semaphore.acquire()

        with psql.write_lock:
            args, kwargs = psql.pending_writes.popleft()

        with psql.write_cursor() as cur:
            cur.execute(*args, **kwargs)


psql = PSQL("dbname=spaghetti")


############
# HANDLERS #
############

@register_handler("ping")
async def _ (context, user, message, websocket):
    data = message.get("data", None)
    return {"type": "ping reply", "data": data}


@register_handler("get balance")
async def _ (context, user, message, websocket):
    account_id = message.get("account_id", None)
    if account_id is None:
        return INVALID_PARAMETERS
    elif account_id not in user.accounts:
        return INVALID_PARAMETERS

    account = Account.lookup(account_id)
    return {"type": "balance", "balance": float(account.balance)}


@register_handler("list accounts")
async def _ (context, user, message, websocket):
    return {"type": "accounts", "accounts": sorted(list(user.accounts))}


@register_handler("transfer")
async def _ (context, user, message, websocket):
    from_id = message.get("from_id", None)
    to_id = message.get("to_id", None)
    amount = message.get("amount", None)
    if from_id is None or to_id is None or amount is None:
        return INVALID_PARAMETERS
    elif from_id not in user.accounts:
        return INVALID_PARAMETERS

    source = Account.lookup(from_id)
    destination = Account.lookup(to_id)

    if source.balance < amount:
        return INVALID_PARAMETERS

    source.transfer_to(destination, amount)
    return SUCCESS


################
# REGISTRATION #
################

request_handlers = {}

def register_handler(message_type):
    def sub_register_handler(func):
        request_handlers[message_type] = func
        return func
    return sub_register_handler


#############
# MAIN LOOP #
#############

def main(port, cert_path, key_path, oauth_path):
    global GOOGLE_OAUTH_CLIENT_ID

    # Load OAUTH client id
    with open(oauth_path) as fp:
        GOOGLE_OAUTH = json.load(fp)
        GOOGLE_OAUTH_CLIENT_ID = GOOGLE_OAUTH['CLIENT_ID']

    # Set up SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(cert_path, keyfile=key_path)
    # Host server
    context = object()
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(
            partial(main_handler, context),
            "0.0.0.0",
            port,
            ssl=ssl_context
        )
    )
    asyncio.get_event_loop().run_forever()


async def main_handler(context, websocket, path):
    global NOW
    user = None

    while True:
        # Receive message
        try:
            frame = await websocket.recv()
        except websockets.exceptions.ConnectionClosedOK:
            break
        if isinstance(frame, str):
            try:
                msg = json.loads(frame)
            except json.JSONDecodeError:
                msg = {}
        else:
            raise TypeError("Unknown frame type '{}' from websocket.recv()".format(type(frame)))

        request_id = msg.get("request id", None)
        msg_type = msg.get("type", "invalid")
        reply = None

        # Before processing the message, update current time
        NOW = datetime.now()

        # Process message
        if msg_type == "auth":
            auth_token = msg.get("auth_token", None)
            if user:
                reply = {"type": "error", "reason": "already authenticated"}
            elif not auth_token:
                reply = {"type": "auth failure", "reason": "missing auth token"}
            else:
                try:
                    idinfo = id_token.verify_oauth2_token(auth_token, requests.Request(), GOOGLE_OAUTH_CLIENT_ID)

                    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                        raise ValueError('wrong issuer')

                    google_id = idinfo['sub']
                    email = idinfo['email']
                    user = User.lookup(google_id, email)
                    if not user.accounts:
                        user.create_account(balance=STARTING_BALANCE)
                    reply = {"type": "auth success", "id": user.user_id}
                except ValueError as e:
                    reply = {"type": "auth failure", "reason": "invalid auth token, " + str(e)}
        elif msg_type == "invalid":
            reply = {"type": "error", "reason": "invalid message"}
        elif not user:
            reply = {"type": "error", "reason": "not authenticated"}
        else:
            try:
                handler = request_handlers[msg_type]
            except KeyError:
                handler = None
            
            if handler is not None:
                reply = await handler(context, user, msg, websocket)
            else:
                reply = {"type": "error", "reason": "unknown request", "request": json.dumps(message)}

        # Ensure requests have replies
        if request_id is not None:
            if reply is not None:
                reply['request id'] = request_id
            else:
                reply = {"type": "no reply", "request id": request_id}

        # Send reply
        if reply is not None:
            await websocket.send(json.dumps(reply))


PORT = 3036
CERTCHAIN = "/etc/letsencrypt/live/miravalier.net/fullchain.pem"
CERTKEY = "/etc/letsencrypt/live/miravalier.net/privkey.pem"
OAUTH_PATH = "/etc/auth/oauth.json"

if __name__ == '__main__':
    main(PORT, CERTCHAIN, CERTKEY, OAUTH_PATH)
