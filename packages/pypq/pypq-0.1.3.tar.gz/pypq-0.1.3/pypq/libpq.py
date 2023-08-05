"""ctypes interface to the libpq library"""

# CODE TAKEN FROM psycopg2ct
# https://raw.github.com/mvantellingen/psycopg2-ctypes/develop/psycopg2ct/libpq.py


from ctypes import *
from ctypes.util import find_library

PG_LIBRARY = find_library('pq')
if not PG_LIBRARY:
    raise OSError('Cannot find libpq in the system')


libpq = cdll.LoadLibrary(PG_LIBRARY)
c = libpq


c_char_p_p = POINTER(c_char_p)
c_int_p = POINTER(c_int)
c_uint_p = POINTER(c_uint)

class PGconn(Structure):
    _fields_ = []

PGconn_p = POINTER(PGconn)


class PGresult(Structure):
    _fields_ = []

PGresult_p = POINTER(PGresult)

class PGcancel(Structure):
    _fields_ = []

PGcancel_p = POINTER(PGcancel)


CONNECTION_OK = 0
CONNECTION_BAD = 1

ConnStatusType = c_int

PGRES_EMPTY_QUERY = 0
PGRES_COMMAND_OK = 1
PGRES_TUPLES_OK = 2
PGRES_COPY_OUT = 3
PGRES_COPY_IN = 4
PGRES_BAD_RESPONSE = 5
PGRES_NONFATAL_ERROR = 6
PGRES_FATAL_ERROR = 7

ExecStatusType = c_int

PG_DIAG_SEVERITY = ord('S')
PG_DIAG_SQLSTATE = ord('C')
PG_DIAG_MESSAGE_PRIMARY = ord('M')
PG_DIAG_MESSAGE_DETAIL = ord('D')
PG_DIAG_MESSAGE_HINT = ord('H')
PG_DIAG_STATEMENT_POSITION = 'P'
PG_DIAG_INTERNAL_POSITION = 'p'
PG_DIAG_INTERNAL_QUERY = ord('q')
PG_DIAG_CONTEXT = ord('W')
PG_DIAG_SOURCE_FILE = ord('F')
DIAG_SOURCE_LINE = ord('L')
PG_DIAG_SOURCE_FUNCTION = ord('R')


class PGnotify(Structure):
    pass


# Database connection control functions

PQconnectdb = libpq.PQconnectdb
PQconnectdb.argtypes = [c_char_p]
PQconnectdb.restype = PGconn_p

PQfinish = libpq.PQfinish
PQfinish.argtypes = [PGconn_p]
PQfinish.restype = None

# Connection status functions

PQdb = libpq.PQdb
PQdb.argtypes = [PGconn_p]
PQdb.restype = c_char_p

PQuser = libpq.PQuser
PQuser.argtypes = [PGconn_p]
PQuser.restype = c_char_p

PQport = libpq.PQport
PQport.argtypes = [PGconn_p]
PQport.restype = c_char_p

PQhost = libpq.PQhost
PQhost.argtypes = [PGconn_p]
PQhost.restype = c_char_p

PQstatus = libpq.PQstatus
PQstatus.argtypes = [PGconn_p]
PQstatus.restype = ConnStatusType

PQtransactionStatus = libpq.PQtransactionStatus
PQtransactionStatus.argtypes = [PGconn_p]
PQtransactionStatus.restype = c_int

PQparameterStatus = libpq.PQparameterStatus
PQparameterStatus.argtypes = [PGconn_p, c_char_p]
PQparameterStatus.restype = c_char_p

PQprotocolVersion = libpq.PQprotocolVersion
PQprotocolVersion.argtypes = [PGconn_p]
PQprotocolVersion.restype = c_int

PQserverVersion = libpq.PQserverVersion
PQserverVersion.argtypes = [PGconn_p]
PQserverVersion.restype = c_int

PQerrorMessage = libpq.PQerrorMessage
PQerrorMessage.argtypes = [PGconn_p]
PQerrorMessage.restype = c_char_p

PQbackendPID = libpq.PQbackendPID
PQbackendPID.argtypes = [PGconn_p]
PQbackendPID.restype = c_int

# Command execution functions

PQexec = libpq.PQexec
PQexec.argtypes = [PGconn_p, c_char_p]
PQexec.restype = PGresult_p

PQexecParams = libpq.PQexecParams
PQexecParams.argtypes = [PGconn_p, c_char_p, c_int, c_uint_p, c_char_p_p,
    c_int_p, c_int_p, c_int]
PQexecParams.restype = PGresult_p

PQclientEncoding = libpq.PQclientEncoding
PQclientEncoding.argtypes = [PGconn_p]
PQclientEncoding.restype = c_int

PQsetClientEncoding = libpq.PQsetClientEncoding
PQsetClientEncoding.argtypes = [PGconn_p, c_char_p]
PQsetClientEncoding.restype = c_int

pg_encoding_to_char = libpq.pg_encoding_to_char
pg_encoding_to_char.argtypes = [c_int]
pg_encoding_to_char.restype = c_char_p

PQresultStatus = libpq.PQresultStatus
PQresultStatus.argtypes = [PGresult_p]
PQresultStatus.restype = ExecStatusType

PQresultErrorMessage = libpq.PQresultErrorMessage
PQresultErrorMessage.argtypes = [PGresult_p]
PQresultErrorMessage.restype = c_char_p

PQresultErrorField = libpq.PQresultErrorField
PQresultErrorField.argtypes = [PGresult_p, c_int]
PQresultErrorField.restype = c_char_p

PQclear = libpq.PQclear
PQclear.argtypes = [POINTER(PGresult)]
PQclear.restype = None

# Retrieving query result information

PQntuples = libpq.PQntuples
PQntuples.argtypes = [PGresult_p]
PQntuples.restype = c_int

PQnfields = libpq.PQnfields
PQnfields.argtypes = [PGresult_p]
PQnfields.restype = c_int

PQfname = libpq.PQfname
PQfname.argtypes = [PGresult_p, c_int]
PQfname.restype = c_char_p

PQftype = libpq.PQftype
PQftype.argtypes = [PGresult_p, c_int]
PQftype.restype = c_uint

PQgetisnull = libpq.PQgetisnull
PQgetisnull.argtypes = [PGresult_p, c_int, c_int]
PQgetisnull.restype = c_int

PQgetlength = libpq.PQgetlength
PQgetlength.argtypes = [PGresult_p, c_int, c_int]
PQgetlength.restype = c_int

PQgetvalue = libpq.PQgetvalue
PQgetvalue.argtypes = [PGresult_p, c_int, c_int]
PQgetvalue.restype = c_char_p

# Retrieving other result information

PQcmdStatus = libpq.PQcmdStatus
PQcmdStatus.argtypes = [PGresult_p]
PQcmdStatus.restype = c_char_p

PQcmdTuples = libpq.PQcmdTuples
PQcmdTuples.argtypes = [PGresult_p]
PQcmdTuples.restype = c_char_p

PQoidValue = libpq.PQoidValue
PQoidValue.argtypes = [PGresult_p]
PQoidValue.restype = c_uint

# Escaping string for inclusion in sql commands

#if PG_VERSION >= 0x090000:
#    PQescapeLiteral = libpq.PQescapeLiteral
#    PQescapeLiteral.argtypes = [PGconn_p, c_char_p, c_uint]
#    PQescapeLiteral.restype = POINTER(c_char)

PQescapeStringConn = libpq.PQescapeStringConn
PQescapeStringConn.restype = c_uint
PQescapeStringConn.argtypes = [PGconn_p, c_char_p, c_char_p, c_uint, POINTER(c_int)]

PQescapeString = libpq.PQescapeString
PQescapeString.argtypes = [c_char_p, c_char_p, c_uint]
PQescapeString.restype = c_uint

PQescapeByteaConn = libpq.PQescapeByteaConn
PQescapeByteaConn.argtypes = [PGconn_p, c_char_p, c_uint, POINTER(c_uint)]
PQescapeByteaConn.restype = POINTER(c_char)

PQescapeBytea = libpq.PQescapeBytea
PQescapeBytea.argtypes = [c_char_p, c_uint, POINTER(c_uint)]
PQescapeBytea.restype = POINTER(c_char)

PQunescapeBytea = libpq.PQunescapeBytea
PQunescapeBytea.argtypes = [POINTER(c_char), POINTER(c_uint)]
PQunescapeBytea.restype = POINTER(c_char)

# Cancelling queries in progress

PQgetCancel = libpq.PQgetCancel
PQgetCancel.argtypes = [PGconn_p]
PQgetCancel.restype = PGcancel_p

PQfreeCancel = libpq.PQfreeCancel
PQfreeCancel.argtypes = [PGcancel_p]
PQfreeCancel.restype = None

PQcancel = libpq.PQcancel
PQcancel.argtypes = [PGcancel_p, c_char_p, c_int]
PQcancel.restype = c_int

PQrequestCancel = libpq.PQrequestCancel
PQrequestCancel.argtypes = [PGconn_p]
PQrequestCancel.restype = c_int

# Miscellaneous functions

PQfreemem = libpq.PQfreemem
PQfreemem.argtypes = [c_void_p]
PQfreemem.restype = None

# Notice processing

PQnoticeProcessor = CFUNCTYPE(None, c_void_p, c_char_p)

PQsetNoticeProcessor = libpq.PQsetNoticeProcessor
PQsetNoticeProcessor.argtypes = [PGconn_p, PQnoticeProcessor, c_void_p]
PQsetNoticeProcessor.restype = PQnoticeProcessor