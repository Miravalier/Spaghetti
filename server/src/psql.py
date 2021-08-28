import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal


TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


def convert_result(result):
    if isinstance(result, str):
        # Check if this is a timestamp
        if TIMESTAMP_PATTERN.fullmatch(result):
            return datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        # Check if this is an int
        try:
            return int(result)
        except:
            pass
    return result


def convert_param(param):
    if isinstance(param, datetime):
        return param.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(param, (int, float, Decimal)):
        return str(param)
    return param


class PSQL:
    def __init__(self, connection_string):
        self.connection = sqlite3.Connection(connection_string)

    def close(self):
        self.connection.close()

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    @contextmanager
    def write_cursor(self):
        cur = self.connection.cursor()
        try:
            yield cur
        finally:
            cur.close()
            self.connection.commit()

    @contextmanager
    def read_cursor(self):
        cur = self.connection.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def execute_and_return(self, sql, params=None, **kwargs):
        if params:
            params = tuple(convert_param(p) for p in params)
        with self.write_cursor() as cur:
            if params:
                cur.execute(sql, params, **kwargs)
            else:
                cur.execute(sql, **kwargs)
            result = [convert_result(r) for r in cur.fetchone()]
            if result and len(result) == 1:
                return result[0]
            else:
                return result

    def execute(self, sql, params=None, **kwargs):
        if params:
            params = tuple(convert_param(p) for p in params)
        with self.write_cursor() as cur:
            if params:
                cur.execute(sql, params, **kwargs)
            else:
                cur.execute(sql, **kwargs)

    def query(self, sql, params=None, **kwargs):
        if params:
            params = tuple(convert_param(p) for p in params)
        with self.read_cursor() as cur:
            if params:
                cur.execute(sql, params, **kwargs)
            else:
                cur.execute(sql, **kwargs)
            return [[convert_result(r) for r in line] for line in cur.fetchall()]

    def single_query(self, sql, params=None, **kwargs):
        if params:
            params = tuple(convert_param(p) for p in params)
        with self.read_cursor() as cur:
            if params:
                cur.execute(sql, params, **kwargs)
            else:
                cur.execute(sql, **kwargs)
            result = [convert_result(r) for r in cur.fetchone()]
            if result and len(result) == 1:
                return result[0]
            else:
                return result
