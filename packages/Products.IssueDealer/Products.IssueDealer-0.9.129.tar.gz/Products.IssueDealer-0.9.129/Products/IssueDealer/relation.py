from Globals import Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
from DateTime import DateTime
import base, mixins
from App.config import getConfiguration
import importers
import functions
from cgi import escape
import permissions
from Products.IssueDealer import issue_dealer_globals

def manage_add_relation(self, id=None, relation_='', title='',
                        referrer='', index=1, REQUEST=None):
    """Add an Relation."""
    if id is None:
        id = self.get_unique_id()
    relation_ = relation(id, relation_, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id())
    self._setObject(id, relation_)
    relation_ = self[id]
    relation_.version = self.get_issue_dealer().filesystem_version
    if index:
        try:
            relation_.index_object()
        except AttributeError:
            pass
    if referrer and REQUEST is not None:
        REQUEST.RESPONSE.redirect(referrer)
    else:
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)
        else:
            # To get the object in a context
            return self[id]

class relation(
    mixins.catalog,
    ZCatalog.CatalogPathAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    importers.importers,
    ): 
    """Relation class.

    An relation relates two issues, and may contain
    issues related to the relationship.
    """

    version = (0,9,70)
    meta_type = 'Relation'
    created = DateTime("2003/01/01")
    publisher = 0
    dependency = None
    dependency_type = None

    # Needed for cutting and pasting objects.
    all_meta_types = [
        {'visibility': 'Global',
         'interfaces': [],
         'action': 'manage_add_issue',
         'permission': 'Add Issue',
         'name': 'Issue',
         'product': 'Issue Dealer',
         'instance': ''}
    ]

    manage_options = (OFS.Folder.Folder.manage_options[0],) + \
        (
            {'label': 'View',       'action': ''},
            {'label': 'Security',   'action': 'manage_access'},
        )

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(permissions.view_issue_dealer,
      'index_html', 'get_title')
    security.declareProtected(permissions.add_edit_issues_and_relations,
      'manage_add_issue', 'edit')
    instance_home = getConfiguration().instancehome
    index_html = PageTemplateFile('skins/issue_dealer/issue_dealer_relation_index.pt', issue_dealer_globals)
    manage_add_relation = manage_add_relation
    edit = PageTemplateFile('skins/issue_dealer/issue_dealer_relation_edit.pt', issue_dealer_globals)

    def __init__(self, id, relation, title='', creator='', owner=''): 
        """Initialise a new instance of Relation"""
        self.id = id
        self.relation = relation
        self.title = title
        self.creator = creator or 'unknown'
        self.owner_ = owner or 'unknown'
        self.modified = self.created = DateTime()
        self.order = []

    security.declareProtected(permissions.view_issue_dealer, 'get_related_object')
    def get_related_object(self):
        """Returns the related object."""
        return functions.get_related_object(self)

    security.declareProtected(permissions.view_issue_dealer, 'get_remote_object')
    def get_remote_object(self, issue):
        """Returns the remotely related object."""
        if self.relation == issue.id:
            object = self.get_object(self.getParentNode().id)
            if not object:
                raise 'Error', 'object is None'
        else:
            try:
                object = self.get_object(self.relation)
            except IndexError:
                object = self.get_object('missing')
        return object

    security.declareProtected(permissions.view_issue_dealer, 'get_depended_issue')
    def get_depended_issue(self):
        """Returns the issue depended upon."""
	if self.dependency_type == 'remote':
	    return self.get_related_object()
	else:
	    return self.getParentNode()

    security.declareProtected(permissions.view_issue_dealer, 'render_dependency')
    def render_dependency(self, issue_id, lowercase=0):
	" "
        status = ""
	if self.dependency_type == 'remote':
	    related = self.get_related_object()
            if issue_id == related.id:
                status = 'Depended upon'
            else:
                status = 'Depends upon'
        else:
	    related = self.get_related_object()
            if issue_id != related.id:
                status = 'Depended upon'
            else:
                status = 'Depends upon'
	if lowercase:
	    status = status.lower()
	return status
        
    security.declareProtected(permissions.add_edit_issues_and_relations, 'manage_edit')
    def manage_edit(self, title, dependency=0, dependency_type='remote'):
        """Updates the object with new values."""
        self.title = title
        self.modified = DateTime()
        self.index_object()
	if dependency:
	    self.dependency = 1
	    self.dependency_type = dependency_type
	else:
	    self.dependency = 0
	    self.dependency_type = None
        self.REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declarePrivate('get_all_text')
    def get_all_text(self):
        """Returns all text on the object."""
        return self.title

    def manage_add_issue(self, id=None, title='', contents='',
		state='', referrer='', format=None,
		creator=None, REQUEST=None):
        " "
        import issue
        issue.manage_add_issue(self, id=id, title=title, contents=contents,
		state=state, referrer=referrer, format=format,
		creator=creator, REQUEST=REQUEST)

    def manage_add_issue_edit(self, id=None, title='', contents='', referrer='',
                          state='', REQUEST=None):
        " "
        import issue
        issue.manage_add_issue_edit(self, id=id, title=title, contents=contents,
		referrer=referrer, state=state, REQUEST=REQUEST)

    def _update(self):
	pass

    def _export(self, export):
        """Exports the relation as XML."""
        export.write("""<relation id="%s" creator="%s" owner="%s" modified="%s" relation="%s">""" % \
                 (self.id, self.creator, self.owner_, self.modified, self.relation))
        export.write("""<title>%s</title>""" % escape(self.title))
        export.write("""<order>%s</order>""" % ','.join(self.order))
	if self.dependency:
	    export.write("""<dependency_type>%s</dependency_type>""" % self.dependency_type)
        for issue_or_relation in self.get_objects(meta_type=['Issue', 'Relation']):
            issue_or_relation._export(export)
        export.write("""</relation>\n""")

InitializeClass(relation)
