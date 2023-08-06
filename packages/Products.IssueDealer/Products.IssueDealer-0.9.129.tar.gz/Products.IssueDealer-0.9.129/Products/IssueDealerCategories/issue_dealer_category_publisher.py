from Globals import Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products.ZCatalog import CatalogAwareness
from Products.IssueDealer import base
from cgi import escape
import string
from DateTime import DateTime
from Products import IssueDealer
from Products.IssueDealer import session_manager, base, mixins, relation, permissions

def manage_add_category_publisher_edit(self, id=None, title='', REQUEST=None):
    """Add a Category publisher."""
    if id is None:
        id = self.get_unique_id()
    category_publisher_ = category_publisher(id, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id()
    )
    self._setObject(id, category_publisher_)
    category_publisher_ = self._getOb(id)
    category_publisher_.version = self.get_issue_dealer().filesystem_version
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')
    else:
        return category_publisher_

class category_publisher(
    CatalogAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,
    mixins.relation_publisher
    ): 
    """Category publisher class.

    An category publisher publishes issues for category use.
    """

    meta_type = 'Category publisher'
    publisher = 1
    show_path = 0
    access_level = 'private'

    manage_options = (OFS.Folder.Folder.manage_options[0],) + \
        (
            {'label': 'View',       'action': ''},
            {'label': 'Security',   'action': 'manage_access'},
        )

    security = AccessControl.ClassSecurityInfo()
    security.setDefaultAccess('allow')

    security.declareProtected(permissions.edit_publishers, 'edit', 'publish', 'index_html', 'get_title')
    index_html = PageTemplateFile('index.pt', globals())
    edit = PageTemplateFile('edit.pt', globals())
    manage_add_relation = relation.relation.manage_add_relation

    def __init__(self, id, title='Category publisher', show_path=0, creator='', owner=''):
        self.id = id
        self.title = title
        self.show_path = show_path
        self.creator = creator
        self.owner_ = owner
	self.created = self.modified = DateTime()
        self.published = []

    security.declareProtected(permissions.edit_publishers, 'manage_edit')
    def manage_edit(self, id=None, title='', show_path=0, REQUEST=None):
        """Edits the publisher."""
        if id and id != self.id:
            self.getParentNode().manage_renameObjects(ids=[self.id], new_ids=[id])
            get_transaction().commit()
        self.title = title
        self.show_path = show_path
        request = REQUEST
        self.access_level = request['access_level']
        if request['access_level'] == 'private':
            self.manage_permission(permissions.view_issue_dealer, roles=['Owner'])
            self.manage_permission(permissions.add_edit_issues_and_relations, roles=['Owner'])
        if request['access_level'] == 'shared':
            self.manage_permission(permissions.view_issue_dealer, roles=['Authenticated'])
            self.manage_permission(permissions.add_edit_issues_and_relations, roles=['Authenticated'])
        if request['access_level'] == 'public':
            self.manage_permission(permissions.view_issue_dealer, roles=['Anonymous'])
            self.manage_permission(permissions.add_edit_issues_and_relations, roles=['Anonymous'])
	self.modified = DateTime()
	self.index_object()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declareProtected(permissions.view_issue_dealer, 'get_published_categories')
    def get_published_categories(self):
        """Returns a sequence of (id, title) pairs with published issues."""
        categories = []
        for item in self.get_published_issues():
            if self.show_path:
                title = item['issue'].render_breadcrumbs(hyperlink=0, html=0)
            else:
                title = item['issue'].title
            categories.append((item['issue'].id, title))
        return categories

    security.declareProtected(permissions.view_issue_dealer, 'render_category_widget')
    def render_category_widget(self):
        """Renders a category widget."""
        html = "<select name='category'>"
        for id, title in self.get_published_categories():
            html += "<option value='%s'>%s</option>" % (id, title)
        return html + "</select>"

    security.declareProtected(permissions.add_edit_issues_and_relations, 'add_issue')
    def add_issue(self, issue, title, contents):
        """Adds a new issue under published issue."""
        try:
            self.get_objects(relation=issue).manage_add_issue(title=title, contents=contents)
        except IndexError: raise 'Unauthorized'

    def _update(self):
	pass

InitializeClass(category_publisher)

from Products.IssueDealer.issue_dealer import issue_dealer, base

issue_dealer.manage_add_category_publisher_edit = manage_add_category_publisher_edit
issue_dealer.all_meta_types = issue_dealer.all_meta_types + [
    {'visibility': 'Global',
     'interfaces': [],
     'action': 'manage_add_category_publisher_edit',
     'permission': 'Add Category publisher',
     'name': 'Category publisher',
     'product': 'Issue Dealer',
     'instance': ''},]
IssueDealer.add_publisher(category_publisher, manage_add_category_publisher_edit)

