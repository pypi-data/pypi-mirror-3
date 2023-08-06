from Globals import Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
from Products.IssueDealer import base
from cgi import escape
import string
from DateTime import DateTime
from Products import IssueDealer
from Products.IssueDealer import session_manager, base, mixins, permissions
import base64, davlib, urllib

def cookId(path):
    """Gets the name of a file, based on path."""
    if path.find('image?id=') > -1:
        return path.split('image?id=')[-1]
    else:
        return path[max(path.rfind('/'),
                    path.rfind('\\'),
                    path.rfind(':'),
                    )+1:]
    
def manage_add_webdav_publisher_edit(self, id=None, title='', REQUEST=None):
    """Add a WebDAV publisher."""
    if id is None:
        id = self.get_unique_id()
    webdav_publisher_ = webdav_publisher(id, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id())
    self._setObject(id, webdav_publisher_)
    webdav_publisher_ = self._getOb(id)
    webdav_publisher_.version = self.get_issue_dealer().filesystem_version
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')
    else:
        return webdav_publisher_

class webdav_publisher(
    ZCatalog.CatalogAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,
    mixins.publisher,
    ): 
    """Webdav publisher class.

    An Webdav publisher publishes issues to a Webdav
    """

    meta_type = 'WebDAV publisher'
    publisher = 1
    webdav_image_url = ''

    manage_options = (OFS.Folder.Folder.manage_options[0],) + \
        (
            {'label': 'View',       'action': ''},
            {'label': 'Security',   'action': 'manage_access'},
        )

    security = AccessControl.ClassSecurityInfo()
    security.setDefaultAccess('allow')

    security.declareProtected(permissions.edit_publishers, 'edit',
                              'index_html', 'get_title')
    index_html_cmf2 = PageTemplateFile('index_cmf.pt', globals())
    index_html = PageTemplateFile('index.pt', globals())
    edit = PageTemplateFile('edit.pt', globals())
    publish = PageTemplateFile('publish.pt', globals())

    def __init__(self, id, title='WebDAV publisher', webdav_url='',
                 webdav_image_url='', username='', password='',
                 creator='', owner='', header='', footer=''):
        self.id = id
        self.title = title
        self.webdav_url = webdav_url
        self.webdav_image_url = webdav_image_url
        self.username = username
        self._password = password
        self.creator = creator
        self.owner_ = owner
        self.header = header
        self.footer = footer
        self.published = []

    def _update(self):
	pass

    security.declareProtected(permissions.publish_issues, 'publish_issue')
    def publish_issue(self, issue):
        """Publishes Issues to a WebDAV server."""
        self.REQUEST['issue'] = issue
        return self.publish()

    security.declareProtected(permissions.publish_issues, 'publish_directly')
    def publish_directly(self, issue=None, REQUEST=None):
        """Publishes the Issue directly, without asking anything about how it should be published."""
        if issue is None:
            issue = self.get_object(REQUEST['id'])
        self.publish_webdav(issue.id, issue.id, add_local_images=1, add_external_images=1)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(issue.absolute_url)        

    security.declareProtected(permissions.publish_issues, 'publish_webdav')
    def publish_webdav(self, issue, id, add_local_images=None, add_external_images=None, contents=None):
        """Publishes the Issue to a WebDAV server."""
        issue = self.get_object(issue)
        headers = {'AUTHORIZATION': 'Basic %s' % \
          string.replace(
            base64.encodestring(
            "%s:%s" % (self.username, self._password)), "\012", "")
        }
        host, path = urllib.splithost(urllib.splittype(self.webdav_url)[1])
        if not path.strip(): path = '/'
        if path[-1] != '/':
            path += '/'
        host, port = urllib.splitnport(host)
        if port < 0:
            port = None

        # Meta code
        def make_connection(host=host, port=port):
            return davlib.DAV(host, port)
        def handle_response(response, add_message=self.get_user_preferences().add_message):
            if str(response.status)[0] in ('4', '5'):
                # An error occured
                add_message('HTTP Error %s when publishing' % response.status, response.status)
            else:
                add_message('Published (Response code %s)' % response.status, response.status)

        # Handling local and external images
        contents = contents or issue.render_contents()
        if self.webdav_image_url.strip():
            image_path = self.webdav_image_url.strip()
        else:
            image_path = path + id + '_images/'
        if add_local_images:
            for image in issue.get_local_image_links():
                imageId = cookId(image)
                contents = contents.replace(image, image_path + imageId)
        if add_external_images:
            for image in issue.get_external_image_links():
                imageId = cookId(image)
                contents = contents.replace(image, image_path + imageId)

        # Uploading images
        if (add_local_images or add_external_images) and issue.get_image_links():
            connection = make_connection()
            response = connection.mkcol(path + id + '_images', extra_hdrs=headers)
            connection.close()
            if add_local_images:
                for image in issue.get_local_images():
                    headers2 = headers.copy()
                    headers2['content-type'] = image.content_type
                    connection = make_connection()
                    self.get_user_preferences().add_message('Publishing image %s' % image.id)
                    try:
                        data = image.data.data
                    except AttributeError:
                        data = image.data
                    handle_response(connection.put(image_path + image.id, data, extra_hdrs=headers2))
            if add_external_images:
                for image in issue.get_external_image_links():
                    connection = urllib.urlopen(image)
                    headers2 = headers.copy()
                    try:
                        headers2['content-type'] = connection.headers['content-type']
                    except KeyError:
                        headers2['content-type'] = mimetypes.guess_type(image)
                    data = connection.read()
                    connection = make_connection()
                    handle_response(connection.put(image_path + imageId, data, extra_hdrs=headers2))

        # Publishing the issue
        connection = make_connection()
        headers2 = headers.copy()
        headers2['content-type'] = 'text/xhtml'
        self.get_user_preferences().add_message('Publishing issue')
        response = connection.put(path + id,
                       self.header + contents + self.footer,
                       extra_hdrs=headers)
        handle_response(response)
        if str(response.status)[0] in ('4', '5'):
            connection.close()
        else:
            connection.close()
            connection = make_connection()
            connection.setprops(path + id, title=issue.title)
            connection.close()
        self.published.append((issue.id, id, DateTime()))
        self.published = self.published
        self.REQUEST.RESPONSE.redirect(self.get_object(
            self.get_user_preferences().last_visited_issue).absolute_url)

    security.declareProtected(permissions.edit_publishers, 'manage_edit')
    def manage_edit(self, title='', webdav_url='', webdav_image_url='',
                    username='', password='',
                    header='', footer='',
                    REQUEST=None):
        """Edits the publisher."""
        self.title = title
        self.webdav_url = webdav_url
        self.webdav_image_url = webdav_image_url
        self.username = username
        self.header = header
        self.footer = footer
        self.index_object()
        if password.strip():
            self._password = password
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

InitializeClass(webdav_publisher)

from Products.IssueDealer.issue_dealer import issue_dealer, base

issue_dealer.manage_add_webdav_publisher_edit = manage_add_webdav_publisher_edit
issue_dealer.all_meta_types = issue_dealer.all_meta_types + [
    {'visibility': 'Global',
     'interfaces': [],
     'action': 'manage_add_webdav_publisher_edit',
     'permission': 'Add Webdav publisher',
     'name': 'WebDAV publisher',
     'product': 'Issue Dealer',
     'instance': ''},]
IssueDealer.add_publisher(webdav_publisher, manage_add_webdav_publisher_edit)
