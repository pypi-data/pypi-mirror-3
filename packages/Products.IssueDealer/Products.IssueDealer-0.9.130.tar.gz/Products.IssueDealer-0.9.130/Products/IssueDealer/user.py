from Globals import Persistent, InitializeClass, DTMLFile
import OFS
import Acquisition
from AccessControl import ClassSecurityInfo, Role
from Products import ZCatalog
import cgi, mixins, permissions

class preferences(
    mixins.catalog,
    ZCatalog.CatalogPathAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    Role.RoleManager,
    ): 
    """A class for managing user-preferences."""

    title = meta_type = 'Preferences'
    security = ClassSecurityInfo()
    email = ''
    show_remote = 1
    show_marked_issues = 1
    show_shortcuts_in_tree_view = 0
    show_issue_details = 0
    issue_dealer_session = None
    search_owner_default = 'all'
    security.declarePrivate('set')
    issue_contents_size = 0
    sort_on = 'get_state_importance_title_sort'
    sort_order = ''
    show_tree_order = 1
    issue_format = 'text'
    last_visit = None
    notify_session_new = 1
    notify_owned_new = 1
    notify_session_changed = 1
    notify_owned_changed = 1
    textarea_height = 15
    textarea_width = 72
    html_editor_height = 300
    html_editor_width = 600
    show_tree_outline = 0
    link_category_level = 3
    use_iframe = 0
    show_tags = 1
    show_owned_calendar = 1
    notify_past_due = 1

    # View preferences
    show_issue_attributes = ('tags', 'owner', 'modified')

    security.declarePrivate('set')
    def set(self, name, value):
        exec("self.%s = value" % name)

    security.declareProtected(permissions.view_issue_dealer, 'has_messages')
    def has_messages(self):
        """Returns true if self has messages."""
        if hasattr(self.aq_base, 'messages') and \
          self.messages:
            return 1

    security.declarePrivate('add_message')
    def add_message(self, message, level=100):
        """Adds a message for the user."""
        if not hasattr(self, 'messages'):
            self.messages = []
        self.messages.append((message, level))
        self.messages = self.messages

    security.declareProtected(permissions.view_issue_dealer, 'make_messages')
    def make_messages(self):
        """Creates messages, and deletes from the queue."""
        if not hasattr(self, 'messages'):
            self.messages = []
        if self.messages:
            html = '<div id="messages">'
            try:
                for message in self.messages:
                    if str(message[1])[0] == '2':
                        html += '<p class="green">' + cgi.escape(message[0]) + '</p>'
                    elif str(message[1])[0] in ('4', '5'):
                        html += '<p class="red">' + cgi.escape(message[0]) + '</p>'
                    else:
                        html += '<p>' + cgi.escape(message[0]) + '</p>'
                self.messages = []
                return html + '</div>'
            except KeyError:
                print 'KeyError in make messages'
                return ""
            except AttributeError:
                print 'AttributeError in make messages'
                return ""
        else:
            return ""

    # Hack needed for ZCatalog indexing, for some reason,
    # methods are inherited from the containing object
    # when indexing.
    get_number_of_issues = get_issues = lambda x: None

    def __init__(self, id=None, owner=None):
        self.id = id
        self.owner_ = owner
        # Various settings
        self.show_all = 0
        self.show_type = 0
        self.show_contents = 0
        self.show_issue_details = 0
        self.show_remote_help = 1
        self.show_deleted = 0
        self.show_contents = 0
        self.show_all_search_widgets = 0
        # The session the user is currently using
        self.issue_dealer_session = None
        # Whether to show add, edit, etc. in the
        # tree view
        self.show_shortcuts_in_tree_view = 0
        self.messages = []

InitializeClass(preferences)
