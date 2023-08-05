'''Simple connection pool for asynchronous code.
'''
from collections import deque

class ConnectionPool(object):
    '''A connection pool that holds `pool_size` connected instances,
    calls init_callable() when it needs more, and passes
    to close_callable() connections that will not fit on the pool.
    '''
    
    def __init__(self, init_callable, close_callable, pool_size=5):
        self.init_callable = init_callable
        self.close_callable = close_callable
        self.pool_size = pool_size
        self.connections = deque()

    def get(self):
        if not self.connections:
            self.connections.append(self.init_callable())
        conn = self.connections.pop()
        if not conn.is_closed:
            return conn
        else:
            return self.get()

    def release(self, conn, error=False):
        if not conn.is_closed:
            if not error and len(self.connections) < self.pool_size:
                self.connections.append(conn)
            else:
                self.close_callable(conn)

    @property
    def connection(self):
        return ConnContextWrapper(self, self.get())

class ConnContextWrapper(object):
    '''Context wrapper for try/finally behavior using the
    "with" statement.

    Ensures that connections return to the pool when the
    code block that requires them has ended.
    '''
    def __init__(self, pool, conn):
        self.pool = pool
        self.conn = conn

    def __enter__(self):
        return self.conn

    def __exit__(self, type, value, tb):
        error = type is not None
        self.pool.release(self.conn, error)
