import xmlrpclib
from Globals import Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
from cgi import escape
import string
from DateTime import DateTime
from Products import IssueDealer
from Products.IssueDealer import session_manager, base, mixins, permissions

def manage_add_weblog_publisher_edit(self, id=None, title='', REQUEST=None):
    """Add a Weblog publisher."""
    if id is None:
        id = self.get_unique_id()
    weblog_publisher_ = weblog_publisher(id, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id())
    self._setObject(id, weblog_publisher_)
    weblog_publisher_ = self._getOb(id)
    weblog_publisher_.version = self.get_issue_dealer().filesystem_version
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')
    else:
        return weblog_publisher_

class weblog_publisher(
    ZCatalog.CatalogAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,
    mixins.publisher
    ): 
    """Weblog publisher class.

    An weblog publisher publishes issues to a weblog.
    """

    meta_type = 'Weblog publisher'
    publisher = 1

    manage_options = (OFS.Folder.Folder.manage_options[0],) + \
        (
            {'label': 'View',       'action': ''},
            {'label': 'Security',   'action': 'manage_access'},
        )

    security = AccessControl.ClassSecurityInfo()
    security.setDefaultAccess('allow')

    security.declareProtected(permissions.edit_publishers, 'publish', 'index_html', 'get_title')
    index_html = PageTemplateFile('edit.pt', globals())

    def __init__(self, id, title='Weblog publisher', weblog_url='',
                 publish=1, weblog_id='', username='',
                 password='', creator='', owner=''):
        self.id = id
        self.title = title
        self.weblog_url = weblog_url
        self.weblog_id = weblog_id
        self.publish = publish
        self.username = username
        self._password = password
        self.creator = creator
        self.owner_ = owner
        self.published = []

    security.declareProtected(permissions.publish_issues, 'publish_issue')
    def publish_issue(self, issue):
        """Publishes the issue to the weblog."""
        connection = xmlrpclib.ServerProxy(self.weblog_url)
        post_id = connection.metaWeblog.newPost(self.weblog_id,
                                                self.username,
                                                self._password,
                                                {'title':issue.title, 'description':issue.render_contents()},
                                                xmlrpclib.Boolean(self.publish))
        self.published.append((issue.id, post_id, DateTime()))
        self.published = self.published

    security.declareProtected(permissions.edit_publishers, 'manage_edit')
    def manage_edit(self, title='', weblog_url='', weblog_id='',
                    publish=1, username='', password='',
                    REQUEST=None):
        """Edits the publisher."""
        self.title = title
        self.weblog_url = weblog_url
        self.weblog_id = weblog_id
        self.publish = int(publish)
        self.username = username
        if password.strip():
            self._password = password
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    def _update(self):
	pass

InitializeClass(weblog_publisher)

from Products.IssueDealer.issue_dealer import issue_dealer, base

issue_dealer.manage_add_weblog_publisher_edit = manage_add_weblog_publisher_edit
issue_dealer.all_meta_types = issue_dealer.all_meta_types + [
    {'visibility': 'Global',
     'interfaces': [],
     'action': 'manage_add_weblog_publisher_edit',
     'permission': 'Add Weblog publisher',
     'name': 'Weblog publisher',
     'product': 'Issue Dealer',
     'instance': ''},]
IssueDealer.add_publisher(weblog_publisher, manage_add_weblog_publisher_edit)

