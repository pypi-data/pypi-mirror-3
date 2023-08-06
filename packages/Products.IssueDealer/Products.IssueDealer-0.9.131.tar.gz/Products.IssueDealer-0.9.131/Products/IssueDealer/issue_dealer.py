from Globals import DTMLFile, MessageDialog, Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
import base, issue, time, session_manager, session_folder, mixins, utilities
from App.config import getConfiguration
import DateTime
import smtplib
import id_config
import importers
import functions
from cgi import escape
import permissions
import issue_dealer_catalog, issue_dealer_notifications
import laf_root
from Products.laf import laf

manage_add_issue_dealer_form = PageTemplateFile('skins/issue_dealer/issue_dealer_add.pt', globals()) 

def manage_add_issue_dealer(self, id, title='', running_tests=0, REQUEST=None):
    """Add an Issue Dealer."""
    self._setObject(id, issue_dealer(id, title))
    self._getOb(id).public_url = self.absolute_url() + '/' + id
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

class issue_dealer(
    mixins.catalog,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,
    importers.importers,
    issue_dealer_catalog.issue_dealer_catalog,
    issue_dealer_notifications.issue_dealer_notifications,
    ): 
    """Issue Dealer class. 

    An issue dealer contains Issues.
    """

    renaming = 0
    meta_type = 'Issue Dealer'
    deleted = 0
    publishers_ = []
    gateways_ = []
    public_url = ''
    state = 'open'
    type = 'info'
    owner_ = 'unknown'
    creator = 'unknown'

    last_notification_check = None

    access_level_add_edit = 'private'
    access_level_manage = 'private'
    access_level_viewing = 'private'
    access_level_publish = 'private'

    filesystem_version = (0,9,110)

    manage_options = (OFS.Folder.Folder.manage_options[0],) + \
        (
            {'label': 'View',       'action': ''},
            {'label': 'Security',   'action': 'manage_access'},
        ) 

    # Needed for cutting and pasting objects.
    all_meta_types = [
        {'visibility': 'Global',
         'interfaces': [],
         'action': 'manage_add_issue',
         'permission': 'Add Issues',
         'name': 'Issue',
         'product': 'Issue Dealer',
         'instance': ''},
        {'visibility': 'Global',
         'interfaces': [],
         'action': 'manage_add_local_weblog_publisher_edit',
         'permission': 'Add Issues',
         'name': 'Local weblog publisher',
         'product': 'Issue Dealer',
         'instance': ''},
        {'visibility': 'Global',
         'interfaces': [],
         'action': '',
         'permission': permissions.manage_issue_dealer,
         'name': 'Session Folder',
         'product': 'Issue Dealer',
         'instance': ''},
        {'visibility': 'Global',
         'interfaces': [],
         'action': '',
         'permission': permissions.manage_issue_dealer,
         'name': 'Preferences',
         'product': 'Issue Dealer',
         'instance': ''}        
    ]

    security = AccessControl.ClassSecurityInfo()
    security.declareProtected(permissions.view_issue_dealer,
	'index_html', 'javascript', 'css')
    index_html = PageTemplateFile('skins/issue_dealer/issue_dealer_product_index.pt', globals())
    edit = PageTemplateFile('skins/issue_dealer/issue_dealer_edit.pt', globals())
    javascript = DTMLFile('skins/issue_dealer/issue_dealer.js', globals())
    css = DTMLFile('skins/issue_dealer/issue_dealer.css', globals())
    security.declareProtected(permissions.add_edit_issues_and_relations, 'manage_add_issue')
    manage_add_issue = issue.manage_add_issue
    security.declareProtected(permissions.add_edit_issues_and_relations, 'manage_add_issue_edit')
    manage_add_issue_edit = issue.manage_add_issue_edit

    optional_issue_attributes = ('tags', 'importance', 'state', 'owner', 'modified', 'order')

    security.declareProtected(permissions.manage_issue_dealer, 'setup_laf')
    def setup_laf(self):
        "Sets up the Lightweight application framework class"
        self._setObject('laf', laf.laf('laf'))

    def manage_afterAdd(self, *a, **k):
        self.setup_laf(self)

    security.declareProtected(permissions.view_issue_dealer, 'has_absolute_url')
    def has_absolute_url(self):
        """Returns a truth value if we have a http(s):// url."""
        if self.absolute_url().find('://') > -1: return 1
        elif self.public_url.find('://') > -1: return 1
        else: return 0

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'get_custom_absolute_url')
    def get_custom_absolute_url(self):
        """Returns an absolute url."""
        if self.absolute_url().find('://') > -1: return self.absolute_url()
        else: return self.public_url

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'style')
    def style(self):
        """Returns stylesheet data."""
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/css')
        return self.css()

    security.declareProtected(permissions.view_issue_dealer, 'get_issue_dealer')
    def get_issue_dealer(self):
        """Returns self."""
        return self

    def __init__(self, id, title='Issues'):
        self.id = id
        self.title = title
        ZCatalog.ZCatalog.manage_addZCatalog(self, 'Catalog', 'Issue catalog')
        self.add_indexes()
        self.add_columns()
        self._add_session_folder()
        self.order = []

    security.declareProtected(permissions.manage_issue_dealer, 'manage_edit')
    def manage_edit(self, title='', public_url='', REQUEST=None):
        """Edits the Issue Dealer."""
        self.title = title
        self.public_url = public_url.strip() or self.absolute_url()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/index_html')        

    security.declareProtected(permissions.view_issue_dealer, 'get_issue_states')
    def get_issue_states(self):
        """Returns a tuple of Issue states."""
        return ('open', 'closed', 'discarded', 'suspended')

    security.declareProtected(permissions.view_issue_dealer, 'get_issue_types')
    def get_issue_types(self):
        """Returns a tuple of Issue types."""
        return ('goal', 'idea', 'info',
                'problem', 'question', 'solution')

    security.declareProtected(permissions.view_issue_dealer, 'get_importance_levels')
    def get_importance_levels(self):
        """Returns a sequence of importance levels."""
        return ((0, 'low'), (1, 'normal'), (2, 'high'))

    security.declareProtected(permissions.view_issue_dealer, 'get_object')
    def get_object(self, id):
        """Returns the object specified by id."""
        return functions.get_object(self, id)

    # Untested
    def _add_session_folder(self):
        if hasattr(self, 'aq_base'):
            if hasattr(self.aq_base, 'sessions'): return
        session_folder.manage_addSessionFolder(self, id='sessions')

    security.declareProtected(permissions.view_issue_dealer, 'r')
    def r(self, i):
        """Redirects to the specified Issue."""
        issue = self.get_object(id=i).getObject()
        self.REQUEST.RESPONSE.redirect(issue.absolute_url())

    security.declareProtected(permissions.view_issue_dealer, 'get_title')
    def get_title(self):
        """Returns a descriptive title."""
        if self.title:
            title = self.title
        else:
            title = self.meta_type
        return title

    security.declareProtected(permissions.view_issue_dealer, 'get_publishers')
    def get_publishers(self):
        """Returns a sequence of available publishers."""
        types = ['Local weblog publisher', 'Weblog publisher', 'FAQ publisher', 'WebDAV publisher', 'Category publisher']
        return self.get_issue_dealer().objectValues(types)

    security.declareProtected(permissions.view_issue_dealer, 'get_gateways')
    def get_gateways(self):
        """Returns a sequence of available gateways."""
        types = ['Mail gateway']
        return self.get_issue_dealer().objectValues(types)

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'get_gateway_types')
    def get_gateway_types(self, REQUEST=None):
        """Returns a sequence of dictionaries, describing available gateways."""
        return self.gateways_

    security.declareProtected(permissions.view_issue_dealer, 'get_tree_publishers')
    def get_tree_publishers(self):
        """Returns a sequence of available tree publishers."""
        types = ['Tree publisher']
        return self.get_issue_dealer().objectValues(types)

    security.declareProtected(permissions.view_issue_dealer, 'get_action_issue_types')
    def get_action_issue_types(self):
        " "
        return ('goal', 'idea', 'problem', 'question')

    def _export(self, export):
        """Exports the issue as XML."""
        export.write("""<issue id="%s" format="%s" creator="%s" owners="%s" state="%s" modified="%s">""" % \
                 (str(float(DateTime.DateTime())).replace('.', 'X'), 'text', self.creator, self.owner_, self.state, DateTime.DateTime()))
        export.write("""<title>%s</title>""" % escape(self.title))
        export.write("""<contents>%s</contents>""" % "")
        export.write("""<order>%s</order>""" % ','.join(self.order))
        for issue_or_relation in self.get_objects(meta_type=['Issue', 'Relation']):
            issue_or_relation._export(export)
        return export.write("""</issue>""")

    def change_state(*arguments, **keywords):
        pass

InitializeClass(issue_dealer)
