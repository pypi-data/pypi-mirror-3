import libpq
import ctypes

from constants import *

import errors
from pypq import datatypes


class Cursor(object):

    def __init__(self, connection):
        self._connection = connection
        self.arraysize = 1
        self._init()

    @property
    def connection(self):
        return self._connection

    @property
    def rownumber(self):
        return self._rownumber

    @property
    def description(self):
        """
        This read-only attribute is a sequence of 7-item
        sequences.  

        Each of these sequences contains information describing
        one result column:

          (name,
           type_code,
           display_size,
           internal_size,
           precision,
           scale,
           null_ok)
        """
        data = []
        if self._field_names and self._field_types:
            for index, name in enumerate(self._field_names):
                data.append((
                    name, # name
                    self._field_oids[index], # type_code
                    None, # display_size
                    None, # internal_size
                    None, # precision
                    None, # scale
                    None, # null_ok
                ))
        return data

    @property
    def field_names(self):
        """You can use it to make dict-like interfaces"""
        return self._field_names

    @property
    def rowcount(self):
        """
        This read-only attribute specifies the number of rows that
        the last .execute*() produced (for DQL statements like
        'select') or affected (for DML statements like 'update' or
        'insert').

        The attribute is -1 in case no .execute*() has been
        performed on the cursor or the rowcount of the last
        operation is cannot be determined by the interface. [7]

        Note: Future versions of the DB API specification could
        redefine the latter case to have the object return None
        instead of -1.
        """
        return self._rowcount

    def callproc(self, procname, params=()):
        """Call a stored database procedure with the given name.
        """
        return self.execute('select * from %s(%s)' % (
            procname, ', '.join('%s' for i in params)
        ), params)

    def execute(self, query, args=None):
        """
        Prepare and execute a database operation (query or
        command).  Parameters may be provided as sequence or
        mapping and will be bound to variables in the operation.
        Variables are specified in a database-specific notation
        (see the module's paramstyle attribute for details). [5]
        """
        return self._execute(query, args)

    def __iter__(self):
        while True:
            data = self.fetchone()
            if data is None:
                break
            yield data

    def _check_closed(self):
        if self._closed:
            raise errors.ProgrammingError('The cursor is already closed')

    def _execute(self, query, args=None):
        """Execute the query through libpq execution api"""
        self._connection._check_closed()
        self._check_closed()
        self._clear()
        self._init()
        if isinstance(query, unicode):
            query = query.encode(self._connection._encoding)
        if not args:
            self._result = libpq.c.PQexec(self.connection._db, query)
        else:
            # Prepare the arguments for passing to PQexecParams
            # convert them to postgres types according to registered
            # datatypes see datatypes.py for details
            n_args = len(args)
            if query.count('%s') != n_args:
                raise errors.ProgrammingError('Number of arguments and '
                                              'replacements do not match')

            # Replace "%s" arguments with libpq $1,$2 style
            for i in xrange(n_args):
                query = query.replace('%s', '$%s' % (i + 1), 1)

            # Create c types for parameter arrays
            arr_chars_t = ctypes.c_char_p * n_args
            arr_ints_t = ctypes.c_int * n_args

            def process_arg(arg):
                """Convert the python argument for PQexecParams"""
                
                # TODO: fix a bug (there is no such issue in psycopg2)
                # cur.execute('select %s', [None])
                # DatabaseError: ERROR: could not determine data type
                # of parameter $1
                if arg is None:
                    return 0, None, 0, 0
                value, oid = datatypes.to_postgres(arg)
                return oid, value, len(value), 0

            types, values, lengths, formats = zip(*map(process_arg, args))
            self._result = libpq.c.PQexecParams(
                self.connection._db, query,
                n_args, # int nParams,
                # Passing oids only creates problems, so ignore that param
                # arr_ints_t(*types), # const Oid *paramTypes,
                None,
                arr_chars_t(*values), # const char * const *paramValues,
                arr_ints_t(*lengths), # const int *paramLengths,
                arr_ints_t(*formats), # const int *paramFormats,
                0 # int resultFormat
            )

        self._query = query
        
        # The query has been executed, now process the result
        status = libpq.c.PQresultStatus(self._result)
        if status == PGRES_FATAL_ERROR:
            exc = errors.DatabaseError(self._get_error_msg())
            self._clear()
            raise exc
        elif status == PGRES_COMMAND_OK:
            self._cleared = False
            self._rowcount = int(ctypes.string_at(libpq.c.PQcmdTuples(self._result)) or -1)
            self._rownumber = self._rowcount
            self._clear()
        elif status == PGRES_TUPLES_OK:
            self._rowcount = libpq.c.PQntuples(self._result)
            self._rownumber = 0
            self._field_names, self._field_types, self._field_oids = zip(*self._get_fields())
        else:
            # AFAIK, this should not happen
            raise NotImplementedError

    def _get_fields(self):
        """Get a list of (field_name, field_type) tuples from the result"""
        if not self._result:
            raise errors.ProgrammingError('This method should be called'
                                          ' when cursor._result is available')
        nfields = libpq.c.PQnfields(self._result)
        fields = []
        for i in xrange(nfields):
            fname = ctypes.string_at(libpq.c.PQfname(self._result, i))
            foid = libpq.c.PQftype(self._result, i)
            ftype = datatypes.get_type_by_oid(foid)
            fields.append((fname, ftype, foid))
        return tuple(fields)

    def _get_error_msg(self):
        """Get an error message describing why failure occured"""
        if not self._result:
            return
        return ctypes.string_at(libpq.c.PQresultErrorMessage(self._result))

    def executemany(self, query, args):
        for arg_group in args:
            self.execute(query, arg_group)

    def fetchone(self):
        if self._rowcount == -1:
            raise errors.ProgrammingError('Nothing to fetch')
        if self._rowcount == self._rownumber:
            return
        data = []
        for i, type in enumerate(self._field_types):
            value = ctypes.string_at(libpq.c.PQgetvalue(self._result, self._rownumber, i))
            if not value:
                is_null = libpq.c.PQgetisnull(self._result, self._rownumber, i)
                if is_null:
                    data.append(None)
                    continue
            # TODO: add encoding checking here via connection passing as
            # an argument to "to_python"
            value = type.to_python(value)
            data.append(value)
        self._rownumber += 1
        if self._rowcount == self._rownumber:
            self._clear()
        return tuple(data)

    @property
    def query(self):
        """A property to mimic psycopg2's cursor"""
        return self._query

    def _init(self):
        self._cleared = False
        self._result = None
        self._rowcount = -1
        self._rownumber = None
        self._field_names = None
        self._field_types = None
        self._field_oids = None
        self._closed = False
        self._query = None

    def _clear(self):
        """Clear the result of previous execution."""
        if self._result and not self._cleared:
            libpq.c.PQclear(self._result)
            self._cleared = True
            
    def __del__(self):
        self._clear()

    def close(self):
        """DBAPI 2.0 cursor.close()

        Close the cursor now (rather than whenever __del__ is
        called).  The cursor will be unusable from this point
        forward; an Error (or subclass) exception will be raised
        if any operation is attempted with the cursor.
        """
        self._clear()
        self._closed = True

    def fetchall(self):
        data = []
        for row in self:
            data.append(row)
        return data

    def fetchmany(self, size=None):
        size = size or self.arraysize
        result = []
        for i in xrange(size):
            row = self.fetchone()
            if row is None:
                return result
            result.append(row)
        return result
