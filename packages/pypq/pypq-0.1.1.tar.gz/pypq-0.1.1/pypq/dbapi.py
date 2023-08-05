import time
import datetime

def Date(year,month,day):
    return datetime.date(year, month, day)

def Time(hour,minute,second):
    raise NotImplementedError

def Timestamp(year,month,day,hour,minute,second):
    return datetime.datetime(year, month, day, hour, minute, second)

def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])

def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])

def Binary(str):
    return str

STRING = str
BINARY = STRING
NUMBER = int
DATETIME = datetime.datetime
ROWID = int