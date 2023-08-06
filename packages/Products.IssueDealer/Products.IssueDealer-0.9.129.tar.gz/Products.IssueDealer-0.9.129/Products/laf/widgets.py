from cgi import escape

# It's important to note that, a widget must accept the value
# as a string too, in case input gathered from a form doesn't
# validate, we need to redisplay the widget to the user with
# the same value they entered

def integer(name, value):
    return """<input type="text" name="%s" value="%s" size="20" class="inputText" />""" % (name, value)

def float(name, value):
    return """<input type="text" name="%s" value="%s" size="20" class="inputText" />""" % (name, value)

def line(name, value):
    return """<input type="text" name="%s" value="%s" size="45" class="inputText" />""" % (name, escape(value))

def text(name, value):
    return """<textarea name="%s" rows="5" cols="72" style="font-size: 1em;">%s</textarea>""" % (name, escape(value))

def boolean(name, value):
    if value:
        return ("""<input type="radio" name="%s" value="1" checked="checked" />Yes """ % name) + \
    		("""<input type="radio" name="%s" value="0" />No""" % name)
    else:
        return ("""<input type="radio" name="%s" value="1" />Yes """ % name) + \
    		("""<input type="radio" name="%s" value="0" checked="checked" />No""" % name)

from DateTime import DateTime

def date(name, value):
    if isinstance(value, DateTime):
        value = value.strftime("%Y-%m-%d %H:%M")
    return """<input type="text" name="%s" value="%s" size="20" class="inputText" />""" % (name, value)


def email(name, value):
    return """<input type="text" name="%s" value="%s" size="45" class="inputText" />""" % (name, escape(value))
