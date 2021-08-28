#!/usr/bin/env python3.9

import uuid
import sys
import traceback
from flask import Flask
from flask_restful import reqparse, Resource, Api
from datetime import datetime, timedelta
from decimal import Decimal
from google.oauth2 import id_token
from google.auth.transport import requests
from psql import PSQL
from mcollections import LRU

# Configuration
GOOGLE_OAUTH_CLIENT_ID = "308770941548-1mlflanlicqq21sah7odbo8jghacksu2.apps.googleusercontent.com"
STARTING_BALANCE = 50
WEEKLY_INCOME = 25
SAVINGS_APR = 0.015
SAVINGS_DPR = SAVINGS_APR / 365

# Constants
DAYS_PER_WEEK = 7
SECONDS_PER_DAY = 86400
CHECKING = 0
SAVINGS = 1


def last_friday(day):
    friday = day - timedelta(days=day.weekday() - 4)
    if friday > day:
        friday -= timedelta(days=7)
    return friday


def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def elog(e, *args, **kwargs):
    exc_info = sys.exc_info()
    traceback.print_exception(*exc_info)
    log(*args, "{}: {}".format(str(type(e).__name__), str(e)), **kwargs)


def account_parameter(account_id):
    account = Account.lookup(account_id)
    if not account:
        raise ValueError("Invalid account id {}".format(account_id))
    return account


def user_parameter(user_id):
    user = User.lookup(user_id)
    if not user:
        raise ValueError("Invalid user id {}".format(user_id))
    return user


def request_parameter(request_id):
    request = Request.lookup(request_id)
    if not request:
        raise ValueError("Invalid request id {}".format(request_id))
    return request


def authenticate_user(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_OAUTH_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            log("User attempted to authenticate with wrong issuer: {}".format(idinfo['iss']))
            raise ValueError('wrong issuer')

        google_id = idinfo['sub']
        email = idinfo['email']
        return User.create(google_id, email)

    except Exception as e:
        elog(e, "User failed to authenticate")
        abort(403, message="Failed to authenticate.")
        raise


class AuthenticatedParser(reqparse.RequestParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument(
            'idtoken',
            dest='user',
            type=authenticate_user,
            help='Invalid Google OAuth2 idtoken',
            required=True
        )


#############
# RESOURCES #
#############

app = Flask(__name__)
api = Api(app)


class AuthStatus(Resource):
    def put(self):
        parser = AuthenticatedParser()
        args = parser.parse_args()
        return {"status": "authenticated", "user": args["user"].email}


class Status(Resource):
    def put(self):
        return {"status": "online"}

    def get(self):
        return {"status": "online"}


class NetWorth(Resource):
    def put(self):
        parser = AuthenticatedParser()
        args = parser.parse_args()

        account = args["user"].checking
        account.advance_time()
        return {"balance": float(account.balance)}


class ListUsers(Resource):
    def put(self):
        parser = AuthenticatedParser()
        args = parser.parse_args()

        with PSQL("/var/spaghetti/db") as psql:
            return {"users": psql.query("SELECT user_id, user_name FROM users")}


class ListInboundRequests(Resource):
    def put(self):
        parser = AuthenticatedParser()
        args = parser.parse_args()

        user = args["user"]

        return {"requests": user.inbound_requests}


class ListOutboundRequests(Resource):
    def put(self):
        parser = AuthenticatedParser()
        args = parser.parse_args()

        user = args["user"]

        return {"requests": user.outbound_requests}


class DenyRequest(Resource):
    def put(self):
        parser = AuthenticatedParser()
        parser.add_argument('request', type=request_parameter, help='Invalid request id', required=True)
        args = parser.parse_args()

        user = args["user"]
        request = args["request"]
        if request.source.owner != user and request.destination.owner != user:
            return {"error": "You can't deny a transfer that does not involve you."}

        try:
            request.deny()
            return {"success": "Request denied."}
        except Exception as e:
            return {"error": str(e)}


class AcceptRequest(Resource):
    def put(self):
        parser = AuthenticatedParser()
        parser.add_argument('request', type=request_parameter, help='Invalid request id', required=True)
        args = parser.parse_args()

        user = args["user"]
        request = args["request"]
        if request.source.owner != user:
            return {"error": "You can't approve a transfer from someone else's account."}

        try:
            request.accept()
            return {"success": "Request accepted."}
        except Exception as e:
            return {"error": str(e)}


class CreateTransfer(Resource):
    def put(self):
        parser = AuthenticatedParser()
        parser.add_argument('source', type=user_parameter, help='Invalid source user id', required=True)
        parser.add_argument('destination', type=user_parameter, help='Invalid destination user id', required=True)
        parser.add_argument('amount', type=Decimal, help='Invalid amount', required=True)
        args = parser.parse_args()

        user = args["user"]
        source = args["source"].checking
        destination = args["destination"].checking
        amount = args["amount"]

        if source == destination:
            return {"error": "'To' and 'From' must be different."}
        elif source in user.accounts:
            if source.balance > amount:
                source.transfer_to(destination, amount)
                return {"success": "Transfer completed."}
            else:
                return {"error": "Insufficient balance."}
        elif destination in user.accounts:
            Request.create(source, destination, amount)
            return {"success": "Transfer requested."}
        else:
            return {"error": "You can't request a transfer that does not involve you."}


class UpdateUsername(Resource):
    def put(self):
        parser = AuthenticatedParser()
        parser.add_argument('username', type=str, help='Invalid username', required=True)
        args = parser.parse_args

        user = args["user"]
        user.update_username(args["username"])

        return {"success": "Username updated."}


api.add_resource(AuthStatus, '/authstatus')
api.add_resource(Status, '/status')
api.add_resource(NetWorth, '/net-worth')
api.add_resource(ListUsers, '/list-users')
api.add_resource(CreateTransfer, '/transfer/create')
api.add_resource(AcceptRequest, '/transfer/accept')
api.add_resource(DenyRequest, '/transfer/deny')
api.add_resource(ListInboundRequests, '/transfer/list-inbound')
api.add_resource(ListOutboundRequests, '/transfer/list-outbound')
api.add_resource(UpdateUsername, '/update-username')


###########
# CLASSES #
###########

def add_transaction(date, source, destination, amount):
    if source is not None and destination is not None:
        transaction = (date, source.account_id, destination.account_id, amount)
        source.transactions.append(transaction)
        destination.transactions.append(transaction)
    elif source is not None:
        transaction = (date, source.account_id, None, amount)
        source.transactions.append(transaction)
    elif destination is not None:
        transaction = (date, None, destination.account_id, amount)
        destination.transactions.append(transaction)
    else:
        raise ValueError("Source and destination can't both be None")

    with PSQL("/var/spaghetti/db") as psql:
        psql.execute("""
            INSERT INTO transactions (transaction_time, from_id, to_id, amount)
            VALUES (?, ?, ?, ?)
        """, transaction)


class Request:
    cache = LRU(4096)

    def __init__(self, creation_time, from_id, to_id, amount, request_id):
        self.creation_time = creation_time
        self.source = Account.lookup(from_id)
        self.destination = Account.lookup(to_id)
        self.amount = amount
        self.request_id = request_id
        self.deleted = False

    def __str__(self):
        return "Request(id={}, {} -> {}, amount={})".format(
            self.request_id, self.source, self.destination, self.amount
        )

    __repr__ = __str__

    def accept(self):
        # Verify this request is still good
        if self.deleted:
            raise ValueError("Request no longer exists")
        # Verify enough funds are available
        if self.amount > self.source.balance:
            raise ValueError("Not enough funds to cover the transaction")
        # Delete request
        self.deleted = True
        with PSQL("/var/spaghetti/db") as psql:
            psql.execute("DELETE FROM requests WHERE request_id=?", (self.request_id,))
        # Transfer funds
        self.source.transfer_to(self.destination, self.amount)

    def deny(self):
        # Verify this request is still good
        if self.deleted:
            raise ValueError("Request no longer exists")
        # Delete request
        self.deleted = True
        with PSQL("/var/spaghetti/db") as psql:
            psql.execute("DELETE FROM requests WHERE request_id=?", (self.request_id,))

    @classmethod
    def create(cls, source, destination, amount):
        parameters = (datetime.now(), source.account_id, destination.account_id, Decimal(amount))
        # Insert into database and get id
        with PSQL("/var/spaghetti/db") as psql:
            request_id = psql.execute_and_return(
                """
                    INSERT INTO requests (creation_time, from_id, to_id, amount)
                    VALUES (?, ?, ?, ?)
                    RETURNING request_id
                """,
                parameters
            )
        # Create request
        request = cls(*parameters, request_id)
        # Cache and return request
        cls.cache[request_id] = request
        return request

    @classmethod
    def lookup(cls, request_id):
        # Check the cache
        request = cls.cache.get(request_id, None)
        if request is not None:
            return request

        # Query the database
        request_query = """
            SELECT creation_time, from_id, to_id, amount
            FROM requests WHERE request_id=?
        """
        with PSQL("/var/spaghetti/db") as psql:
            response = psql.single_query(request_query, (request_id,))
        if not response:
            return None

        # Update cache and return request
        creation_time, from_id, to_id, amount = response
        request = cls(creation_time, from_id, to_id, amount, request_id)
        cls.cache[request_id] = request
        return request


class Account:
    cache = LRU(4096)

    def __init__(self, user_id, account_id, account_uuid, account_type, name, balance, update_time):
        self.user_id = user_id
        self.account_id = account_id
        self.uuid = account_uuid
        self.type = account_type
        self.name = name
        self.balance = balance
        self.update_time = update_time
        with PSQL("/var/spaghetti/db") as psql:
            self.transactions = psql.query("""
                SELECT transaction_time, from_id, to_id, amount
                FROM transactions WHERE from_id=? OR to_id=?
            """, (account_id, account_id))

    def __str__(self):
        return "Account(id={}, balance={})".format(self.account_id, self.balance)
    
    __repr__ = __str__

    @property
    def owner(self):
        return User.lookup(self.user_id)

    @property
    def inbound_requests(self):
        with PSQL("/var/spaghetti/db") as psql:
            request_values = psql.query(
                "SELECT from_id, to_id, amount, request_id FROM requests WHERE from_id=?",
                (self.account_id,)
            )
        requests = []
        for from_id, to_id, amount, request_id in request_values:
            requests.append((
                Account.lookup(from_id).owner.username,
                Account.lookup(to_id).owner.username,
                float(amount),
                request_id
            ))
        return requests

    @property
    def outbound_requests(self):
        with PSQL("/var/spaghetti/db") as psql:
            request_values = psql.query(
                "SELECT from_id, to_id, amount, request_id FROM requests WHERE to_id=?",
                (self.account_id,)
            )
        requests = []
        for from_id, to_id, amount, request_id in request_values:
            requests.append((
                Account.lookup(from_id).owner.username,
                Account.lookup(to_id).owner.username,
                float(amount),
                request_id
            ))
        return requests

    def grant_funds(self, amount, date=None):
        if date is None:
            date = datetime.now()
        add_transaction(date, None, self, amount)
        self.add_balance(amount)

    def transfer_to(self, destination, amount, date=None):
        if date is None:
            date = datetime.now()
        add_transaction(date, self, destination, amount)
        destination.add_balance(amount)
        self.subtract_balance(amount)

    def transfer_from(self, source, amount, date=None):
        if date is None:
            date = datetime.now()
        add_transaction(date, source, self, amount)
        source.subtract_balance(amount)
        self.add_balance(amount)

    def add_balance(self, amount):
        self.update_balance(self.balance + Decimal(amount))

    def subtract_balance(self, amount):
        self.update_balance(self.balance - Decimal(amount))

    def update_balance(self, amount):
        self.balance = Decimal(amount)
        with PSQL("/var/spaghetti/db") as psql:
            psql.execute("""
                UPDATE accounts SET account_balance=? WHERE account_id=?
            """, (amount, self.account_id))

    def advance_time(self):
        seconds_advanced = (datetime.now() - self.update_time).total_seconds()
        days_advanced = seconds_advanced // SECONDS_PER_DAY
        weeks_advanced = days_advanced // DAYS_PER_WEEK

        if self.type == CHECKING:
            if weeks_advanced <= 0:
                return
            self.add_balance(WEEKLY_INCOME * weeks_advanced)
            self.update_time += timedelta(days=weeks_advanced * DAYS_PER_WEEK)

        elif self.type == SAVINGS:
            if days_advanced <= 0:
                return
            interest_rate = SAVINGS_DPR ** days_advanced
            self.add_balance(self.balance * interest_rate)
            self.update_time += timedelta(days=days_advanced)

        with PSQL("/var/spaghetti/db") as psql:
            psql.execute("""
                UPDATE accounts SET update_time=? WHERE account_id=?
            """, (self.update_time, self.account_id))

    @classmethod
    def lookup(cls, account_id):
        # Check the cache
        account = cls.cache.get(account_id, None)
        if account is not None:
            account.advance_time()
            return account

        # Query the database
        with PSQL("/var/spaghetti/db") as psql:
            response = psql.single_query("""
                SELECT user_id, account_type, account_name, account_uuid, account_balance, update_time
                FROM accounts WHERE account_id=?
            """, (account_id,))
        if not response:
            return None
        user_id, account_type, name, account_uuid, balance, update_time = response

        # Update the cache and return the account
        account = cls(user_id, account_id, account_uuid, account_type, name, balance, update_time)
        cls.cache[account_id] = account
        account.advance_time()
        return account


class User:
    cache = LRU(1024)

    def __init__(self, username, user_id, google_id, email):
        self.username = username
        self.user_id = user_id
        self.google_id = google_id
        self.email = email

        with PSQL("/var/spaghetti/db") as psql:
            account_ids = psql.query("""
                SELECT account_id, account_name
                FROM accounts WHERE user_id=?
            """, (self.user_id,))

        self.accounts = set()
        for account_id, name in account_ids:
            self.accounts.add(Account.lookup(account_id))

    def __str__(self):
        return "User(id={}, name={})".format(self.user_id, self.username[:8])

    __repr__ = __str__

    def __eq__(self, other):
        return self.user_id == other.user_id

    def update_username(username):
        self.username = username
        with PSQL("/var/spaghetti/db") as psql:
            psql.execute("UPDATE users SET user_name=? WHERE user_id=?", (username, self.user_id))

    @property
    def inbound_requests(self):
        requests = []
        for account in self.accounts:
            requests.extend(account.inbound_requests)
        return requests

    @property
    def outbound_requests(self):
        requests = []
        for account in self.accounts:
            requests.extend(account.outbound_requests)
        return requests

    @property
    def checking(self):
        for account in self.accounts:
            if account.type == CHECKING:
                return account
        return None

    def create_account(self, name="Checking", type=CHECKING, balance=STARTING_BALANCE):
        account_uuid = str(uuid.uuid4())
        with PSQL("/var/spaghetti/db") as psql:
            account_id = psql.execute_and_return(
                """
                    INSERT INTO accounts (
                        account_uuid, account_name, account_type,
                        account_balance, user_id, update_time
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    RETURNING account_id
                """,
                (
                    account_uuid, name, type, balance, self.user_id,
                    last_friday(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
                )
            )
        account = Account.lookup(account_id)
        self.accounts.add(account)
        return account

    @classmethod
    def lookup(cls, id):
        # Check the cache
        user = cls.cache.get(id, None)
        if user is not None:
            return user

        # Build the query
        lookup_query = "SELECT user_name, user_id, google_id, email FROM users WHERE "
        if type(id) is int:
            lookup_query += "user_id=?"
        elif type(id) is str:
            lookup_query += "google_id=?"
        else:
            raise TypeError("Invalid user id lookup type '{}'".format(type(id)))

        # Query the database
        with PSQL("/var/spaghetti/db") as psql:
            response = psql.single_query(lookup_query, (id,))
        if not response:
            return None
        username, user_id, google_id, email = response

        # Store the user in the cache and return
        user = cls(username, user_id, google_id, email)
        cls.cache[user_id] = user
        cls.cache[google_id] = user
        return user

    @classmethod
    def create(cls, google_id, email, username=None):
        if username is None:
            username = email.replace('@gmail.com', '')

        # Make sure this user doesn't exist
        user = cls.lookup(google_id)
        if user:
            return user

        # Insert a new user
        with PSQL("/var/spaghetti/db") as psql:
            user_id = psql.execute_and_return("""
                INSERT INTO users (google_id, email, user_name)
                VALUES (?, ?, ?)
                RETURNING user_id
            """, (google_id, email, username))
        user = cls(username, user_id, google_id, email)
        user.create_account(balance=STARTING_BALANCE)

        # Update the cache
        cls.cache[user_id] = user
        cls.cache[google_id] = user
        return user


if __name__ == '__main__':
    #import waitress
    #waitress.serve(app, host='0.0.0.0', port=80)
    app.run(host="0.0.0.0", port=80, debug=True)
