from Globals import DTMLFile, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import string
from OFS.CopySupport import cookie_path, _cb_decode
import AccessControl
import utilities
from Products.laf import url_utilities
from cgi import escape
import urllib, time
from DateTime import DateTime
import user
from App.config import getConfiguration
import tempfile
import permissions as id_permissions
from Products.IssueDealer import issue_dealer_globals
import id_config
import cStringIO
from Products.laf.utilities import get_parents
import laf_mixin
from Products.laf import laf_base

import base_sequence, base_search, base_browse, base_tree, base_placement, \
	base_publish, base_utilities, base_calendar

class base(
	base_sequence.base_sequence,
	base_search.base_search,
	base_browse.base_browse,
	base_tree.base_tree,
	base_placement.base_placement,
	base_publish.base_publish,
	base_calendar.base_calendar,
        laf_mixin.laf_mixin,
        laf_base.laf_base,
	):
    """Mixin class used to provide common functionality."""

    version = (0,9,70)
    security = AccessControl.ClassSecurityInfo()
    deleted = 0
    due = None
    last_modified_by = None

    security.declareProtected(id_permissions.view_issue_dealer, 'search', 'search_advanced',
                              'issue_tree', 'settings', 'filters', 'rdf', 'issue_calendar', 'issue_calendar_past_due')
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'rename', 'rename_submit', 'issue_multi_add',
	'relation_add', 'locate_issue_javascript', 'change_tags', 'change_tags_submit')
    security.declareProtected(id_permissions.manage_issue_dealer, 'permissions', 'gateways')
    security.declareProtected(id_permissions.publish_issues, 'publish',
	'publishers', 'publish_multiple_submit')
    security.declarePublic('issue_dealer_template', 'optional_issue_attributes', 'standard_error_message')

    instance_home = getConfiguration().instancehome
    search = PageTemplateFile('skins/issue_dealer/issue_dealer_search.pt', issue_dealer_globals)
    search_advanced = PageTemplateFile('skins/issue_dealer/issue_dealer_search_advanced.pt', issue_dealer_globals)
    issue_tree = PageTemplateFile('skins/issue_dealer/issue_dealer_tree.pt', issue_dealer_globals)
    issue_calendar = PageTemplateFile('skins/issue_dealer/issue_dealer_calendar.pt', issue_dealer_globals)
    issue_calendar_past_due = PageTemplateFile('skins/issue_dealer/issue_dealer_calendar_past_due.pt', issue_dealer_globals)
    settings = PageTemplateFile('skins/issue_dealer/issue_dealer_settings.pt', issue_dealer_globals)
    permissions = PageTemplateFile('skins/issue_dealer/issue_dealer_permissions.pt', issue_dealer_globals)
    filters = PageTemplateFile('skins/issue_dealer/issue_dealer_filters.pt', issue_dealer_globals)
    publish = PageTemplateFile('skins/issue_dealer/issue_dealer_publish.pt', issue_dealer_globals)
    publishers = PageTemplateFile('skins/issue_dealer/issue_dealer_publishers.pt', issue_dealer_globals)
    gateways = PageTemplateFile('skins/issue_dealer/issue_dealer_gateways.pt', issue_dealer_globals)
    about = PageTemplateFile('skins/issue_dealer/issue_dealer_about.pt', issue_dealer_globals)
    issue_dealer_template = PageTemplateFile('skins/issue_dealer/issue_dealer_template.pt', issue_dealer_globals)
    session_template = PageTemplateFile('skins/issue_dealer/issue_dealer_session_template.pt', issue_dealer_globals)
    session_index = PageTemplateFile('skins/issue_dealer/issue_dealer_session_index.pt', issue_dealer_globals)
    session_folder_index = PageTemplateFile('skins/issue_dealer/issue_dealer_session_folder_index.pt', issue_dealer_globals)
    session_edit = PageTemplateFile('skins/issue_dealer/issue_dealer_session_edit.pt', issue_dealer_globals)
    session_relate = PageTemplateFile('skins/issue_dealer/issue_dealer_session_relate.pt', issue_dealer_globals)
    select_link_category = PageTemplateFile('skins/issue_dealer/issue_dealer_select_link_category.pt', issue_dealer_globals)
    publish_multiple = PageTemplateFile('skins/issue_dealer/issue_dealer_publish_multiple.pt', issue_dealer_globals)
    rename = PageTemplateFile('skins/issue_dealer/issue_dealer_rename.pt', issue_dealer_globals)
    rdf = PageTemplateFile('skins/issue_dealer/issue_dealer_rdf.pt', issue_dealer_globals)
    issue_multi_add = PageTemplateFile('skins/issue_dealer/issue_dealer_multi_add.pt', issue_dealer_globals)
    relation_add = PageTemplateFile('skins/issue_dealer/issue_dealer_relation_add.pt', issue_dealer_globals)
    locate_issue_javascript = PageTemplateFile('skins/issue_dealer/issue_dealer_locate_issue_javascript.pt', issue_dealer_globals)
    change_tags = PageTemplateFile('skins/issue_dealer/issue_dealer_change_tags.pt', issue_dealer_globals)
    standard_error_message = PageTemplateFile('skins/issue_dealer/standard_error_message.pt', issue_dealer_globals)

    security.declarePublic('get_response')
    def get_response(self):
        ""
        return self.REQUEST.RESPONSE

    security.declareProtected(id_permissions.view_issue_dealer, 'get_request')
    def get_request(self):
        ""
        return self.REQUEST

    security.declareProtected(id_permissions.view_issue_dealer, 'get_self')
    def get_self(self):
        """Returns self."""
        return self

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'rename_submit')
    def rename_submit(self, ids, titles):
        """Renames a group of issues."""
        for index in range(len(ids)):
            issue = self.get_object(ids[index]).getObject()
            issue.title = titles[index]
            issue.index_object()
        self.get_response().redirect(self.get_admin_url())

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'change_tags_submit')
    def change_tags_submit(self, ids, add_tags, remove_tags):
        """Re-tags a group of issues."""
        add_tags = map(lambda x: x.strip().replace(',', ':'), cStringIO.StringIO(add_tags).readlines())
        remove_tags = map(lambda x: x.strip().replace(',', ':'), cStringIO.StringIO(remove_tags).readlines())
        for index in range(len(ids)):
            try:
                issue = self.get_object(ids[index]).getObject()
            except IndexError: pass
            issue.add_tags(add_tags)
            issue.remove_tags(remove_tags)
            issue.index_object()
        self.get_response().redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'manage_cut')
    def manage_cut(self, ids=None):
        """Cuts selected objects."""
        copy_data = self.manage_cutObjects(ids=ids)
        self.REQUEST.RESPONSE.setCookie('__cp', copy_data,
                                        path='%s' % cookie_path(self.REQUEST))
        self.REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'manage_paste')
    def manage_paste(self):
        """Pastes cut objects."""
        # Move the objects and reindex old and new
        # parent and the moved objects.
        cb = _cb_decode(self.REQUEST['__cp'])
        objects = cb[1]
        ids = map(lambda x: x[-1], objects)
        objects = map(lambda x: string.join(x, '/'), objects)
        objects = map(lambda x, self=self: self.unrestrictedTraverse(x), objects)
        parent = objects[0].getParentNode()
        self.manage_pasteObjects(cb_copy_data=self.REQUEST['__cp'])
        if parent.meta_type != 'Issue Dealer':
            self.modified = DateTime()
            parent.index_object()
        for id in ids:
            self[id].modified = DateTime()
            self[id].index_object()
        if self.meta_type != 'Issue Dealer':
            self.modified = DateTime()
            self.index_object()
        self.REQUEST['RESPONSE'].setCookie('__cp', 'deleted',
                                      path='%s' % cookie_path(self.REQUEST),
                                      expires='Wed, 31-Dec-97 23:59:59 GMT')
        self.REQUEST['__cp'] = None
        self.REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declareProtected(id_permissions.view_issue_dealer, 'inCMF')
    def inCMF(self):
        """Returns a truth value if we're inside the CMF."""
        return 0

    security.declareProtected(id_permissions.view_issue_dealer, 'session_remove')
    def session_remove(self, ids=[], REQUEST=None):
        """Removes specified issues from the session."""
        self.get_session().remove(ids=ids)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(id_permissions.view_issue_dealer, 'session')
    def session(self, REQUEST):
        """Redirects to the Session."""
        REQUEST.RESPONSE.redirect(self.get_session().absolute_url())

    security.declareProtected(id_permissions.view_issue_dealer, 'get_user_preferences')
    def get_user_preferences(self):
        """Returns the user preferences object."""
        try:
            try:
                return self.catalog_search(meta_type='Preferences', owner_=self.get_user().get_id())[0].getObject()
            except (IndexError, KeyError):
		# We might be updating the catalog
                preferences = self.get_issue_dealer().objectValues('Preferences')
                preferences = filter(lambda x, user_id=self.get_user().get_id(): x.owner_ == user_id, preferences)
                if preferences:
                    return preferences[0]
                else:
                    preferences = user.preferences(id=self.get_unique_id(),
                                                   owner=self.get_user().get_id())
                    self.get_issue_dealer()._setObject(preferences.id, preferences)
                    preferences = self.get_issue_dealer()[preferences.id]
                    preferences.index_object()
                    return preferences
        except AttributeError:
            raise
            # Reraise the KeyError
            raise KeyError

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'on_access')
    def on_access(self):
        """Method called each time an object is accessed."""
	if self.get_user().get_id() == None:
            # The user is unknown, don't do anything
            return
        self.handle_session()

    security.declarePublic('create_hyperlink')
    def create_hyperlink(self, *arguments, **keywords):
        """Creates a hyperlink."""
        return url_utilities.create_hyperlink(*arguments, **keywords)

    security.declarePrivate('get_parents')
    def get_parents(self, stop=None):
        """Returns a list of parent objects."""
        if stop is None:
            stop = lambda x: getattr(x, 'meta_type', 'Issue Dealer') == 'Issue Dealer'
        return get_parents(self, stop=stop)

    security.declareProtected(id_permissions.view_issue_dealer, 'render_breadcrumbs')
    # From laf_base

    security.declareProtected(id_permissions.view_issue_dealer, 'render_context_breadcrumbs')    
    def render_context_breadcrumbs(self, separator=' :: '):
        """Renders breadcrumbs based on context, for the search page."""
        parents = self.get_parents()
        breadcrumbs = []
        for parent in parents:
            if parent.meta_type == 'Issue Dealer':
                break
            breadcrumbs.append(self.create_hyperlink(
                parent.get_admin_url(), parent.get_title()))
        breadcrumbs.reverse()
        return string.join(breadcrumbs, separator)

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_title')
    def get_title(self):
        """Returns a descriptive title."""
        if self.title:
            title = self.title
        else:
            title = self.meta_type
        if self.deleted:
            title += " [Deleted] "
        return title

    # Untested
    security.declarePublic('html_quote')
    def html_quote(self, string_):
        """HTML Quotes the given string."""
        return escape(string_)

    security.declarePrivate('get_state_importance_due_sort')
    def get_state_importance_due_sort(self):
        " "
        return ""

    security.declarePrivate('get_filtered_objects')
    def get_filtered_objects(self, meta_type=['Issue', 'Relation'], **keywords):
        """Returns a list of filtered objects."""
        if self.get_user_preferences().show_deleted:
            deleted = [0,1]
        else:
            deleted = 0
        sort_order = self.get_user_preferences().sort_order
        sort_on = self.get_user_preferences().sort_on
        if meta_type in (['Issue'], 'Issue'):
            if not self.get_user_preferences().show_all:
                return self.get_objects(meta_type=meta_type, deleted=deleted,
                    sort_order=sort_order, sort_on=sort_on,
			state=['open', 'suspended'])
        return self.get_objects(meta_type=meta_type, deleted=deleted,
            sort_order=sort_order, sort_on=sort_on)

    security.declarePrivate('get_sorted_objects')
    def get_sorted_objects(self, **keywords):
	if not keywords.has_key('sort_on'):
	    keywords['sort_on'] = self.get_user_preferences().sort_on
	if not keywords.has_key('sort_order'):
            keywords['sort_order'] = self.get_user_preferences().sort_order
        return self.get_objects(**keywords)

    security.declarePrivate('get_objects')
    def get_objects(self, meta_type=['Issue', 'Relation'], **keywords):
        """Returns a list of objects."""
        result = self.catalog_search(
                get_parent_url='/'.join(self.getPhysicalPath()),
                meta_type=meta_type, **keywords)
        return result

    security.declareProtected(id_permissions.view_issue_dealer, 'get_issues')
    def get_issues(self):
        """Returns a list of the Issues contained."""
        return self.get_objects(meta_type='Issue')

    def get_open_suspended(self, meta_type=['Issue', 'Relation']):
        """Returns a list of open or suspended Objects."""
        states = ['open', 'suspended']
        if self.get_user_preferences().show_deleted:
            deleted = [0,1]
        else:
            deleted = 0
        return self.get_objects(state=states, deleted=deleted, meta_type=meta_type)

    security.declareProtected(id_permissions.view_issue_dealer, 'get_open_suspended_issues')
    def get_open_suspended_issues(self):
        """Returns a list of the (non deleted), open or suspended Issues contained."""
        return self.get_open_suspended(meta_type='Issue')

    security.declareProtected(id_permissions.view_issue_dealer, 'get_closed_discarded')
    def get_closed_discarded(self, meta_type=['Issue', 'Relation']):
        """Returns a list of the closed and discarded objects contained."""
        states = ['closed', 'discarded']
        if self.get_user_preferences().show_deleted:
            deleted = [0,1]
        else:
            deleted = 0
        return self.get_objects(state=states, deleted=deleted, meta_type=meta_type)

    security.declareProtected(id_permissions.view_issue_dealer, 'get_closed_discarded_issues')
    def get_closed_discarded_issues(self):
        """Returns a list of the closed and discarded Issues contained."""
        return self.get_closed_discarded(meta_type='Issue')

    security.declareProtected(id_permissions.view_issue_dealer, 'get_deleted_issues')
    def get_deleted_issues(self):
        """Returns a sequence of deleted issues."""
        return self.get_objects(deleted=1, meta_type='Issue')

    security.declareProtected(id_permissions.view_issue_dealer, 'get_deleted_relations')
    def get_deleted_relations(self):
        """Returns a sequence of deleted relations."""
        return self.get_objects(deleted=1, meta_type='Relation')

    security.declareProtected(id_permissions.view_issue_dealer, 'get_number_of_issues')
    def get_number_of_issues(self):
        """Returns the number of Issues contained."""
        return len(self.get_issues())

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'manage_delete')
    def manage_delete(self, ids=[], REQUEST=None):
        """Deletes the specified objects."""
        for id in ids:
	    self[id].delete()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'manage_undelete')
    def manage_undelete(self, ids=[], REQUEST=None):
        """Undeletes the specified objects."""
        for id in ids:
            self[id].undelete()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'mark')
    def mark(self, ids=[]):
        """Marks the given ids or this object."""
        session = self.get_session()
        if ids:
            session.add_marks(ids)
        else:
            session.add_marks(self.id)
        self.REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'unmark')
    def unmark(self, ids=[]):
        """Unmarks the given ids or this object."""
        session = self.get_session()
        if ids:
            session.remove(ids=ids)
        else:
            session.remove(ids=[self.id])
        self.REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declarePrivate('get_parent_url')
    def get_parent_url(self):
        """Returns the parents URL."""
        return '/'.join(self.getParentNode().getPhysicalPath())

    # Untested (see tests for more info)
    security.declareProtected(id_permissions.view_issue_dealer, 'catalog_search')
    def catalog_search(self, *arguments, **keywords):
        """Does a catalog search, returning proxied objects."""
        for key, value in keywords.items():
            if value is None: del keywords[key]
        result = base_utilities.lazy(self.get_catalog()(*arguments, **keywords))
        return result

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_catalog')
    def get_catalog(self):
        """Returns the catalog."""
        return self.Catalog

    # Untested
    security.declarePublic('get_user')
    def get_user(self):
        """Returns a user instance."""
        return utilities.user(self.REQUEST['AUTHENTICATED_USER'], self)

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_modified')
    def render_modified(self):
        """Renders the modification time."""
        return self.modified.strftime(id_config.datetime_format)

    security.declareProtected(id_permissions.view_issue_dealer, 'render_modified_by')
    def render_modified_by(self):
        """Renders the username of the user that last modified the object."""
        return str(self.last_modified_by)

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_due')
    def render_due(self):
        """Renders the due time."""
        if self.due:
            if self.due.hour() or self.due.minute():
                return self.due.strftime(id_config.datetime_format)
            else:
                return self.due.strftime(id_config.date_format)
        else:
            return None

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_created')
    def render_created(self):
        """Renders the creation time."""
        return self.created.strftime(id_config.datetime_format)

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_level')
    def get_level(self):
        """Returns the level (depth) of the object."""
        return len(self.getPhysicalPath())

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_custom_remote_html')
    def get_custom_remote_html(self):
        """Returns custom remote HTML."""
        return ""

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_html_title_and_link')
    def render_html_title_and_link(self, size=None, show_session=1, tree=0):
        """Renders a link."""
        if tree:
            url = self.absolute_url() + '/issue_tree'
        else:
            url = self.get_admin_url()
        return self.create_hyperlink(url, self.get_title())

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'make_message')
    def make_message(self, message):
        """Creates HTML for a message."""
        return """<div id="message">%s</div><br />""" % escape(message)

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'open')
    def open(self, ids=[], REQUEST=None):
        """Opens the specified issues."""
        if not ids:
            issues = [self]
        else:
            issues = map(lambda x, self=self: self.get_object(x), ids)
        for issue in issues:
            if issue.meta_type == 'Relation':
                issue.get_related_object().change_state('open')
            else:
                issue.change_state('open')
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'close')
    def close(self, ids=[], REQUEST=None):
        """Closes the specified issues."""
        if not ids:
            issues = [self]
        else:
            issues = map(lambda x, self=self: self.get_object(x), ids)
        for issue in issues:
            if issue.meta_type == 'Relation':
                issue.get_related_object().change_state('closed')
            else:
                issue.change_state('closed')
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'suspend')
    def suspend(self, ids=[], REQUEST=None):
        """Suspend the specified issues."""
        if not ids:
            issues = [self]
        else:
            issues = map(lambda x, self=self: self.get_object(x), ids)
        for issue in issues:
            if issue.meta_type == 'Relation':
                issue.get_remote_object(self).change_state('suspended')
            else:
                issue.change_state('suspended')
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'discard')
    def discard(self, ids=[], REQUEST=None):
        """Discards the specified issues."""
        if not ids:
            issues = [self]
        else:
            issues = map(lambda x, self=self: self.get_object(x), ids)
        for issue in issues:
            if issue.meta_type == 'Relation':
                issue.get_related_object().change_state('discarded')
            else:
                issue.change_state('discarded')
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_custom_search_remote_html')
    def get_custom_search_remote_html(self):
        """Returns custom HTML to the search interface."""
        return """<input type="text" name="title" size="15" class="remoteTextInput" />
        <input type="hidden" name="referrer" value="%s" />
        <input type="submit" name="save_filter:method" value=" Save filter "
        class="remoteInput" /><br /><br />
        """ % (self.REQUEST['URL'] + ('?' + self.REQUEST['QUERY_STRING']))

    # Untested
    security.declarePrivate('update')
    def update(self):
        if hasattr(self.aq_base, '_update'):
            self._update()

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_custom_settings_html')
    def get_custom_settings_html(self):
        " "
        return ""

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'image')
    def image(self, id=None, REQUEST=None, RESPONSE=None):
        """Returns an image."""
        image = self.get_object(id).getObject()
        return image.index_html(REQUEST, RESPONSE)

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_admin_url')
    def get_admin_url(self):
        """Returns the administrative URL."""
        return self.absolute_url()

    security.declareProtected(id_permissions.view_issue_dealer, 'get_edit_url')
    def get_edit_url(self):
        """Returns the editing URL."""
        return self.absolute_url() + '/edit'

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'create_query_string')
    create_query_string = url_utilities.create_query_string

    security.declareProtected(id_permissions.view_issue_dealer, 'handle_edited_settings')
    def handle_edited_settings(self):
        """Handles edited settings."""
        preferences = self.get_user_preferences()
        request = self.REQUEST
        for key in ('textarea_width', 'textarea_height', 'html_editor_width',
		'html_editor_height', 'issue_format', 'show_issue_details',
		'issue_contents_size', 'sort_on', 'show_deleted',
		'search_owner_default', 'show_shortcuts_in_tree_view', 'show_type',
		'email', 'show_issue_attributes', 'show_contents', 'show_tree_outline',
		'link_category_level', 'notify_session_new', 'notify_owned_new',
		'notify_session_changed', 'notify_owned_changed', 'use_iframe', 'show_tags',
		'show_owned_calendar'):
            try:
                preferences.set(key, request[key])
            except KeyError: pass

    security.declareProtected(id_permissions.view_issue_dealer, 'handle_settings_redirect')
    def handle_settings_redirect(self):
        """Handles redirects for the settings page."""
        if self.REQUEST.has_key('save_and_view'):
            self.REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(id_permissions.view_issue_dealer, 'handle_notifications_redirect')
    def handle_notifications_redirect(self):
        """Handles redirects for the notifications page."""
        if self.REQUEST.has_key('save_and_view'):
            self.REQUEST.RESPONSE.redirect(self.absolute_url())

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_possible_issue_types')
    def get_possible_issue_types(self, object=None):
        """Returns the issue types that could be contained in object."""
        if object is None:
            object = self
        try:
            type = object.get_type()
        except AttributeError: # It's the Issue Dealer instance
            type = None
        if type in ('goal', 'problem', 'question'):
            return ('goal', 'idea',
                    'info', 'problem', 'question', 'solution')
        else:
            return ('goal', 'idea', 'info', 'problem', 'question')

    security.declareProtected(id_permissions.view_issue_dealer, 'handle_issue_listing')
    def handle_issue_listing(self):
        """Handles issue listing related things."""
        object = self
	if self.REQUEST.has_key('show_all'):
            if self.REQUEST['show_all'] == 'More..':
		self.get_user_preferences().set('show_all', 1)
	    else:
		self.get_user_preferences().set('show_all', 0)
        if self.get_user_preferences().show_all:
	    self.REQUEST.set('issues', object.get_filtered_objects(meta_type='Issue'))
        else:
	    self.REQUEST.set('issues', object.get_filtered_objects(meta_type='Issue', state=['open', 'suspended']))
        try:
            relations = object.get_all_relations()
	    self.REQUEST.set('relations', relations)
        except NameError:
	    self.REQUEST.set('relations', [])
        except AttributeError:
	    self.REQUEST.set('relations', [])

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'submit_link')
    def submit_link(self, url, title, parent, REQUEST):
        """Stores a link."""
        if parent == 'issue_dealer':
            parent = self.get_issue_dealer()
        else:
            parent = self.get_object(parent)
        issue = parent.manage_add_issue()
        issue.format = 'text'
        issue.manage_edit(contents=url, title=title, tags='info')
        return """<html><body onload="window.close();"></body></html>"""

    security.declarePublic('get_permission_states')
    def get_permission_states(self):
        " "
        return ('private', 'shared', 'public')

    security.declareProtected(id_permissions.manage_issue_dealer, 'permissions_update')
    def permissions_update(self):
        """Updates id_permissions."""
        request = self.get_request()
        for access_level, permission in (
		('access_level_add_edit', id_permissions.add_edit_issues_and_relations),
		('access_level_manage',  id_permissions.manage_issue_dealer),
		('access_level_viewing', id_permissions.view_issue_dealer),
		('access_level_publish', id_permissions.publish_issues)
	):
            exec("self.%s = request[access_level]" % access_level)
            if request[access_level] == 'private':
                self.manage_permission(permission, roles=['Owner'])
            if request[access_level] == 'shared':
                self.manage_permission(permission, roles=['Authenticated'])
            if request[access_level] == 'public':
                self.manage_permission(permission, roles=['Anonymous'])
        self.get_user_preferences().add_message('Updated permissions')
        self.get_response().redirect('./permissions')

    security.declareProtected(id_permissions.view_issue_dealer, 'get_relations')
    def get_relations(self):
        """Returns a list containing relations."""
        if self.get_user_preferences().show_deleted:
            deleted = [0,1]
        else:
            deleted = 0
        r = self.get_objects(meta_type='Relation', deleted=deleted)
        return r

    security.declarePrivate(id_permissions.view_issue_dealer, 'get_remote_relations')
    def get_remote_relations(self):
        """Returns relations linking to the issue."""
        if self.get_user_preferences().show_deleted:
            deleted = [0,1]
        else:
            deleted = 0
        r = self.catalog_search(relation=self.id, deleted=deleted)
        return r

    security.declareProtected(id_permissions.view_issue_dealer, 'get_all_relations')
    def get_all_relations(self):
        """Returns all relations, both contained and 'remote'."""
        return self.get_relations() + self.get_remote_relations()

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'delete')
    def delete(self):
        """Marks self as deleted."""
        self.deleted = 1
	self.modified = DateTime()
        for issue in self.get_issues():
            issue.delete()
        self.index_object()

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'undelete')
    def undelete(self):
        """Marks self as deleted."""
        self.deleted = 0
	self.modified = DateTime()
        for issue in self.get_issues():
            issue.undelete()
        self.index_object()

    security.declareProtected(id_permissions.view_issue_dealer, 'get_link_saver_html')
    def get_link_saver_html(self):
        """Returns linker html for settings page."""
        return r"""<a href="javascript:var popup=window.open('', '','scrollbars=no,toolbar=no,location=no,width=500,height=400');popup.document.write('<html><head><title>Save a link</title><link rel=\'stylesheet\' type=\'text/css\' href=\'%s\' /><style type=\'text/css\'>body { padding: 5px; }</style></head><body><form action=\'%s\'><table><tr><th>Title</th><td><input class=\'inputText\' name=\'title\' type=\'text\' size=\'50\' value=\''+document.title+'\'></td></tr><tr><th>URL</th><td><input class=\'inputText\' type=\'text\' size=\'50\' name=\'url\' value=\''+document.location+'\'/></td></tr><tr><td colspan=\'2\'><br /><input class=\'issueDealer\' type=\'submit\' value=\' Continue \'/></td></tr></table></form></body></html>')">Save link</a>""" % (self.get_issue_dealer().absolute_url() + '/style', self.get_issue_dealer().absolute_url() + '/select_link_category')

    security.declareProtected(id_permissions.view_issue_dealer, 'notify_change')
    def notify_change(self, object):
        """Notifies listeners of changes to object."""
        try:
            self.getParentNode().notify_change(object)
        except AttributeError:
            pass

    security.declareProtected(id_permissions.view_issue_dealer, 'get_unique_id')
    def get_unique_id(self):
        """Returns a unique identifier."""
        # This is good enough for now
        integer, float = str(time.time()).split('.')
        time.sleep(0.01) # Make somewhat sure we're not getting similar IDs
        return integer + 'X' + float

    security.declareProtected(id_permissions.view_issue_dealer, 'call')
    call = base_utilities.call

    security.declareProtected(id_permissions.view_issue_dealer, 'get_parent_ids')
    def get_parent_ids(self):
        """Returns a list of parent ids."""
        ids = list()
        for object in self.get_parents():
            try: ids.append(self.call(object.id))
            except AttributeError: pass
        return ids

    security.declareProtected(id_permissions.view_issue_dealer, 'get_parent_id')
    def get_parent_id(self):
        """Returns the parent id."""
        return self.call(self.getParentNode().id)

    security.declareProtected(id_permissions.view_issue_dealer, 'get_parent_titles')
    def get_parent_titles(self):
        """Returns a list of parent titles."""
        titles = list()
        for object in self.get_parents():
            try: titles.append(self.call(object.title))
            except AttributeError: pass
        return titles

    security.declareProtected(id_permissions.view_issue_dealer, 'get_parent_meta_types')
    def get_parent_meta_types(self):
        """Returns a list of parent meta_types."""
        meta_types = list()
        for object in self.get_parents():
            try: meta_types.append(self.call(object.meta_type))
            except AttributeError: pass
        return meta_types

    security.declareProtected(id_permissions.view_issue_dealer, 'export')
    def export(self):
        """Exports issues and relations, as XML."""
        response = self.get_response()
        if not hasattr(self.aq_base, '_export'):
            raise NotImplementedError
        else:
            file = tempfile.TemporaryFile()
            file.write('<issuedealerdata encoding="utf-8" version="%s">\n' % '.'.join(map(str, self.filesystem_version)))
            self._export(file)
            file.write('\n</issuedealerdata>')
            file.seek(0)
            response.setHeader('Content-type','application/data')
            response.setHeader('Content-Disposition', 'inline;filename=issuedealer.xml')
            return file.read()

    security.declareProtected(id_permissions.view_issue_dealer, 'supports_iframe')
    def supports_iframe(self):
        """Returns a truth value if the browser supports iframe tags."""
        if self.get_user_preferences().use_iframe:
            user_agent = self.get_request()['HTTP_USER_AGENT'].lower()
            return user_agent.find('firefox') > -1 or \
                   user_agent.find('opera') > -1 or \
                   user_agent.find('msie') > -1 or \
                   user_agent.find('safari') > -1 or \
                   user_agent.find('konqueror') > -1
        else:
            return 0

    security.declareProtected(id_permissions.view_issue_dealer, 'is_action_issue')
    def is_action_issue(self):
        """Returns a truth value if the issue is an action issue."""
        return 1

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'add_multiple_issues')
    def add_multiple_issues(self, REQUEST):
        """Adds multiple issues."""
        for index in range(len(REQUEST['title'])):
            title = REQUEST['title'][index]
            contents = REQUEST['contents'][index]
            tags = REQUEST['tags'][index]
            owners = REQUEST['owners_%s' % index]
            if title.strip() or contents.strip():
                self.manage_add_issue(title=title, contents=contents, tags=tags, owners=owners)
        self.get_response().redirect(self.get_admin_url())

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'relation_add_submit')
    def relation_add_submit(self, REQUEST):
	"""Adds a relation."""
	import relation
	relation.manage_add_relation(self, relation_=REQUEST['issue'],
		title=REQUEST['title'])
	self.get_response().redirect(self.get_admin_url())

    security.declareProtected(id_permissions.view_issue_dealer, 'render_issue_format_widget')
    def render_issue_format_widget(self):
        """Returns a widget for selecting the default Issue format."""
        widget = '<select name="issue_format">'
        for key, value in (('text', 'Text'),
                           ('stx',  'STX'),
                           ('html', 'HTML'),
                           ):
            if key == self.get_user_preferences().issue_format:
                widget += """<option value="%s" selected="selected">%s</option>""" % \
                          (key, value)
            else:
                widget += """<option value="%s">%s</option>""" % \
                          (key, value)
        widget += "</select>"
        return widget

    security.declarePublic('generate_issue_selector_javascript')
    def generate_issue_selector_javascript(self, request):
        " "
        return """function select(item) {
	window.opener.document.forms[0].%s.value = item;
	window.close();
	return false;
	}""" % request.get('update_name', 'issue')

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_usernames')
    def get_usernames(self):
        """Returns a list of all known usernames."""
        reference = self
        users = ['unknown']
        while 1:
            try:
                if hasattr(reference.aq_base, 'acl_users'):
                    for user in reference.acl_users.getUserNames():
                        if not user in users: users.append(user)
                reference = reference.getParentNode()
            except AttributeError:
                break
        return users

InitializeClass(base)
