from cgi import escape
import string
import utilities
import cStringIO
import htmllib, formatter
import urllib
from Products.HTMLTools import html
from docutils.core import publish_string
import html4css1_inline
from htmlentitydefs import name2codepoint

def alter_entities(text):
    for key, value in name2codepoint.items():
        entity = '&%s;' % key
        if text.find(entity):
            text = text.replace(entity, '&#%s;' % value)
    return text

def render_contents_weblog(self, unlinked=0):
    if self.format == 'html':
        contents = self.contents
        for image in get_image_links(self):
            path = urllib.splithost(urllib.splittype(image)[1])[1]
            try:
                image_ = self.restrictedTraverse(path)
                if image_.meta_type == 'Image':
                    contents = contents.replace(image, path)
            except IndexError:
                print 'IndexError', image
            except KeyError:
                if image.find('image?id=') > -1:
                    id = path.split('image?id=')[-1]
                    try:
                        contents = contents.replace(image,
				 self.REQUEST['URL1'] + '/image?id=' + id)
                    except IndexError: pass
        for link in get_internal_links(self):
            id = link.split('/')[-1].split('=')[-1]
            contents = contents.replace(link,
		self.REQUEST['URL1'] + '/blog_entry?id=' + id)
        return alter_entities(contents)
    if self.format == 'file':
        file = getattr(self, self.filename)
        if file.content_type == 'text/plain':
            return alter_entities('<pre>' + str(file.data) + '</pre>')
        if file.content_type == 'text/html':
            return alter_entities(str(file.data))
        else:
            return alter_entitites('<a href="./files/%s/%s">Download file %s</a>' % \
		(self.id, urllib.quote(self.filename), escape(self.filename)))
    else:
        return alter_entities(render_contents(self, unlinked=unlinked))

def render_contents(self, skip_less_more=0, unlinked=0):
    """Renders the contents."""
    if self.format == 'file':
        file = getattr(self, self.filename)
        if file.content_type == 'text/plain':
            return '<pre>' + str(file.data) + '</pre>'
        if file.content_type == 'text/html':
            return str(file.data)
        if file.content_type.split('/')[0] == 'image':
            return '<img src="./%s" alt="No description available" />' % self.filename
        else:
            return 'Unable to display issue contents, download as a file: ' \
                   '<a href="./%s">%s</a>' % (self.filename, self.filename)
    if not self.contents.strip():
        return ""
    if self.format == 'stx':
        if (self.REQUEST.has_key('expand_text')
            and self.REQUEST['expand_text']):
            html = render_stx_as_html(self)
            if not skip_less_more:
                html += ' <a href="?expand_text:int=0">Less..</a>'
            return html
        else:
            contents = render_stx_as_html(self)
            if 0: # self.get_user().logged_in():
                size = 200
            else:
                size = None
            if self.REQUEST.has_key('expand_text') and self.REQUEST['expand_text']:
                size = None
            if size and len(self.contents) > size:
                contents += ' <a href="%s?expand_text:int=1">More..</a>' % \
                            self.get_admin_url()
            return contents
    elif self.format == 'text':
        return render_text_as_html(self, unlinked=unlinked)
    elif self.format == 'html':
        return self.contents

def render_stx_as_html(self):
    if 0:# self.get_user().logged_in():
        size = 200
    else:
        size = None
    if self.REQUEST.has_key('expand_text') and self.REQUEST['expand_text']:
        size = None
    contents = self.contents[:size]
    try:
        return publish_string(contents, writer=html4css1_inline.Writer(),
          parser_name='rst', settings_overrides={'input_encoding':'utf-8',
                                                 'output_encoding':'utf-8',
                                                 'report_level':3})
    except:
        # Failed at returning the text as RST HTML,
        # try regular text instead.
        utilities.log("Failed at converting STX text to HTML")
        utilities.log(contents)
        import sys, traceback, string
        type, val, tb = sys.exc_info()
        utilities.log(string.join(
            traceback.format_exception(type, val, tb), ''))
        return render_contents_as_text(self)
    
def render_text_as_html(self, unlinked=0):
    if 0: #self.get_user().logged_in():
        size = 200
    else:
        size = None
    if self.REQUEST.has_key('expand_text') and self.REQUEST['expand_text']:
        size = None
    contents = self.contents[:size]
    contents = contents.replace('\r\n', '\n')
    contents = contents.replace('\n\r', '\n')
    contents = escape(contents)
    lines = contents.split('\n')
    new_lines = []
    for line in lines:
        if not line:
            new_lines.append(line)
            continue
        new_line = ''
        if line[0] == ' ':
            for character in line:
                if character == ' ':
                    new_line += '&nbsp;'
                else:
                    new_line += character
        else:
            new_line = line
        new_lines.append(new_line)
    text = string.join(new_lines, '<br />')
    if unlinked:
        return text
    else:
        return utilities.hyperlink_urls(text)

class MyAbstractFormatter(formatter.AbstractFormatter):

    def add_line_break(self):
        if not (self.hard_break or self.para_end):
            self.writer.send_line_break()
            self.have_label = self.parskip = 0
        self.nospace = 1
        self.softspace = 0

def render_contents_as_text(self, size=None):
    if self.format in ('stx', 'text'):
        return self.contents[:size]
    elif self.format in ('html', 'file'):
        file = cStringIO.StringIO()
        parser = htmllib.HTMLParser(MyAbstractFormatter(
            formatter.DumbWriter(file=file)))
        parser.feed(self.render_contents())
        parser.close()
        data = file.getvalue()[:size]
        return data
    else:
        raise NotImplementedError

def get_object(self, id):
    try:
        return self.catalog_search(id=id)[0]
    except IndexError:
        return self.catalog_search(id='missing')[0]
    
def get_related_object(self):
    return get_object(self, self.relation)

def get_image_links(self):
    images = []
    if self.format == 'html':
        for image in html.image.findall(self.contents):
            try:
                images.append(html.source.search(image).group()[5:-1])
            except AttributeError:
                # Broken image tag, skip it
                pass
    return images

def get_internal_links(self):
    links = []
    if self.format == 'html':
        for link in html.link_start.findall(self.contents):
            try:
                link = html.href.search(link).group()[6:-1]
                id = link.split('/')[-1].split('=')[-1].strip()
                if id:
                    object = self.get_object(id)
                    links.append(link)
            except IndexError:
                # Not a local issue, skip it
                pass
            except AttributeError:
                # Broken link, skip it
                pass
    return links
