from Globals import Persistent, InitializeClass, DTMLFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
from cgi import escape
import string
from DateTime import DateTime
import session_manager, base, user, mixins
import permissions

def manage_add_filter(self, REQUEST):
    """Add a filter."""
    try:
        id = REQUEST['id']
    except KeyError:
        id = None
    if id is None:
        id = self.get_unique_id()
    filter_ = filter(id, title=REQUEST['title'],
                     search_string=REQUEST['search_string'],
                     tags=REQUEST['tags'],
                     states=REQUEST['states'],
                     owner=REQUEST['owner'],
                     path=REQUEST['path'],
                     sort_type=REQUEST['sort_type'],
                     relative_state=REQUEST['relative_state'])
    self._setObject(id, filter_)
    filter_ = self._getOb(id)
    try:
        self.index_object()
    except AttributeError:
        pass

user.preferences.manage_add_filter = manage_add_filter

class filter(
    mixins.catalog,
    ZCatalog.CatalogPathAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,    
    ): 
    """Filter."""

    security = AccessControl.ClassSecurityInfo()

    meta_type = 'Filter'
    index_html = PageTemplateFile('skins/issue_dealer/issue_dealer_filter_index.pt', globals())
    relative_state = 0
    tags = ""

    def __init__(self, id, title='',
                 search_string='',
                 states=[], owner=[], path='',
                 sort_type='', tags='', relative_state=0):
        self.id = id
        self.title = title
        self.search_string = search_string
        self.states = states
        self.owner = owner
        self.path = path
        self.sort_type = sort_type
        self.relative_state = relative_state
        self.tags = tags

    security.declareProtected(permissions.view_issue_dealer, 'get_title')

    security.declareProtected(permissions.view_issue_dealer, 'update_request')
    def update_request(self, path, REQUEST):
        """Updates the REQUEST with search values."""
        REQUEST['search_string'] = self.search_string
        REQUEST['states'] = self.states
        REQUEST['owner'] = self.owner
        if not self.path:
            REQUEST['path'] = path
        REQUEST['sort_type'] = self.sort_type
        REQUEST['relative_state'] = self.relative_state
        REQUEST['tags'] = self.tags

    security.declareProtected(permissions.view_issue_dealer, 'render_states')
    def render_states(self):
        return ', '.join(map(lambda x: x.capitalize(), self.states))

    security.declareProtected(permissions.view_issue_dealer, 'render_relative_state')
    def render_relative_state(self):
        if self.relative_state:
            return 'Yes'
        else:
            return 'No'

    security.declareProtected(permissions.view_issue_dealer, 'render_owners')
    def render_owners(self):
        return ', '.join(map(lambda x: x.capitalize(), self.owner))

    security.declareProtected(permissions.view_issue_dealer, 'render_path')
    def render_path(self):
        return self.path

    security.declareProtected(permissions.view_issue_dealer, 'render_tags')
    def render_tags(self):
        return self.tags

    def _update(self):
        if not hasattr(self.aq_base, 'tags'):
            self.tags = ''
            for type in self.types:
                self.tags += 'issue-type:' + type + '\n'
            del self.types

InitializeClass(filter)