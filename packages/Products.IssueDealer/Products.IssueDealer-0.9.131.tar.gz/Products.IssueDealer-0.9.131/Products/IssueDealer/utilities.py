from AccessControl.PermissionRole import rolesForPermissionOn
import sys, traceback, string
import id_config
import zLOG
from DateTime import DateTime
from cStringIO import StringIO

def log(message):
    if id_config.verbose:
        print message

def dump_error_log():
    type, val, tb = sys.exc_info()
    trace = string.join(
      traceback.format_exception(type, val, tb), '')
    zLOG.LOG('issue dealer', 100, trace)
    #sys.stderr.write(trace)
    del type, val, tb

def reverse(sequence):
    """Reverses a sequence."""
    if type(sequence) is type(()):
        new = ()
        index = range(len(sequence))
        index.reverse()
        for i in index:
            new += (sequence[index],)
        return sequence
    elif type(sequence) is type([]):
        new = sequence[:]
        new.reverse()
        return new
    else: raise NotImplementedError, str(type(sequence))

from Products.laf.utilities import simple

class user:

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, user, context):
        self._user = user
        self._context = context

    def logged_in(self):
        return self.get_id() != None

    def get_id(self):
        return self._user.getId()

    def has_permission(self, permission, object=None):
        """Returns a truth value if user has the given permission."""
        object = object or self._context
        permission_roles = rolesForPermissionOn(permission, object)
        if 'Anonymous' in permission_roles: return 1
        for role in self._user.getRolesInContext(object):
            if role in permission_roles: return 1
        return 0

def generate_select(name, start, end, step, padding=0, selected=None, starting_options=[]):
    select = "<select name='%s'>" % name
    for x in starting_options + range(start, end, step):
        if selected:
            if selected == x:
                        select += '<option selected="selected" value="%s">%s</option>' % (x,x)
                        continue
        select += '<option value="%s">%s</option>' % (x,x)
    return select + "</select>"

def render_datetime_widget(selected_date=None):
    """selected_date is a datetime object."""
    if selected_date:
        selected_year = selected_date.year()
        selected_month = selected_date.month()
        selected_day = selected_date.day()
        selected_hour = selected_date.hour()
        selected_minute = selected_date.minute()
        selected_minute = selected_minute - (selected_minute % 5)    
        if not selected_hour and not selected_minute:
            selected_hour = selected_minute = '---'
    else:
        selected_year = selected_month = selected_day = None
        selected_hour = selected_minute = '---'
    widget = ""
    widget += generate_select('due_year', 2005, 2011, 1, selected=selected_year) + ' '
    widget += generate_select('due_month', 1, 13, 1, selected=selected_month) + ' '
    widget += generate_select('due_day', 1, 32, 1, selected=selected_day) + ' - '
    widget += generate_select('due_hour', 1, 25, 1, selected=selected_hour, starting_options=['---']) + ' '
    widget += generate_select('due_minute', 0, 60, 5, selected=selected_minute, starting_options=['---'])
    return widget

def get_due_date(due, request):
    """Returns the due DateTime, or None."""
    if due:
        if request:
            due = request
        if due.has_key('due'):
            due_year = int(due['due_year'])
            due_month = int(due['due_month'])
            due_day = int(due['due_day'])
            try:
                due_hour = int(due['due_hour'])
                due_minute = int(due['due_minute'])
            except ValueError:
                due_hour = 0
                due_minute = 0
            for x in range(0,4):
                try:
                    due = DateTime('%s/%s/%s %s:%s' % (due_year, due_month, due_day-x, due_hour, due_minute))
                    break
                except:
                    print 'error on %s/%s/%s %s:%s' % (due_year, due_month, due_day-x, due_hour, due_minute)
                    pass
        else:
            due = None
    else:
        due = None
    return due

def get_unique_values(sequences):
    unique = []
    for sequence in sequences:
        for item in sequence:
            if not item in unique:
                unique.append(item)
    return unique

def get_unique_values_single(sequence):
    unique = []
    for item in sequence:
        if not item in unique:
            unique.append(item)
    return unique

def parse_tags(text):
    """Parses tags."""
    return map(lambda x: x.strip().replace(',', ':'), StringIO(text).readlines())

from Products.laf.url_utilities import hyperlink_urls

if __name__ == '__main__':
    print hyperlink_urls(example)
