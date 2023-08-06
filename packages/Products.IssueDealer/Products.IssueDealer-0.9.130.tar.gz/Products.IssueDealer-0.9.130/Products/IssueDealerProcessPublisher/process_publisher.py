from Globals import DTMLFile, Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
from Products.IssueDealer import base
from cgi import escape
import string
from DateTime import DateTime, DateTimeZone
from Products import IssueDealer
from Products.IssueDealer import session_manager, base, mixins, relation, permissions

def manage_add_process_publisher_edit(self, id=None, title='', REQUEST=None):
    """Add a process publisher."""
    if id is None:
        id = self.get_unique_id()
    process_publisher_ = process_publisher(id, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id())
    self._setObject(id, process_publisher_)
    process_publisher_ = self._getOb(id)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')
    else:
        return process_publisher_

class process_publisher(
    ZCatalog.CatalogAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,
    mixins.publisher
    ): 
    """Process publisher class.

    A process publisher publishes processes.
    """

    meta_type = 'Process publisher'
    publisher = 1

    security = AccessControl.ClassSecurityInfo()
    security.setDefaultAccess('allow')

    security.declareProtected(permissions.edit_publishers, 'edit', 'publish', 'deal')
    security.declarePublic('get_title')
    edit = PageTemplateFile('edit.pt', globals())
    deal = PageTemplateFile('index.pt', globals())
    remote = DTMLFile('remote', globals())
    manage_add_relation = relation.relation.manage_add_relation

    def __init__(self, id, title='Processes', creator='', owner=''):
        self.id = id
        self.title = title
        self.creator = creator
        self.owner_ = owner
	self.published = []
        self.modified = self.created = DateTime()

    security.declareProtected(permissions.view_issue_dealer, 'render_importance')
    def render_importance(self):
        " "
        return "N/A"

    def publish_issue(self, issue):
        """Publishes the issue."""
        relation = self.manage_add_relation(relation_=issue.id)

    security.declareProtected(permissions.view_issue_dealer, 'get_admin_url')
    def get_admin_url(self):
        """Returns the adminstrator view."""
        return self.absolute_url() + '/deal'
 
    security.declareProtected(permissions.edit_publishers, 'admin_edit')
    def admin_edit(self, title='', REQUEST=None):
        """Edits the publisher."""
        self.title = title
        self.index_object()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    def remove(self, ids=[]):
        """Removes the specified issues from the weblog."""
        for id in ids:
            self.get_object(id).delete()
        self.REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declareProtected(permissions.view_issue_dealer, 'get_published_ids')
    def get_published_ids(self):
        "Returns the published ids."
        return map(lambda x: x.relation, self.get_objects(meta_type='Relation', sort_order='reverse', deleted=0))

InitializeClass(process_publisher)

from Products.IssueDealer.issue_dealer import issue_dealer, base

issue_dealer.manage_add_process_publisher_edit = manage_add_process_publisher_edit
issue_dealer.all_meta_types = issue_dealer.all_meta_types + [
    {'visibility': 'Global',
     'interfaces': [],
     'action': 'manage_add_process_publisher_edit',
     'permission': 'Add Local Weblog publisher',
     'name': 'Local Weblog publisher',
     'product': 'Issue Dealer',
     'instance': ''},]
IssueDealer.add_publisher(process_publisher, manage_add_process_publisher_edit)

