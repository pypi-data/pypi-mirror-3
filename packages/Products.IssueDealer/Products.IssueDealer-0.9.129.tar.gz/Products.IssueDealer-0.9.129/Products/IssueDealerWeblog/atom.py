from Globals import Persistent
import OFS
import Acquisition
import AccessControl
from cgi import escape
import utilities
from xml.dom.minidom import parseString
from DateTime import DateTime
import re
import base64, sha

wsse_key_value = re.compile('\w[A-Za-z]+=".*?"')

def generate_atom_entry(issue, weblog):
    """Generates the XML for an Atom entry."""
    data = {}
    data['title'] = escape(issue.get_title)
    data['weblog_url'] = weblog.get_weblog_url()
    data['id'] = issue.id
    data['modified'] = utilities.render_as_W3CDTF(issue.modified)
    data['issued'] = utilities.render_as_W3CDTF(weblog.get_objects(meta_type='Relation', relation_=issue.id)[0].modified)
    data['get_weblog_host'] = weblog.get_weblog_host()
    data['render_contents_weblog'] = issue.render_contents_weblog()
    return """<?xml version="1.0" encoding="utf-8"?>
<entry>
<title>%(title)s</title>
<link rel="alternate" type="text/html"
	href="%(weblog_url)s/blog_entry?id=%(id)s" />
<modified>%(modified)s</modified>
<issued>%(issued)s</issued>
<id>tag:%(get_weblog_host)s,%(issued)s:%(id)s</id>
<content type="text/html" mode="escaped"><![CDATA[%(render_contents_weblog)s]]></content>
</entry>""" % data

class user:
    """Our own user thing!  Swching!"""

    def __init__(self, id):
        self.id = id

    def getId(self): return self.id

class atom_entry:

    def __init__(self, data):
        self.dom = parseString(data)

    def __getattr__(self, name):
        return self.get(name, node=0)

    def get(self, name, node=0):
        for node_ in self.dom.childNodes[0].childNodes:
            if node_.nodeName == name:
                if node:
                    return node_
                else:
                    return node_.childNodes[0].data
        else:
            raise AttributeError, name

class atom(
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager):
    """Atom implementation for Zope/Issue Dealer."""

    security = AccessControl.ClassSecurityInfo()
    nonces = ()

    def __init__(self, id):
        self.id = id

    security.declarePublic('index_html')
    def index_html(self):
        " "
        return self._v_message

    def nonce_is_valid(self, nonce):
        """Checks whether the nonce has been used before."""
        if filter(lambda x: nonce == x[1], self.nonces):
            return 0
        else:
            old = DateTime() - 3
            nonces = []
            for date, nonce_ in self.nonces:
                if date > old: 
                    nonces.append((date, nonce_))
            self.nonces = tuple(nonces) + ((DateTime(), nonce),)
            return 1

    def __bobo_traverse__(self, REQUEST, id):
        # Zope gobs up the authorization header, so we'll look at the
        # x-wsse header for now.  This could be coded a lot better :S
        if REQUEST.environ.has_key('HTTP_X_WSSE') and REQUEST.environ['HTTP_X_WSSE'].startswith('UsernameToken'):
            data = {}
            for key, value in map(lambda x: x.split('=', 1), wsse_key_value.findall(REQUEST.environ['HTTP_X_WSSE'])):
                data[key] = value[1:-1]
            data['Nonce'] = base64.decodestring(data['Nonce'])
            if not self.nonce_is_valid(data['Nonce']):
                REQUEST['AUTHENTICATED_USER'] = user('Anonymous')
                REQUEST.RESPONSE.setStatus(500)
                self._v_message = "Nonce rejected (it has been used before)"
                return self.index_html
            if abs(DateTime(data['Created']) - DateTime()) > 2:
                REQUEST['AUTHENTICATED_USER'] = user('Anonymous')
                REQUEST.RESPONSE.setStatus(500)
                self._v_message = "Created time rejected (it's too far off)"
                return self.index_html
            data['Password'] = self.acl_users.getUserById(data['Username'])._getPassword()
            digest = base64.encodestring(sha.new(data['Nonce'] + data['Created'] + data['Password']).digest()).replace("\n", "")
            if data['PasswordDigest'] == digest:
                REQUEST['AUTHENTICATED_USER'] = user(data['Username'])
            else:
                REQUEST['AUTHENTICATED_USER'] = user('Anonymous')                
        else:
            REQUEST['AUTHENTICATED_USER'] = user('Anonymous')
        arguments = {}
        arguments_ = REQUEST['PATH_INFO'][REQUEST['PATH_INFO'].rfind('/atom')+6:].split('/')
        for item in map(lambda x: x.split('='), filter(None, arguments_)):
            if len(item) == 1:
                key = item[0]
                value = None
            else:
                key, value = item
            arguments[key] = value
        if arguments.has_key('id'):
            assert arguments['id'] in self.getParentNode().get_published_ids()
        if REQUEST['REQUEST_METHOD'] == 'GET':
            self.GET(arguments)
        # Requires authentication
        if REQUEST['AUTHENTICATED_USER'].getId() == 'Anonymous':
            REQUEST.RESPONSE.setHeader('WWW-Authenticate', 'WSSE realm="weblog", profile="UsernameToken"')
            REQUEST.RESPONSE.setStatus(401)
            self._v_message = 'Authentication required'
            return self.index_html
        if REQUEST['REQUEST_METHOD'] == 'PUT':
            self.PUT(arguments)
        if REQUEST['REQUEST_METHOD'] == 'DELETE':
            self.DELETE(arguments)
        if REQUEST['REQUEST_METHOD'] == 'POST':
            self.POST(arguments)
        return self.index_html

    def GET(self, arguments):
        if not arguments.has_key('id'):
            self._v_message = \
              """<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://purl.org/atom/ns#">""" + \
              """<link rel="service.post" href="%s" type="application/x.atom+xml" title="%s" />""" % (
                self.getParentNode().get_weblog_url() + '/atom', escape(self.getParentNode().get_title())) + \
              """<link rel="service.feed" href="%s" type="application/x.atom+xml" title="%s" />""" % (
                self.getParentNode().get_weblog_url() + '/atom.xml', escape(self.getParentNode().get_title()))
            self.REQUEST.RESPONSE.setHeader('content-type', 'application/x.atom+xml')
            return
        try:
            issue = self.get_object(arguments['id'])
        except IndexError:
            self.REQUEST.RESPONSE.setStatus(404)
            self._v_message = 'Entry not found'
            return self.index_html
        self._v_message = generate_atom_entry(issue, self.getParentNode())
        self.REQUEST.RESPONSE.setHeader('content-type', 'application/x.atom+xml')
        self.REQUEST.RESPONSE.setStatus(200)

    def PUT(self, arguments):
        data = self.REQUEST._file.read()
        entry = atom_entry(data)
        issue = self.get_object(arguments['id']).getObject()
        issue.title = entry.title
        issue.contents = entry.content
        issue.modified = DateTime()
        type = entry.get('content', node=1).attributes['type']
        if type.value in ('text/html', 'text/xhtml'):
            format = 'html'
        else:
            format = 'text'
        issue.format = format
        issue.index_object()
        self._v_message = 'Successfully updated entry'

    def DELETE(self, arguments):
        self.getParentNode().get_objects(meta_type='Relation', relation=arguments['id'])[0].delete()
        self.getParentNode().get_object(arguments['id']).delete()
        self.REQUEST.RESPONSE.setStatus(200)
        self._v_message = 'Success'

    def POST(self, arguments):
        data = self.REQUEST._file.read()
        entry = atom_entry(data)
        type = entry.get('content', node=1).attributes['type']
        if type.value in ('text/html', 'text/xhtml'):
            format = 'html'
        else:
            format = 'text'
        issue = self.get_issue_dealer().manage_add_issue(title=entry.title, contents=entry.content, format=format)
        self.getParentNode().publish_issue(issue)
        self.REQUEST.RESPONSE.setStatus('201')
        self.REQUEST.RESPONSE.setHeader('Location', self.get_weblog_url() + '/atom/id=' + issue.id)
        self._v_message = 'Successfully uploaded entry'
