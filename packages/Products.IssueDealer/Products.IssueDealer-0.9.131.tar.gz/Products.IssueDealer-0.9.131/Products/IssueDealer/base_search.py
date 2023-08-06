import AccessControl
import permissions as id_permissions
import urllib
from cgi import escape
from Globals import InitializeClass
import cStringIO
import utilities
import re

class base_search:

    security = AccessControl.ClassSecurityInfo()

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_sort_on_widget')
    def render_sort_on_widget(self):
        """Returns a widget for selecting sorting index."""
        widget = '<select name="sort_on">'
        sort_on = self.get_user_preferences().sort_on
        for key, value in (('title', 'Title'),
			   ('importance', 'Importance'),
                           ('created', 'Created'),
			   ('owner', 'Owner'),
                           ('state', 'State'),
			   ('modified', 'Modified'),
			   ('get_state_importance_title_sort', 'State, importance, title'),
                           ('get_order', 'Order'),
                           ('get_state_importance_due_sort', 'State, importance, due'),
                           ):
            if key == sort_on:
                widget += """<option value="%s" selected="selected">%s</option>""" % \
                          (key, value)
            else:
                widget += """<option value="%s">%s</option>""" % \
                          (key, value)
        widget += "</select>"
        return widget

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_sort_order_widget')
    def render_sort_order_widget(self):
        sort_order = self.get_user_preferences().sort_order
        if sort_order == 'ascending':
            return """<input type="radio" name="sort_order" value="ascending" checked="checked" />Ascending<br />
                         <input type="radio" name="sort_order" value="descending" />Descending<br />"""  
        elif sort_order == 'descending':
            return """<input type="radio" name="sort_order" value="ascending" />Ascending<br />
                         <input type="radio" name="sort_order" value="descending" checked="checked" />Descending<br />"""
        else:
            raise NotImplementedError

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_search_owner_widget')
    def render_search_owner_widget(self):
        """Renders a widget for owner search."""
        widget = ''
        unique_owners = list(self.get_catalog().uniqueValuesFor('owners'))
        unique_owners.sort()
        if self.REQUEST.has_key('owner'):
            owners = self.REQUEST['owner']
        elif self.REQUEST.has_key('searching'):
            owners = []
        else:
            if self.get_user_preferences().search_owner_default == 'all':
                owners = unique_owners
            elif self.get_user_preferences().search_owner_default == 'self':
                owners = [self.get_user().get_id()]
            else:
                raise NotImplementedError
        for owner in unique_owners:
            if owner == None: continue
            if owner in owners:
                widget += """&nbsp;&nbsp;<input type="checkbox" name="owner:list"
                             value="%s" checked="checked" class="remoteCheckbox" /> %s<br />""" % \
                             (owner, owner.capitalize())
            else:
                widget += """&nbsp;&nbsp;<input type="checkbox" name="owner:list"
                             value="%s" class="remoteCheckbox" /> %s<br />""" % (owner, owner.capitalize())
        return widget

    # Untested
    security.declarePrivate('get_sort_index')
    def get_sort_index(self):
        """Returns the default sort index."""
        raise NotImplementedError

    # Untested
    security.declarePrivate('set_default_path')
    def set_default_path(self):
        """Sets the default path in the REQUEST."""
        self.REQUEST['path'] = '/'.join(self.getPhysicalPath())

    # Untested
    security.declarePrivate('set_default_states')
    def set_default_states(self):
        """Sets the default Issue states in the REQUEST."""
        states = ['open', 'closed', 'suspended', 'discarded']
        self.REQUEST['states'] = states
        try:
            quoted_search_string = urllib.quote(self.REQUEST['search_string'])
        except KeyError:
            quoted_search_string = ''
        if not self.REQUEST['QUERY_STRING']:
            self.REQUEST['QUERY_STRING'] = '?search_string=%s&' % quoted_search_string
        else:
            if not self.REQUEST['QUERY_STRING'].find('search_string=') > -1:
                self.REQUEST['QUERY_STRING'] += '&search_string=%s&' % quoted_search_string
        for state in states:
            self.REQUEST['QUERY_STRING'] += "states:list=%s" % state + '&'
        else:
            self.REQUEST['QUERY_STRING'] = self.REQUEST['QUERY_STRING'][:-1]

    # Untested
    security.declarePrivate('set_recent_changes_defaults')
    def set_recent_changes_defaults(self):
        """Sets defaults for listing recent changes."""
        self.REQUEST['states'] = self.get_issue_states()
        self.REQUEST['importance'] = map(lambda x: x[0],
                                         self.get_importance_levels())
        self.REQUEST['sort_type'] = 'modification_time'
        self.REQUEST['search_string'] = ''

    # Untested
    security.declarePrivate('search_defaults')
    def search_defaults(self, path, REQUEST):
        """Sets defaults for the search."""
        if REQUEST.has_key('filter'):
            filter = self.get_object(REQUEST['filter'])
            filter.update_request(path, REQUEST)

    security.declareProtected(id_permissions.view_issue_dealer, 'handle_search')
    def handle_search(self):
        """Handles search related logic."""
        self.search_defaults('/'.join(self.getPhysicalPath()), self.REQUEST)
	if self.REQUEST.get('search_all', 0):
	    self.set_recent_changes_defaults()
        if not self.REQUEST.has_key('states'):
	    self.set_default_states()
        if not self.REQUEST.has_key('path'):
	    self.set_default_path()

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_search_importance_level_widget')
    def render_search_importance_level_widget(self):
        """Returns a widget for handling importance levels."""
        widget = ""
        if not self.REQUEST.has_key('importance'):
            self.REQUEST['importance'] = \
              map(lambda x: x[0], self.get_importance_levels())
        else:
            self.REQUEST['importance'] = \
              map(lambda x: int(x), self.REQUEST['importance'])
        for key, value in self.get_importance_levels():
            widget += "&nbsp;&nbsp;"
            if key in self.REQUEST['importance']:
                widget += """<input type="checkbox" name="importance:list"
                             value="%s" checked="checked" class="remoteInput" /> %s""" % \
                             (key, value.capitalize())
            else:
                widget += """<input type="checkbox" name="importance:list"
                             value="%s" class="remoteInput" /> %s""" % (key, value.capitalize())
            widget += "<br />"
        return widget

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_search_sort_order_widget')
    def render_search_sort_order_widget(self):
        """Returns a widget for sort orders."""
        widget = '<select name="sort_type">'
        if not self.REQUEST.has_key('sort_type'):
            self.REQUEST['sort_type'] = 'modification_time'
        for key, value in (('score', 'Score'),
                           ('modification_time', 'Modified'),
                           ('modification_time_reverse', 'Modified, reversed'),
                           ('title', 'Title'),
                           ('title_reverse', 'Title, reversed'),
                           ('created', 'Created'),
                           ('created_reverse', 'Created, reversed'),
                           ('due', 'Due'),
                           ('due_reverse', 'Due, reversed'),
                           ):
            if key == self.REQUEST['sort_type']:
                widget += """<option value="%s" selected="selected">%s</option>""" % \
                          (key, value)
            else:
                widget += """<option value="%s">%s</option>""" % \
                          (key, value)
        widget += "</select>"
        return widget

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_search_results')
    def get_search_results(self, query=None):
        """Returns search results, based on REQUEST."""
        query = query or self.REQUEST
        if query.has_key('filter'):
	    self.search_defaults('/'.join(self.getPhysicalPath()), query)
        sort_on = None
        sort_order = None
        if self.get_user_preferences().show_deleted:
            deleted = [0,1]
        else:
            deleted = 0
        if query.has_key('sort_type'):
            if query['sort_type'] == 'modification_time':
                sort_order = 'descending'
                sort_on = 'modified'
            elif query['sort_type'] == 'modification_time_reverse':
                sort_order = 'ascending'
                sort_on = 'modified'
            elif query['sort_type'] == 'title':
                sort_order = 'ascending'
                sort_on = 'get_title'
            elif query['sort_type'] == 'title_reverse':
                sort_order = 'descending'
                sort_on = 'get_title'
            elif query['sort_type'] == 'created':
                sort_order = 'ascending'
                sort_on = 'created'
            elif query['sort_type'] == 'created_reverse':
                sort_order = 'descending'
                sort_on = 'created'
            elif query['sort_type'] == 'score':
                sort_on = None
                sort_order = None
            elif query['sort_type'] == 'due':
                sort_on = 'due'
                sort_order = 'descending'
            elif query['sort_type'] == 'due_reverse':
                sort_on = 'due'
                sort_order = 'ascending'
            else:
                raise NotImplementedError
        search = query['search_string']
        if query.has_key('states'):
            states = query['states']
        else:
            states = self.get_issue_states()
        if query.has_key('path'):
            path = query['path']
        else:
            path = ''
        if query.has_key('relative_state'):
            relative_state = query['relative_state']
        else:
            relative_state = 0
        if query.has_key('importance'):
            importance = map(lambda x: int(x),
                             query['importance'])
        else:
            importance = map(lambda x: x[0], self.get_importance_levels())
        if query.has_key('owner'):
            owner = query['owner']
        else:
            owner = None
        tags = None
        if query.has_key('tags') and query['tags'].strip():
            tags = map(lambda x: x.strip().replace(',', ':'), cStringIO.StringIO(query['tags']).readlines())
        if sort_on:
            if relative_state:
                return self.catalog_search(get_all_text=search,
                                           path=path, deleted=deleted,
                                           importance=importance, meta_type=['Issue'],
                                           sort_on=sort_on, sort_order=sort_order,
                                           owners=owner, get_relative_state=states, tags=tags)
            else:
                return self.catalog_search(get_all_text=search,
                                           path=path, deleted=deleted,
                                           importance=importance, meta_type=['Issue'],
                                           sort_on=sort_on, sort_order=sort_order,
                                           owners=owner, state=states, tags=tags)
        else:
            if relative_state:
                return self.catalog_search(get_all_text=search,
                                           path=path, deleted=deleted,
                                           importance=importance, meta_type=['Issue'],
                                           owners=owner, get_relative_state=state, tags=tags)
            else:
                return self.catalog_search(get_all_text=search,
                                           path=path, deleted=deleted,
                                           importance=importance, meta_type=['Issue'],
                                           owners=owner, state=states, tags=tags)

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'search_buttons')
    def search_buttons(self):
        """Returns search buttons."""
        filters = self.get_user_preferences().objectValues('Filter')
        if filters:
            html = """<div class="buttons">"""
            for filter in filters:
                html += """<a href="%s" class="button">%s</a>&nbsp;&nbsp;""" % \
                        (self.REQUEST['URL'] + '?filter=%s' % filter.id, escape(filter.get_title()))
            return html + """</div><br /><br />"""
        else:
            return ""

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'save_filter')
    def save_filter(self, REQUEST):
        """Saves the filter."""
        self.get_user_preferences().manage_add_filter(REQUEST=REQUEST)
        REQUEST.RESPONSE.redirect(REQUEST['referrer'])

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'manage_delete_filters')
    def manage_delete_filters(self, ids=[], REQUEST=None):
        """Deletes the specified filters."""
        if ids:
            self.get_object(ids[0]).getParentNode().manage_delObjects(ids=ids)
        if REQUEST:
            self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/filters')

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_advanced_search_results')
    def get_advanced_search_results(self):
        " "
        request = self.REQUEST
        if not request.get('query'): return
        query = re.compile(request['query'])
        #tags = utilities.parse_tags(request['tags'])
        display = request['display']
        found = []
        if display == 'navigate':
            for issue in self.get_issues():
                matches = query.findall(issue.contents)
                if matches:
                    found.append({'issue':issue.getObject(), 'matches':matches})
        elif display == 'tabular':
            for issue in self.get_issues():
                matches = query.findall(issue.contents)
                if matches:
                    found.extend(matches)
            found = utilities.get_unique_values_single(matches)
        return found

InitializeClass(base_search)