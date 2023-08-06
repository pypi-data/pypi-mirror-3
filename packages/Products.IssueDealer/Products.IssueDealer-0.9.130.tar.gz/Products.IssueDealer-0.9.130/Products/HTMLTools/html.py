"""A simple module for processing XML/XHTML data.

This software is released under the LGPL License, see
license.txt for more info."""

import re, popen2, string, os
import urlparse, httplib
import cStringIO
try:
    from mx.Tidy.Tidy import tidy as mxTidy
except ImportError:
    mxTidy = None
from feedparser import _sanitizeHTML

# Spaced and unspaced formatting tags, without
# any 'real' content
spaced=re.compile('</[b|i]>\s+<[b|i]>', re.S)
unspaced= re.compile('</[b|i]><[b|i]>', re.S)
# Start and end tags for body
body_start = re.compile('<body.*?>', re.S)
body_end = re.compile('</body.*?>', re.S)
# Image tag
image = re.compile(r'<img.*?>', re.S)
# Source attribute
source = re.compile(r"""src=("|').*?("|')""", re.S)
# Script tag, with 'real' content
script = re.compile(r"""<script.*?>.*?</script>""", re.S)
# Iframe tag, with 'real' content
iframe = re.compile(r"""<iframe.*?>.*?</iframe>""", re.S)
# Start of a tag
link_start = re.compile(r"""<a.*?>""", re.S)
# The href attribute
href = re.compile(r"""href=("|').*?("|')""", re.S)
# Form tag
# Iframe tag, with 'real' content
form = re.compile(r"""<form.*?>.*?</form>""", re.S)
# Content-type
content_type = re.compile('<meta.*?charset=.*?>', re.S)
# Charset
charset = re.compile(r"""charset=[-\w]*""", re.S)
# Head tag
head = re.compile(r"""<head>.*?</head>""", re.S)
# Title tag
title = re.compile(r"""<title>.*?</title>""", re.S)
# Contents of a tag
tag_content = re.compile(r""">.*?<""", re.S)

class InvalidHTML(SyntaxWarning):
    """Exception raised for invalid HTML."""
    pass

class tag:
    """Class representing an XHTML tag."""

    def __init__(self, tag, single=0):
        self.tag = tag
        self.single = single
        self.attributes = {}

    def build(self):
        """Builds an XHTML tag."""
        tag = "<" + self.tag
        if self.attributes:
            tag += " "
            for key, value in self.attributes.items():
                if self.tag == 'img':
                    if key in ('width', 'height'):
                        if self.attributes.has_key('style'):
                            if parse_style(self.attributes['style']).has_key(key):
                                pass
                            else:
                                tag += '%s="%s" ' % (key, value)
                        else:
                            tag += '%s="%s" ' % (key, value)
                    else:
                        tag += '%s="%s" ' % (key, value)
                else:
                    tag += '%s="%s" ' % (key, value)
            else:
                tag = tag[:-1]
        if self.tag == 'img' and not self.attributes.has_key('alt'):
            tag += ' alt="No description available"'
        if self.single:
            tag = tag +  " />"
        else:
            tag = tag + ">"
        return tag

def parse_style(style):
    """Parses the value of a style tag."""
    data = {}
    for item in filter(lambda x: x.strip(), style.split(';')):
        key, value = item.strip().split(':', 1)
        data[key.strip()] = value.strip()
    return data

def parse_attributes(tag, attribute=re.compile(r'\s?[a-zA-Z]*?=".*?"')):
    """Returns all attributes found in the tag."""
    items = map(lambda x: x.split('=', 1),
                map(lambda x: x.strip(),
                    attribute.findall(tag)))
    dictionary = {}
    for index in range(len(items)):
        dictionary[items[index][0]] = items[index][1][1:-1]
    return dictionary

def parse_tag(stringTag, reTag=re.compile(r'<[A-Za-z]+[0-9]?\s?')):
    """Parses the value of a tag and creates a tag instance."""
    if stringTag[-2:] == '/>':
        single = 1
    else:
        single = 0
    tag_type = reTag.search(stringTag).group()[1:].strip()
    parsed = tag(tag_type, single=single)
    parsed.attributes = parse_attributes(stringTag)
    return parsed

def parse_tag_contents(stringTag):
    return tag_content.search(stringTag).group()[1:-1]

def alter_attribute(data, function, attribute):
    """Alters the specified attribute on all XML elements.

    data - Well formed XML
    function - receives the attribute data
    attribute - name of the attribute to alter
    """
    reTag = re.compile('<.*?%s=.*?>' % attribute)
    reAttribute = re.compile(r'%s=("|\').*?("|\')' % attribute)
    start = 0
    while 1:
        tagMatch = reTag.search(data, start)
        if tagMatch is None:
            break
        attributeMatch = reAttribute.search(tagMatch.group())
        try:
            attributeValue = attributeMatch.group()[len(attribute) + 1:]
        except AttributeError:
            break
        data = data[:tagMatch.start()] + \
               tagMatch.group()[:attributeMatch.start()] + \
               attribute + '=' + function(attributeValue) + \
               tagMatch.group()[attributeMatch.end():] + data[tagMatch.end():]
        start = tagMatch.end()
    return data

def alter_tags(data, reTag=re.compile(r'<[A-Za-z]+[0-9]?.*?>', re.S)):
    """Rebuilds an XHTML snippet."""
    return reTag.sub(lambda x: parse_tag(x.group()).build(), data)

def _clean(html):
    """Cleans the HTML."""
    if mxTidy:
        try:
            errors, warnings, data, errordata = mxTidy(html, output_xhtml=1,
              numeric_entities=1, wrap=0, char_encoding='utf8')
            return data, errors, warnings, errordata
        except:
            print 'Failed to clean html'
            raise
    else:
        pass
    return html, 0, 0, ""        

def clean(html):
    """Scrubs HTML data."""
    # Run the HTML through an external cleanup tool
    html, errors, warnings, errordata = _clean(html)
    # Find the body tags and extract the contained HTML
    try:
        start = body_start.search(html)
        start = start.start() + len(start.group())
        end = body_end.search(html)
        html = html[start:end.start()]
    except AttributeError:
        # Data didn't have body tags
        pass
    # Remove empty redundant elements
    html = spaced.sub(' ', html)
    html = unspaced.sub('', html)
    # Lowercase the contents of the style tag
    html = alter_attribute(html, string.lower, 'style')
    # Rebuild some tags that have redundant data
    html = alter_tags(html)
    # Remove <script> tags
    html = script.sub('', html)
    # Remove <iframe> tags
    html = iframe.sub('', html)
    # Remove <form> tags
    html = form.sub('', html)
    # Verify that the result is well formed HTML
    verify("<html><head></head><body>" + html + "</body></html>")
    return html

def paranoid_clean(html):
    "Cleans the HTML, being really paranoid as we don't know the source."
    return clean(_sanitizeHTML(html, 'utf-8'))

def verify(data, dump=1):
    """Verifies that the data is proper XHTML."""
    data, errors, warnings, errordata = _clean(data)
    if errors > 0:
        if dump:
            print data
            print error
        raise InvalidHTML, 'Malformed input to tidy'

def find_absolute_url(host, url, path=None):
    """Returns the absolute URL."""
    if url[:7] == 'mailto:':
        return url
    if url[:6] == 'irc://':
        return url
    if url[0] == '/':
        absolute_url = 'http://%s%s' % (host, url)
    elif url[:7] == 'http://':
        absolute_url = url
    else:
        if url[:2] == './':
            absolute_url = 'http://' + host + path
            if absolute_url[-1] != '/':
                absolute_url += '/'
            absolute_url += url[2:]
        else:
            if url[0] != '/':
                absolute_url = 'http://' + host + path
                if absolute_url[-1] != '/':
                    absolute_url = absolute_url + '/'
                absolute_url += url
            else:
                absolute_url = 'http://' + host + url
    return absolute_url

def fetch_webpage(url, out=None):
    """Fetches the webpage with images from url."""
    if out is None:
        import sys
        out = sys.stderr
    data, page_meta = fetch(url)
    headers = page_meta[-1]
    if page_meta[0] != 200:
        out.write('Failed to fetch webpage from %s\n' % url)
    else:
        out.write('Fetched webpage from %s\n' % url)
    content_type_ = ''
    if headers.has_key('content-type'):
        content_type_ = headers['content-type']
    try:
        content_type_ = content_type.findall(data)[0]
    except IndexError: pass
    charset_ = 'ascii'
    if content_type_:
        try:
            charset_ = charset.findall(content_type_)[0][8:]
        except IndexError: pass
    try:
        title_ = parse_tag_contents(title.findall(head.findall(data)[0])[0])
    except IndexError:
        title_ = 'Untitled'
    data = data.decode(charset_).encode('utf-8')
    html = clean(data)
    images = []
    images_ = {}
    errors = []
    for image_ in image.findall(html):
        try:
            source_ = source.search(image_).group()
            if not source_ in images:
                images.append(source_[5:-1])
        except AttributeError:
            out.write('Failed to find source for image %s\n' % image_)
    protocol, host, path = urlparse.urlparse(url)[:3]
    start = 0
    while 1:
        match = link_start.search(html, start)
        if not match: break
        tag_ = parse_tag(match.group())
        start = match.end()
        link = href.search(match.group())
        if link:
            tag_.attributes['href'] = find_absolute_url(host, link.group()[6:-1], path=path)
            html = html[:match.start()] + tag_.build() + html[match.end():]
    if images:
        for image_ in images:
            image_url = find_absolute_url(host, image_, path=path)
            try:
                data, meta = fetch(image_url)
                if meta[0] == 200:
                    images_[image_] = (data, image_url, meta[0], meta[1], meta[2])
                    out.write('Downloaded image %s \n' % image_url)
                else:
                    out.write('Failed to download image %s from %s\n' % (image_, image_url))
                    out.write(str(meta) + '\n')
            except:
                out.write('Failed to download image %s from %s\n' % (image_, image_url))
                import sys, traceback, string
                type_, val, tb = sys.exc_info()
                sys.stderr.write(string.join(
                    traceback.format_exception(type_, val, tb), ''))
    print charset_, type(html)
    return {'page':(html, page_meta), 'images':images_, 'title':title_}
            
def fetch(url):
    """Retrieves a file from the given URL.  Currently only HTTP is supported."""
    protocol, host, path = urlparse.urlparse(url)[:3]
    connection = httplib.HTTP(host)
    connection.putrequest('GET', path)
    connection.putheader('host', host)
    connection.putheader('user-agent', 'Python/HTMLTools')
    connection.endheaders()
    # Get the result
    response, message, result = connection.getreply()
    return connection.getfile().read(), (response, message, result)

def test():
    """Checks that the verify function complains about invalid data."""
    try:
        verify('<x>xp<x/px>', dump=0)
    except InvalidHTML:
        pass
    else:
        # This probably means that a tool to verify the
        # data couldn't be found.
        raise Exception

def test2(data=None):
    """Checks that the alter tags works and that it produces proper XHTML."""
    data = alter_tags(data or open('test.html').read())
    verify(data)

def test3():
    """Checks that the clean function produces proper XHTML."""
    data = clean(open('test.html').read())
    verify(data)

def test4():
    """Checks that the fetch function works."""
    result = fetch_webpage('http://www.nidelven-it.no/articles/introduction_to_thunderbird')
    #print result['page']

if __name__ == '__main__':
    test()
    test2()
    test3()
    test4()

