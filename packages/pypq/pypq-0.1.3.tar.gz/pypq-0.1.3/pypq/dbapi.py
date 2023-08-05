import time
import datetime

def Date(year,month,day):
    return datetime.date(year, month, day)

def Time(hour,minute,second):
    return datetime.time(hour, minute, second)

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

import datatypes

STRING = datatypes.Unicode
BINARY = datatypes.String
NUMBER = datatypes.Integer
DATETIME = datatypes.DateTime
ROWID = datatypes.ROWID