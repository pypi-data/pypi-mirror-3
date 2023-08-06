def integer(value):
    return int(value)

def float(value):
    return __builtins__['float'](value)

def line(value):
    return str(value)

from cStringIO import StringIO

def text(value):
    value = value.replace('\r\n', '\n')
    value = value.replace('\r', '\n')
    return value

def boolean(value):
    return int(value)
         
from DateTime.DateTime import DateTime, DateTimeError

def date(value):
    return DateTime(value)

def email(value):
    return str(value).strip()