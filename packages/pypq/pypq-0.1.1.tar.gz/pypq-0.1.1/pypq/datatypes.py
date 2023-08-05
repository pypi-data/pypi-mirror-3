import datetime
import abc
import ctypes
import collections

try:
    import pytz
except ImportError:
    pytz = None

import errors

TYPE_MAP = {}
OID_MAP = {}


class AutoRegisteringPQType(abc.ABCMeta):

    def __new__(mcs, name, bases, dict):
        cls = super(AutoRegisteringPQType, mcs).__new__(mcs, name, bases, dict)
        if cls.auto_register:
            for c in cls.python_types:
                register_adapter(c, cls.to_postgres)
            register_type(cls)
        return cls


def register_adapter(cls, adapter):
    TYPE_MAP[cls] = adapter

def new_type(oids, name, adapter):
    return type(name, (_PyPQDataType,), {'to_python': adapter, 'oids': oids})

def register_type(cls):
    for oid in cls.oids:
        OID_MAP[oid] = cls


class _PyPQDataType(object):
    oids = ()
    python_types = ()

    @classmethod
    def to_python(cls, value):
        return value

    @classmethod
    def to_postgres(cls, value):
        if cls.oids:
            oid = cls.oids[0]
        else:
            oid = 0
        return str(value), oid


class PyPQDataType(_PyPQDataType):

    __metaclass__ = AutoRegisteringPQType

    auto_register = True


class Integer(PyPQDataType):

    oids = (23, 20)

    python_types = (int, )

    @classmethod
    def to_python(cls, value):
        return int(value)


class Float(PyPQDataType):

    oids = (700, 701)

    python_types = (float, )

    @classmethod
    def to_python(cls, value):
        return float(value)


class String(PyPQDataType):

    oids = (25, 1043)

    python_types = (str, )

    
class Unicode(String):

    python_types = (unicode, )

    @classmethod
    def to_postgres(cls, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return value, 25

class AutoUnicode(Unicode):

    auto_register = False

    @classmethod
    def to_python(cls, value):
        return value.decode('utf-8')

class Date(PyPQDataType):

    oids = (1082,)

    python_types = (datetime.date, )

    @classmethod
    def to_python(cls, value):
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()


class DateTime(PyPQDataType):

    oids = (1114, )

    python_types = (datetime.date, )

    @classmethod
    def to_python(cls, value):
        format = '%Y-%m-%d %H:%M:%S'
        if '.' in value:
            format += '.%f'
        return datetime.datetime.strptime(value, format)


class DateTimeTz(PyPQDataType):

    oids = (1184,)

    @classmethod
    def to_python(cls, value):
        # TODO: Implement timezone handling
        value = value.split('+')[0]
        return DateTime.to_python(value)


class PgInterval(datetime.timedelta):

    def __init__(self, *args, **kwargs):
        super(PgInterval, self).__init__(*args, **kwargs)
        self.original_interval = None
        

# Converting into python Timedelta destroys some information
# so we use PgInterval instead, which saves the original info
class Interval(PyPQDataType):

    oids = (1186,)

    python_types = (datetime.timedelta, PgInterval)

    @classmethod
    def to_postgres(cls, value):
        if isinstance(value, PgInterval):
            return value.original_interval, 1186
        return '%s days %s seconds %s microseconds' % \
               (value.days, value.seconds, value.microseconds), 1186

    @classmethod
    def to_python(cls, value):
        years = 0
        months = 0
        days = 0
        ms = 0
        h = 0
        m = 0
        s = 0

        original_value = value

        # example value: '10 years 10 mons 15 days 10:10:10'
        if 'year' in value:
            years, value = value.split(' year')
            years = int(years)
            try:
                value = value.split(' ', 1)[1]
            except IndexError:
                value = ''

        if 'mon' in value:
            months, value = value.split(' mon')
            months = int(months)
            try:
                value = value.split(' ', 1)[1]
            except IndexError:
                value = ''

        if 'day' in value:
            days, value = value.split(' day')
            days = int(days)
            try:
                value = value.split(' ', 1)[1]
            except IndexError:
                value = ''

        if '.' in value:
            value, ms = value.split('.')
            ms = int(ms)

        if ':' in value:
        # For now, the value should be "H:M:S"
            h,m,s = map(int, value.split(':'))

        interval = PgInterval(365 * years + 31 * months + days, hours=h,
                          seconds=s, microseconds=ms)
        interval.original_interval = original_value
        return interval

    
class Boolean(PyPQDataType):

    python_types = (bool, ) 

    oids = (16,)

    @classmethod
    def to_python(cls, value):
        value = value.lower()
        if value == 't':
            return True
        elif value == 'f':
            return False
        raise errors.Error('Cannot convert "%s" to bool' % value)

    
def to_postgres(value):
    try:
        adapter = TYPE_MAP[type(value)]
    except KeyError:
        raise errors.NotSupportedError('Cannot cast %s to postgres type' % type(value))
    return adapter(value)

adapt = to_postgres


def to_python(value, oid=None):
    cls = get_type_by_oid(oid)
    return cls.to_python(value)


def get_type_by_oid(oid, default=String):
    return OID_MAP.get(oid, default)