import threading
import psycopg2
from contextlib import contextmanager
from collections import deque

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
        self.worker = threading.Thread(target=sql_write_worker, args=(self,), daemon=True)
        self.worker.start()

    def close(self):
        self.running = False
        self.read_connection.close()
        self.write_connection.close()
        self.worker.join()

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    @contextmanager
    def read_write_cursor(self):
        cur = self.read_connection.cursor()
        try:
            yield cur
        finally:
            cur.close()
            self.read_connection.commit()

    @contextmanager
    def write_cursor(self):
        cur = self.write_connection.cursor()
        try:
            yield cur
        finally:
            cur.close()
            self.write_connection.commit()

    @contextmanager
    def read_cursor(self):
        cur = self.read_connection.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def execute_and_return(self, *args, **kwargs):
        with self.read_write_cursor() as cur:
            cur.execute(*args, **kwargs)
            result = cur.fetchone()
            if result and len(result) == 1:
                return result[0]
            else:
                return result

    def execute(self, *args, **kwargs):
        with self.write_lock:
            self.pending_writes.append((args, kwargs))
        self.write_semaphore.release()

    def query(self, *args, **kwargs):
        with self.read_cursor() as cur:
            cur.execute(*args, **kwargs)
            return cur.fetchall()

    def single_query(self, *args, **kwargs):
        with self.read_cursor() as cur:
            cur.execute(*args, **kwargs)
            result = cur.fetchone()
            if result and len(result) == 1:
                return result[0]
            else:
                return result


def sql_write_worker(psql):
    while psql.running:
        psql.write_semaphore.acquire(timeout=1)

        args = None
        with psql.write_lock:
            if psql.pending_writes:
                args, kwargs = psql.pending_writes.popleft()

        if args:
            with psql.write_cursor() as cur:
                cur.execute(*args, **kwargs)
