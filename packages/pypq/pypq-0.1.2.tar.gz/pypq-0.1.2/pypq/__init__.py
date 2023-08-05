apilevel = '2.0'
threadsafety = 0
paramstyle = 'format'

from connection import *
from cursor import *
from constants import *
from errors import *

def connect(*args, **kwargs):
    return Connection(*args, **kwargs)