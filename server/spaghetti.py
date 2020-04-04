#!/usr/bin/env python3.7

import uuid
import sys
from flask import Flask
from flask_restful import reqparse, Resource, Api
from datetime import datetime
from decimal import Decimal
from google.oauth2 import id_token
from google.auth.transport import requests
from psql import PSQL
from mcollections import LRU


# Configuration
GOOGLE_OAUTH_CLIENT_ID = "308770941548-1mlflanlicqq21sah7odbo8jghacksu2.apps.googleusercontent.com"
STARTING_BALANCE = 15
DAILY_INCOME = 10
SAVINGS_APR = 0.015

# Constants
MINUTES_PER_DAY = 1440
MINUTES_PER_YEAR = 525600 # HOW DO YOU MEASURE A YEAR IN THE LIFE
CHECKING = 0
SAVINGS = 1


def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def authenticate_user(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_OAUTH_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('wrong issuer')

        google_id = idinfo['sub']
        email = idinfo['email']
        user = User.lookup(google_id, email)
        if not user.accounts:
            user.create_account(balance=STARTING_BALANCE)
        return user
    except:
        abort(403, message="Failed to authenticate.")
        raise


class AuthenticatedParser(reqparse.RequestParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('idtoken', dest='user', type=authenticate_user, help='Invalid Google OAuth2 idtoken', required=True)


#############
# RESOURCES #
#############

app = Flask(__name__)
api = Api(app)


class AuthStatus(Resource):
    def put(self):
        parser = AuthenticatedParser()
        args = parser.parse_args()
        return {"status": "authenticated"}


class Status(Resource):
    def get(self):
        return {"status": "online"}


class Balance(Resource):
    def put(self):
        parser = AuthenticatedParser()
        parser.add_argument('account', dest='account', type=account_parameter, help='Invalid account id', required=True)
        args = parser.parse_args()
        account = args["account"]
        return {"balance": float(account.balance)}


api.add_resource(AuthStatus, '/authstatus')
api.add_resource(Status, '/status')
api.add_resource(Balance, '/balance')


###########
# CLASSES #
###########

psql = PSQL("dbname=spaghetti")


def add_transaction(date, source, destination, amount):
    transaction = (date, source.account_id, destination.account_id, amount)
    source.transactions.append(transaction)
    destination.transactions.append(transaction)
    psql.execute("""
        INSERT INTO transactions (transaction_time, from_id, to_id, amount)
        VALUES (%s, %s, %s, %s)
    """, transaction)


def account_parameter(account_id):
    return Account.lookup(account_id)


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
        self.update_balance(self.balance + amount)

    def subtract_balance(self, amount):
        self.update_balance(self.balance - amount)

    def update_balance(self, amount):
        self.balance = amount
        psql.execute("""
            UPDATE accounts SET account_balance=%s WHERE account_id=%s
        """, (amount, self.account_id))

    def advance_time(self):
        seconds_advanced = (datetime.now() - self.update_time).total_seconds()
        if seconds_advanced < 60:
            return
        minutes_advanced = round(seconds_advanced / 60)

        if self.type == CHECKING:
            self.add_balance(DAILY_INCOME * minutes_advanced / MINUTES_PER_DAY)
        elif self.type == SAVINGS:
            mpr = SAVINGS_APR / MINUTES_PER_YEAR
            interest_rate = mpr ** minutes_advanced
            self.add_balance(self.balance * interest_rate)

        self.update_time = datetime.now()
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
        """, (account_uuid, name, type, balance, self.user_id, datetime.now()))
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3033, debug=True)
