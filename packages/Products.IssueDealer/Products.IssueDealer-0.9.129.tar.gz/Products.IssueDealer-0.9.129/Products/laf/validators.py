def integer(value):
    try:
        int(value)
    except ValueError:
        return 0, 'Not a valid integral value'
    if int(value) != int(value):
        return 0, 'Not a valid integral value (examples are 0, 5, 13, 100001 and so on'
    else:
        return 1, ''

def float(value):
    try:
        __builtins__['float'](value)
        return 1, ''
    except ValueError:
        return 0, 'Not a valid float value'

import re
line_separator = re.compile("(\n|\r\n|\n\r)")

def line(value):
    if line_separator.findall(value):
        return 0, 'Multiple lines detected'
    else:
        return 1, ''

def text(value):
    str(value)
    return 1, ''

def boolean(value):
    try:
        value = int(value)
        if value in (0,1):
            return 1, ''
        else:
            return 0, 'Invalid value for boolean'
    except ValueError:
        return 0, 'Boolean value not an integer'
         
from DateTime.DateTime import DateTime, DateTimeError

def date(value):
    try:
        DateTime(value)
        return 1, ''
    except DateTimeError:
        return 0, 'Not a valid date (and time) value'

def email(value):
    try:
        value = str(value)
        if value.strip():
            if value.find('@') > 0:
                return 1, ''
            else:
                return 0, 'Invalid email address, try something like morten@nidelven-it.no'
        else:
            return 1, ''
    except:
        return 0, 'Something went very wrong, please contact support'
