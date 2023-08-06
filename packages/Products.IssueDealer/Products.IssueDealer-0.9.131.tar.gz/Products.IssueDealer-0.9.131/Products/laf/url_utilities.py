import re, cgi, urllib

# Where did this come from?
urlchars = r'[A-Za-z0-9/:@_%~#=&\.\-\?;\+,\(\)\$]+'
url = r'["=]?((http|ftp|https|irc|telnet)://%s)' % urlchars
example = """At http://www.python.org you can see things.
At ftp://ftp.python.org you can download things.
At https://www.python.org you can't find anything!"""

def hyperlink_urls(text):
    """Replaces all URLs in the text with HTML hyperlinks."""
    regexp = re.compile(url, re.I|re.S)
    def replace(match):
        url = match.groups()[0]
        return create_hyperlink(url, url)
    text = regexp.subn(replace, text)[0]
    return text

def create_hyperlink(url, title, size=60, etc="...",
                     klass=None, escape=1, **keywords):
    """Creates a hyperlink."""
    if size:
        if len(title) > size:
            title = title[:size] + etc
    if klass is not None:
        keywords['class'] = klass
    if escape:
        title = cgi.escape(title)
    attributes = ""
    if keywords:
        for key, value in keywords.items():
            attributes += '%s="%s" ' % (key, value)
        else:
            attributes = attributes[:-1]
    return '<a href="%s" %s>%s</a>' % (url, attributes, title)

def create_query_string(self, query_string, replace=0, **keywords):
    """Creates a new query string with keywords."""
    items = []
    for item in query_string.split('&'):
        if not item.strip(): continue
        try:
            items.append(item.split('='))
        except:
            raise str(item.split('='))
    for key, value in keywords.items():
        value = urllib.quote(str(value))
        set = 0
        if replace:
            for index in range(len(items)):
                key_, value_ = items[index]
                if key_ == key:
                    items[index][1] = value
                    set = 1
            else:
                if not set:
                    items.append([key, value])
        else:
            items.append([key, value])
    result = '&'.join(map(lambda x: '%s=%s' % (x[0],x[1]), items))
    return result

def build_url(main='', query=''):
    if not query.strip():
        return main
    separator = ''
    if main.endswith('?'):
        if query.startswith('?'):
            return main + query[1:]
        else:
            return main + query
    else:
        if query.startswith('?'):
            return main + query
        else:
            return main + '?' + query

def rebuild_url(url, replace=1, **keywords):
    """Rebuilds the URL with (new) keyword/value pairs."""
    if url.find('?') > -1:
        path, arguments = url.split('?')
    else:
        if not keywords: return url
        path, arguments = (url, '')
    return path + '?' + create_query_string(None, arguments, replace=replace, **keywords)

if __name__ == '__main__':
    print rebuild_url('http://blogologue.com/blog_entry?id=1202762343X92', test='locate', test2='no no')
