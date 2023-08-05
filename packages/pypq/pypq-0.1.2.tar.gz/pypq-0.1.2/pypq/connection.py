import libpq
import ctypes
from constants import *
from cursor import Cursor
import warnings

import errors


class Connection(object):
    
    def __init__(self, *args, **kwargs):
        """There are 2 ways of instantiation:
        1. One argument, which is a connstring
        2. Kwargs needed to build a connstring

        To understand connstring, read PQconnectdbParams section at
        http://www.postgresql.org/docs/9.1/static/libpq-connect.html
        """
        connstr = self.build_connstr(*args, **kwargs)
        self._db = libpq.c.PQconnectdb(connstr)
        self._closed = False
        if self._get_status() != CONNECTION_OK:
            raise errors.DatabaseError(self._get_error_msg())
        self._conn_info = self._get_conn_info()
        self._encoding = self.get_client_encoding()

    @classmethod
    def build_connstr(cls, *args, **kwargs):
        """Build a connection string for postgresql from args and kwargs
        """
        assert args or kwargs, 'You should provide a "connstring" argument,'\
            ' or kwargs to create a connection'
        if args:
            assert not kwargs, 'Cannot provide kwargs and args at the same time'
            assert len(args) == 1, 'The only argument accepted is connstring'
            return args[0]
        return ' '.join('%s=%s' % (k,v) for k,v in kwargs.iteritems())
        
    def _get_status(self):
        if self._closed:
            return
        return libpq.c.PQstatus(self._db)

    def _get_status_string(self):
        if self._closed:
            return 'closed'
        return CONNECTION_STATUSES[self._get_status()]

    def _get_error_msg(self):
        return ctypes.string_at(libpq.c.PQerrorMessage(self._db))

    def _check_closed(self):
        if self._closed:
            raise errors.InterfaceError("Connection already closed")

    def _get_transaction_status(self):
        return libpq.c.PQtransactionStatus(self._db)

    def cursor(self):
        self._check_closed()
        return Cursor(self)

    def __repr__(self):
        info = self._conn_info.copy()
        info['status'] = self._get_status_string()
        return '<Connection db=%(db)s user=%(user)s port=%(port)s: %(status)s>' % info

    def _get_conn_info(self):
        self._check_closed()
        info = {}
        info['server_version'] = self._get_server_version()
        info['db'] = ctypes.string_at(libpq.c.PQdb(self._db))
        info['user'] = ctypes.string_at(libpq.c.PQuser(self._db))
        # This raises a segfault somehow
        # info['host'] = ctypes.string_at(libpq.c.PQhost(self._db))
        info['port'] = ctypes.string_at(libpq.c.PQport(self._db))
        return info

    def _get_server_version(self):
        version = libpq.c.PQserverVersion(self._db)
        # TODO: parse the number according to the spec
        return version

    def get_client_encoding(self):
        return ctypes.string_at(libpq.c.pg_encoding_to_char(libpq.c.PQclientEncoding(self._db)))

    def set_client_encoding(self, enc):
        result = libpq.c.PQsetClientEncoding(self._db, enc)
        if result:
            raise errors.ProgrammingError("Cannot set encoding to '%s'" % enc)
        self._encoding = self.get_client_encoding()

    def set_isolation_level(self, level):
        warnings.warn('Ignoring "set_isolation_level"')

    def commit(self):
        if self._get_transaction_status() in (PQTRANS_INTRANS, PQTRANS_INERROR):
            cursor = self.cursor()
            cursor.execute('COMMIT')

    def rollback(self):
        if self._get_transaction_status() in (PQTRANS_INTRANS, PQTRANS_INERROR):
            cursor = self.cursor()
            cursor.execute('ROLLBACK')

    def close(self):
        self._check_closed()
        libpq.c.PQfinish(self._db)
        self._closed = True