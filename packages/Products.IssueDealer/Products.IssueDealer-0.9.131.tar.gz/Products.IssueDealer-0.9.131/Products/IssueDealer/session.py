from Globals import DTMLFile, Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
import base
import utilities, mixins
import permissions

def manage_addSession(self, id=None, title='', REQUEST=None):
    """Add a Session."""
    if id is None:
        id = self.get_unique_id()
    session_ = session(id, creator=self.get_user().get_id(),
                       title=title)
    self._setObject(id, session_)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return session_

class session(
    mixins.catalog,
    ZCatalog.CatalogPathAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    ): 
    """Session class.

    A session is a period devoted to a particular activity.
    """

    title = 'No title'
    meta_type = 'Session'
    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(permissions.view_issue_dealer, 'index_html', 'get_title')
    index_html = PageTemplateFile('skins/issue_dealer/issue_dealer_session_index.pt', globals())
    security.declareProtected(permissions.view_issue_dealer, 'edit')
    edit = PageTemplateFile('skins/issue_dealer/issue_dealer_session_edit.pt', globals())
    security.declareProtected(permissions.view_issue_dealer, 'relate')
    relate = PageTemplateFile('skins/issue_dealer/issue_dealer_session_relate.pt', globals())

    security.declareProtected(permissions.add_edit_issues_and_relations, 'relate_submit')
    def relate_submit(self, REQUEST, redirect=1):
        """Relates issues."""
        issue = self.get_object(self.REQUEST['issue']).getObject()
	relation = None
        if REQUEST.has_key('ids'):
            ids = REQUEST['ids']
            titles = REQUEST['titles']
            for index in range(len(ids)):
                relation = issue.manage_add_relation(relation_=ids[index],
                                         title=titles[index])
	if redirect:
            REQUEST.RESPONSE.redirect(issue.get_admin_url())
	else:
	    return relation

    security.declareProtected(permissions.add_edit_issues_and_relations, 'relate_submit_edit')
    def relate_submit_edit(self, REQUEST):
        """Relates issues."""
	relation = self.relate_submit(REQUEST, redirect=0)
	REQUEST.RESPONSE.redirect(relation.get_edit_url())

    security.declareProtected(permissions.view_issue_dealer, 'manage_edit')
    def manage_edit(self, title):
        """Updates the object with new values."""
        self.title = title
        self.index_object()
        self.REQUEST.RESPONSE.redirect(self.get_admin_url())

    def __init__(self, id, creator=None, title=''):
        self.id = id
        self.marks = []
        self.creator = creator or 'unknown'
        self.title = title
        self.users = []
        self.index_object()

    security.declarePrivate('add_marks')
    def add_marks(self, ids):
        """Adds the given marks to self.marks."""
        changed = 0
        if type(ids) is type(''):
            ids = [ids]
        for id in ids:
            if id not in self.marks:
                changed = 1
                self.marks.append(id)
        if changed:
            self.marks = self.marks
            self.index_object()

    security.declareProtected(permissions.view_issue_dealer, 'get_marked_objects')
    def get_marked_objects(self):
        """Returns the marked objects."""
        if self.marks:
            return self.catalog_search(id=self.marks,
                                sort_on=self.get_user_preferences().sort_on,
				sort_order=self.get_user_preferences().sort_order)
        else:
            return []

    security.declareProtected(permissions.view_issue_dealer, 'remove')
    def remove(self, ids=[], referrer=None, REQUEST=None):
        """Remove the marks specified."""
        for id in ids:
            self.marks.remove(id)
        self.marks = self.marks
        self.index_object()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declarePrivate('add_user')
    def add_user(self, username):
        """Adds the user to the session."""
        if username in self.users:
            utilities.log("Would've added %s to %s" % (username, self.users))
        else:
            self.users.append(username)
            self.users = self.users

    security.declarePrivate('remove_user')
    def remove_user(self, username):
        """Removes the user from the session."""
        try:
            self.users.remove(username)
        except ValueError:
            pass
        self.users = self.users

    security.declarePrivate('update')
    def update(self):
        """Updates the session"""
        if not hasattr(self.aq_base, 'users'):
            self.users = []
        self.index_object()

    security.declareProtected(permissions.view_issue_dealer, 'render_html_title_and_link')
    def render_html_title_and_link(self, size=None):
        """Renders a link to the session."""
        title = self.get_title()
        return self.create_hyperlink(self.absolute_url(), title, size=size)

    security.declareProtected(permissions.view_issue_dealer, 'render_join_link')
    def render_join_link(self, title='Join session'):
        """Renders a link, used to join the session."""
        return self.create_hyperlink(self.absolute_url() + '/join',
                                     title)

    security.declareProtected(permissions.view_issue_dealer, 'join')
    def join(self, REQUEST=None):
        """Lets the user join the session."""
        if self.get_session().id == self.id:
            return
        self.get_session().remove_user(self.get_user().get_id())
        self.add_user(self.get_user().get_id())
        self.get_user_preferences().issue_dealer_session = self.id
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())

InitializeClass(session)
