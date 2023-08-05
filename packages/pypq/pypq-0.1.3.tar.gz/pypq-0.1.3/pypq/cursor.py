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
                    self._field_types[index], # type_code
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
        self.execute('select * from %s(%s)' % (
            procname, ', '.join('%s' for i in params)
        ), params)
        return params

    def execute(self, query, args=()):
        """
        Prepare and execute a database operation (query or
        command).  Parameters may be provided as sequence or
        mapping and will be bound to variables in the operation.
        Variables are specified in a database-specific notation
        (see the module's paramstyle attribute for details). [5]
        """
        self._connection._check_closed()
        self._check_closed()
        self._clear()
        self._init()
        self._check_transaction()
        query, replacements = self._process_query(query)
        return self._execute(query, replacements, args)

    def _check_transaction(self):
        if self._connection._get_transaction_status() == PQTRANS_IDLE:
            self._execute('BEGIN')

    def executemany(self, query, args=()):
        self._connection._check_closed()
        self._check_closed()
        self._clear()
        self._init()
        self._check_transaction()
        query, replacements = self._process_query(query)
        
        rowcount = 0
        
        for arg_group in args:
            self._execute(query, replacements, arg_group)
            # Sum the rowcounts if every one of them is countable
            if rowcount >= 0:
                rowcount += self.rowcount
        self._rowcount = rowcount

    def __iter__(self):
        while True:
            data = self.fetchone()
            if data is None:
                break
            yield data

    def _check_closed(self):
        if self._closed:
            raise errors.ProgrammingError('The cursor is already closed')

    def _process_query(self, query):
        """Replace "%s" arguments with libpq $1,$2 style"""

        if isinstance(query, unicode):
            query = query.encode(self._connection._encoding)

        query = query.replace('%%', '%\0%')
        replacements = 0
        for i in xrange(query.count('%s')):
            query = query.replace('%s', '$%s' % (replacements + 1), 1)
            replacements += 1
        query = query.replace('%\0%', '%%')
        return query, replacements

    def _execute(self, query, replacements=0, args=()):
        """Execute the query through libpq execution api"""
        if not args:
            # We can use the simple "PQexec" function if we do not have
            # any arguments
            self._result = libpq.PQexec(self.connection._db, query)
        else:
            n_args = len(args)

            # Prepare the arguments for passing to PQexecParams
            # convert them to postgres types according to registered
            # datatypes, see datatypes.py for details

            if replacements != len(args):
                raise errors.ProgrammingError('Number of arguments and '
                                              'replacements do not match')

            # Create c types for parameter arrays
            arr_chars_t = ctypes.c_char_p * n_args
            arr_ints_t = ctypes.c_int * n_args
            arr_uints_t = ctypes.c_uint * n_args

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
            self._result = libpq.PQexecParams(
                self.connection._db, query,
                n_args, # int nParams,
                # Passing oids only creates problems, so ignore that param
                # arr_uints_t(*types), # const Oid *paramTypes,
                None,
                arr_chars_t(*values), # const char * const *paramValues,
                arr_ints_t(*lengths), # const int *paramLengths,
                arr_ints_t(*formats), # const int *paramFormats,
                0 # int resultFormat
            )

        self._query = query
        self._process_result()
        
    def _process_result(self):
        # The query has been executed, now process the result
        self._status = libpq.PQresultStatus(self._result)
        if self._status == PGRES_FATAL_ERROR:
            exc = errors.DatabaseError(self._get_error_msg())
            self._clear()
            raise exc
        elif self._status == PGRES_COMMAND_OK:
            self._rowcount = int(libpq.PQcmdTuples(self._result) or -1)
            self._clear()
        elif self._status == PGRES_TUPLES_OK:
            self._rowcount = libpq.PQntuples(self._result)
            self._rownumber = 0
            self._field_names, self._field_types, self._field_oids = zip(*self._get_fields())
        else:
            raise errors.Error('Unexpected pgresultstatus %s' % self._status)

    def setinputsizes(self, sizes):
        """DBAPI 2.0 setinputsizes

        Implementations are free to have this method do nothing
        and users are free to not use it.
        """
        pass

    def setoutputsize(self, size, column=None):
        """DBAPI 2.0 setoutputsize

        Implementations are free to have this method do nothing
        and users are free to not use it.
        """
        pass

    def _get_fields(self):
        """Get a list of (field_name, field_type) tuples from the result"""
        if not self._result:
            raise errors.ProgrammingError('This method should be called'
                                          ' when cursor._result is available')
        nfields = libpq.PQnfields(self._result)
        fields = []
        for i in xrange(nfields):
            fname = libpq.PQfname(self._result, i)
            foid = libpq.PQftype(self._result, i)
            ftype = datatypes.get_type_by_oid(foid)
            fields.append((fname, ftype, foid))
        return tuple(fields)

    def _get_error_msg(self):
        """Get an error message describing why failure occured"""
        if not self._result:
            return
        return libpq.PQresultErrorMessage(self._result)

    def fetchone(self):
        if self._rowcount == -1 or self._status == PGRES_COMMAND_OK:
            raise errors.ProgrammingError('Nothing to fetch')
        if self._rowcount == self._rownumber:
            return
        data = []
        for i, type in enumerate(self._field_types):
            value = libpq.PQgetvalue(self._result, self._rownumber, i)
            if not value:
                is_null = libpq.PQgetisnull(self._result, self._rownumber, i)
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
        self._status = None

    def _clear(self):
        """Clear the result of previous execution."""
        if self._result and not self._cleared:
            libpq.PQclear(self._result)
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
