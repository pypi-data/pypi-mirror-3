from Globals import Persistent, InitializeClass, DTMLFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
from cgi import escape
import string
# The extra entry in sys.path is needed for
# the docutils package
import sys
sys.path.append(SOFTWARE_HOME + '/Products/IssueDealer')
sys.path.append(INSTANCE_HOME + '/Products/IssueDealer')
from docutils.core import publish_string
from DateTime import DateTime
import cStringIO, htmllib, formatter
from Products.HTMLTools import html
import urllib
import image, base, mixins, session_manager, utilities
from Products import IssueDealerEpoz
import html4css1_inline
import relation
from App.config import getConfiguration
import importers
import functions
import base64
import permissions
from Products.IssueDealer import issue_dealer_globals
from persistent.list import PersistentList

def manage_add_issue(self, id=None, title='', contents='',
		state='', referrer='', format=None, tags='',
                creator=None, owners=(), REQUEST=None):
    """Add an Issue."""
    if id is None:
        id = self.get_unique_id()
    issue_ = issue(id, title, contents, state,
                   creator=creator or self.get_user().get_id(),
                   owners=owners or (self.get_user().get_id(),),
                   format=format or self.get_user_preferences().issue_format,
                   tags=tags or 'issue-type:info')
    issue_.last_modified_by = self.get_user().get_id()
    self._setObject(id, issue_)
    self.order.append(issue_.id)
    self.order = self.order
    issue_ = self[id]
    issue_.version = self.get_issue_dealer().filesystem_version
    try:
        self.index_object()
    except AttributeError:
        pass
    if referrer and REQUEST is not None:
        REQUEST.RESPONSE.redirect(referrer)
    else:
        if REQUEST is not None:
            self.get_response().redirect(self.get_admin_url())
        else:
            return issue_

def manage_add_issue_edit(self, id=None, title='', contents='', referrer='',
                          state='', tags='', REQUEST=None):
    """Adds an issue and redirects to the edit page."""
    if id is None:
        id = self.get_unique_id()
    manage_add_issue(self, id=id, title=title, contents=contents,
                     referrer=referrer, state=state, tags=tags,
                     REQUEST=REQUEST)
    REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')

from copy_types import copy_types

class issue(
    mixins.catalog,
    ZCatalog.CatalogPathAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,
    importers.importers,
    ): 
    """Issue class.

    An issue contains information relating to a task, an idea, or something else..
    
    """

    meta_type = 'Issue'

    # Backwards compatability
    state = 'open'
    type = 'info'
    creator = 'unknown'
    owner_ = 'unknown'
    importance = 1
    format = 'text'
    created = DateTime("2003/01/01")
    version = (0,9,70)
    relation = None
    filename = ''
    tags = ()

    # Needed for cutting and pasting objects
    all_meta_types = copy_types

    manage_options = (OFS.Folder.Folder.manage_options[0],) + \
        (
            {'label': 'View',       'action': ''},
            {'label': 'Security',   'action': 'manage_access'},
        )

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(permissions.view_issue_dealer,
      'index_html', 'get_title')
    security.declareProtected(permissions.add_edit_issues_and_relations,
      'manage_add_issue', 'manage_add_issue_edit', 'edit', 'image_edit',
      'add_image', 'issue_edit_image')

    instance_home = getConfiguration().instancehome

    index_html = PageTemplateFile('skins/issue_dealer/issue_dealer_index.pt', issue_dealer_globals)
    manage_add_issue = manage_add_issue
    manage_add_issue_edit = manage_add_issue_edit
    issue_edit_view = PageTemplateFile('skins/issue_dealer/issue_dealer_issue_edit.pt', issue_dealer_globals)
    issue_edit_image = PageTemplateFile('skins/issue_dealer/issue_dealer_edit_image.pt', issue_dealer_globals)
    issue_edit_file = PageTemplateFile('skins/issue_dealer/issue_dealer_edit_file.pt', issue_dealer_globals)
    image_edit = PageTemplateFile('skins/issue_dealer/issue_dealer_image_edit.pt', issue_dealer_globals)
    file_edit = PageTemplateFile('skins/issue_dealer/issue_dealer_file_edit.pt', issue_dealer_globals)
    iframe_view = PageTemplateFile('skins/issue_dealer/issue_dealer_issue_iframe.pt', issue_dealer_globals)

    add_image = image.add_image

    def edit(self, REQUEST):
        """Does some tricks."""
        return self.issue_edit_view()

    def __init__(self, id, title='', contents='', 
                 state='', creator='', owners=(),
                 format='text', tags=''): 
        """Initialize a new instance of Issue"""
        self.id = id
        self.title = title
        self.contents = contents
        self.state = state or 'open'
        self.creator = creator or 'unknown'
        self.owners = PersistentList(owners) or PersistentList(('unknown',))
        self.modified = self.created = DateTime()
        self.format = format
        self.order = []
        self.tags = PersistentList(utilities.parse_tags(tags))

    # Untested
    security.declarePrivate('set')
    def set(self, name, value):
        """Alias for attribute setting."""
        exec("self.%s = value" % name)

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_stx_as_html')
    def render_stx_as_html(self):
        """Renders the contents as reSTX."""
        return functions.render_stx_as_html(self)

    # Untested
    security.declarePrivate(permissions.view_issue_dealer, 'render_text_as_html')
    def render_text_as_html(self):
        """Renders the contents as text, keeping whitespace indentation."""
        return functions.render_text_as_html(self)

    def add_file(self, id, file, title):
        """Adds a issue with a format of file."""
        issue = self.manage_add_issue(id=id)
        issue.manage_edit(title=title, file=file)

    # Untested
    security.declareProtected(permissions.add_edit_issues_and_relations, 'manage_edit')
    def manage_edit(self, title='', contents='', state='open',
                    owners=None, importance=1, file=None,
                    due=None, filename='', tags='', REQUEST=None):
        """Edits the object."""
        if self.format == 'html':
            contents = html.clean(contents)
        self.set('title', title)
        self.set('contents', contents)
        self.tags = PersistentList(map(lambda x: x.strip().replace(',', ':'), cStringIO.StringIO(tags).readlines()))
        self.change_state(state)
        if not owners is None:
             self.owners = PersistentList(owners)
        self.set('importance', importance)
        if due and due.strip():
            self.due = DateTime(due)
        else:
            self.due = None
        self.modified = DateTime()
        self.last_modified_by = self.get_user().get_id()
        if file:
            try:
                self.manage_delObjects(ids=[self.filename])
            except:
                # Empty except, FIXME
                pass
            self.format = 'file'
            self.manage_addFile(getattr(file, 'filename', filename), file=file)
            self.filename = getattr(file, 'filename', filename)
        self.index_object()
        if REQUEST is not None:
            if REQUEST['manage_edit'] == 'Save and view':
                REQUEST.RESPONSE.redirect(self.get_admin_url())
            else:
                REQUEST.RESPONSE.redirect(self.absolute_url() + '/edit')

    # Untested
    security.declareProtected(permissions.add_edit_issues_and_relations, 'get_possible_edit_issue_types')
    def get_possible_edit_issue_types(self):
        """Returns a sequence of issue types, depending on what
        type of Issue the containing Issue is."""
        return self.get_possible_issue_types(self.getParentNode())

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'get_relative_importance')
    def get_relative_importance(self):
        """Returns the relative importance of the Issue;  calculated
        by the importance of containing Issues and self."""
        return 1

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'get_relative_state')
    def get_relative_state(self):
        """Returns the relative state of the Issue."""
        if self.state == 'open':
            try:
                return self.getParentNode().get_relative_state()
            except AttributeError:
                return self.state
        else:
            return self.state

    # Untested
    security.declarePrivate('change_state')
    def change_state(self, new_state, from_parent=0):
        """Changes the state of the object and, if necessary, the
        state of contained objects and the state of the containing object."""
        current_state = self.state
        if new_state != current_state:
            reindex = None
	    parent = self.getParentNode()
            if not hasattr(self.get_user_preferences().aq_base, '_changed_objects'):
                self.get_user_preferences()._changed_objects = []
                reindex = 1
            if self.is_action_issue():
                if new_state == 'open' and current_state == 'closed':
                    # It has been re-opened and we'll have to undo
                    # the closed (selected) state of contained
		    # solutions, if any.
                    issues = self.get_issues()
                    for issue in issues:
                        if issue.get_type() == 'solution':
                            if issue.state == 'closed':
                                issue.change_state('open',
                                  from_parent=1)
            if self.get_type() == 'solution':
                if new_state == 'closed':
                    # It has resolved/reached the containing
                    # problem or goal.
                    if not from_parent:
                        parent.change_state('closed')
                elif new_state == 'open' and current_state == 'closed':
                    # The solution has been re-opened, and
                    # will open the containing goal/problem
                    # as well.
                    if not from_parent:
			if parent.is_action_issue():
                            parent.change_state('open')
                elif new_state == 'discarded' and current_state == 'closed':
                    # The selected solution has been discarded, and
                    # will open the containing goal/problem
                    if not from_parent:
			if parent.is_action_issue():
                            parent.change_state('open')
            if self.get_type() == 'problem':
                # If there are open problems related to the Issue,
                # it has to be open
                if new_state == 'open':
                    parent.change_state('open')
                elif new_state == 'closed':
                    # Can't close the containing Issue
                    pass
            if self.get_type() == 'goal':
                # If there are open goals related to the Issue,
                # it has to be open
                if new_state == 'open':
                    parent.change_state('open')
                elif new_state == 'closed':
                    # Can't close the containing Issue
                    pass
            self.set('state', new_state)
            self.get_user_preferences()._changed_objects.append((self, self.get_level()))
            self.modified = DateTime()
            if reindex:
                object = (None, 1000)
                for object_, level in self.get_user_preferences()._changed_objects:
                    if level < object[1]:
                        # New, higher level object found
                        object = (object_, level)
                self.get_object(object[0].id).reindex_all()
                del self.get_user_preferences()._changed_objects

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_html_title_and_link_tree')
    def render_html_title_and_link_tree(self):
        """Renders a link for tree browsing."""
        return self.render_html_title_and_link(tree=1)

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_html_title_and_link')
    def render_html_title_and_link(self, size=None, show_session=1, tree=0):
        """Renders a coloured link, depending on the type (and state) of the Issue."""
        color = ''
        if self.state == 'open':
            if self.get_type() == 'problem':
                if self.importance == 2:
                    color = 'red'
                else:
                    color = 'yellow'
            else:
                color = 'green'
        else:
            color = 'green'
        title = self.get_title()
        if tree and self.get_objects():
            url = self.absolute_url() + '/issue_tree'
        else:
            url = self.absolute_url()
        if self.id in self.get_session().marks and show_session:
            title = "* " + title
        if color:
            if tree:
                html = self.create_hyperlink(url, title)
            else:
                html = self.create_hyperlink(url, title)
            html = self.create_hyperlink(url, title,
              klass=color, size=size)
            if size is not None and len(title) > size:
                html += """<div class="hidden" id="title_%s">%s</div>""" %\
                  (self.id, escape(title))
        else:
            html = self.create_hyperlink(url, title)
        return html

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_contents')
    def render_contents(self, skip_less_more=0):
        """Renders the contents."""
        return functions.render_contents(self)

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_contents_weblog')
    def render_contents_weblog(self):
        """Renders the contents for a (possibly proxied behind
	different domain name) weblog."""
        return functions.render_contents_weblog(self)

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_contents_weblog_unlinked')
    def render_contents_weblog_unlinked(self):
        """Renders the contents for a (possibly proxied behind different domain name) weblog
	without any links (to stop spammers from gaining googlejuice and such)."""
        return functions.render_contents_weblog(self, unlinked=1)

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_contents_as_text')
    def render_contents_as_text(self, size=None):
        """Renders the contents as text."""
        return functions.render_contents_as_text(self)

    # Untested
    security.declareProtected(permissions.add_edit_issues_and_relations, 'render_importance_level_widget')
    def render_importance_level_widget(self):
        """Returns a widget for handling importance levels."""
        widget = """<select name="importance:int">"""
        for key, value in self.get_importance_levels():
            if self.importance == key:
                widget += """<option value="%s" selected="selected">%s</option>""" % \
                          (key, value.capitalize())
            else:
                widget += """<option value="%s">%s</option>""" % \
                          (key, value.capitalize())
        return widget + "</select>"

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_importance')
    def render_importance(self):
        """Renders the importance."""
        for key, value in self.get_importance_levels():
            if key == self.importance:
                return value
        else:
            return 'Unknown'

    # Untested
    security.declareProtected(permissions.view_issue_dealer, 'render_owners')
    def render_owners(self):
        """Renders the owners."""
        if self.owners:
            return ','.join(self.owners)
        else:
            return 'unknown'

    # Untested
    security.declarePrivate('get_state_importance_title_sort')
    def get_state_importance_title_sort(self):
        """Returns a string used for sorting in the catalog."""
        sort = ""
        if self.state == 'open':
            sort += "0"
        elif self.state == 'suspended':
            sort += "1"
        elif self.state == 'closed':
            sort += "2"
        elif self.state == 'discarded':
            sort += "3"
        else:
            utilities.log("Unknown state %s" % self.state)
        # The dictionary hack is needed so that the catalog sorts
        # in the right order.  Should definently fix this in a
        # better way.
        sort += str({0:2,1:1,2:0}[self.importance])
        sort += self.get_title()
        return sort

    # Untested
    security.declarePrivate('get_state_importance_due_sort')
    def get_state_importance_due_sort(self):
        """Returns a string used for sorting in the catalog."""
        sort = ""
        if self.state == 'open':
            sort += "0"
        elif self.state == 'suspended':
            sort += "1"
        elif self.state == 'closed':
            sort += "2"
        elif self.state == 'discarded':
            sort += "3"
        else:
            utilities.log("Unknown state %s" % self.state)
        # The dictionary hack is needed so that the catalog sorts
        # in the right order.  Should definently fix this in a
        # better way.
        sort += str({0:2,1:1,2:0}[self.importance])
        try:
            sort += str(int(self.due))
        except TypeError:
            pass
        return sort

    security.declareProtected(permissions.view_issue_dealer, 'get_short_url')
    def get_short_url(self):
        """Returns a short URL to the object."""
        return self.get_issue_dealer().absolute_url() + '/r?i=%s' % self.id

    security.declarePrivate('get_all_text')
    def get_all_text(self):
        """Returns all text on the object."""
        try:
            return ((self.title + " ") * 2) + \
                   " " + self.contents + \
                   self.render_breadcrumbs(html=0, hyperlink=0)
        except AttributeError:
            # We're probably importing, ignore it for now XXX
            pass

    security.declarePrivate('get_related_object')
    def get_related_object(self):
        """Returns the related object, relation hack."""
        return self

    security.declarePrivate('get_issue')
    def get_issue(self):
        """Returns self."""
        return self

    security.declareProtected(permissions.view_issue_dealer, 'get_image_links')
    def get_image_links(self):
        """Returns sources of images, if any."""
        return functions.get_image_links(self)

    security.declareProtected(permissions.view_issue_dealer, 'get_internal_links')
    def get_internal_links(self):
        """Returns sources of links, if any."""
        return functions.get_internal_links(self)

    security.declareProtected(permissions.view_issue_dealer, 'get_referenced_ids')
    def get_referenced_ids(self):
        """Returns referenced ids."""
        ids = []
        for link in functions.get_internal_links(self):
            id = link.split('/')[-1].split('=')[-1]
            try:
                object = self.get_object(id)
                ids.append(id)
            except IndexError:
                pass
        return ids

    security.declareProtected(permissions.view_issue_dealer, 'get_local_images')
    def get_local_images(self):
        """Returns a list of local images."""
        images = []
        for image in self.get_local_image_links():
            if image.find('image?id=') > -1:
                images.append(self.get_object(image.split('image?id=')[-1]))
            else:
                images.append(self.restrictedTraverse(image))
        return images

    security.declareProtected(permissions.view_issue_dealer, 'get_local_image_links')
    def get_local_image_links(self):
        """Returns local images, if any."""
        images = []
        for image in functions.get_image_links(self):
            try:
                path = urllib.splithost(urllib.splittype(image)[1])[1]
                if path.find('image?id=') > -1:
                    image_ = self.get_object(path.split('image?id=')[-1])
                else:
                    image_ = self.restrictedTraverse(path)
                images.append(image)
            except:
                pass
        return images

    security.declareProtected(permissions.view_issue_dealer, 'get_local_image_ids')
    def get_local_image_ids(self):
        """Returns local images, if any."""
        images = []
        try:
            for image in self.get_local_images():
                images.append(self.call(image.getObject().id))
        except KeyError:
            # We're probably importing, ignore for now XXX
            pass
        return images

    security.declareProtected(permissions.view_issue_dealer, 'get_external_image_links')
    def get_external_image_links(self):
        """Returns external images, if any."""
        images = []
        local = self.get_local_image_links()
        for image in self.get_image_links():
            if not image in local:
                images.append(image)
        return images

    security.declareProtected(permissions.view_issue_dealer, 'render_due_widget')
    def render_due_widget(self):
        """Renders the due widget."""
        if self.due:
            due = self.due
        else:
            due = DateTime()
        return utilities.render_datetime_widget(selected_date=due)

    security.declareProtected(permissions.add_edit_issues_and_relations, 'switch_format')
    def switch_format(self, REQUEST):
        """Switches to the specified format."""
        self.manage_edit(title=REQUEST['title'], contents=REQUEST.get('contents', ''),
                state=REQUEST['state'], owners=REQUEST['owners'], importance=REQUEST['importance'],
                due=REQUEST.get('due', None), tags=REQUEST['tags'])
        if self.format == 'file':
            if not getattr(self, self.filename).content_type in \
               ('text/html', 'text/plain'):
                self.get_user_preferences().add_message('Unable to convert file')
                self.get_response().redirect(self.get_admin_url())
                return
        if REQUEST['switch_format'] == 'HTML':
            self.contents = self.render_contents()
            if self.format == 'file':
                self.manage_delObjects(ids=[self.filename])
            self.format = 'html'
        elif REQUEST['switch_format'] == 'STX':
            if self.format == 'html':
                pass # XXX print 'Warning, downgrading contents to stx...'
            self.contents = self.render_contents_as_text()
            self.format = 'stx'
            if self.format == 'file':
                self.manage_delObjects(ids=[self.filename])
        elif REQUEST['switch_format'] == 'Text':
            if self.format == 'html':
                pass # XXX print 'Warning, downgrading contents to text...'
            self.contents = self.render_contents_as_text()
            if self.format == 'file':
                self.manage_delObjects(ids=[self.filename])
            self.format = 'text'
        elif REQUEST['switch_format'] == 'File':
            if self.format == 'html':
                data = """"<html><head><title></title></head><body>"""
                data += self.render_contents()
                data += """</body></html>"""
                content_type = 'text/html'
            elif self.format in ('stx', 'text'):
                data = self.contents
                content_type = 'text/plain'
            file = cStringIO.StringIO(data)
            if self.format == 'html': self.filename = 'issue.html'
            elif self.format in ('text', 'stx'): self.filename = 'issue.txt'
            else: raise NotImplementedError
            self.manage_addFile(self.filename, file=file, content_type=content_type)
            self.format = 'file'
        else:
            raise NotImplementedError
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/edit')

    security.declareProtected(permissions.add_edit_issues_and_relations, 'get_editor_html')
    def get_editor_html(self):
        """Returns contents for HTML editing."""
        return """<html><head><title></title></head><body>""" + self.contents + \
		"""</body></html>"""

    security.declareProtected(permissions.add_edit_issues_and_relations, 'get_epoz_style')
    def get_epoz_style(self):
        """Returns style declarations for Epoz."""
        prefs = self.get_user_preferences()
        return """width: %spx; height: %spx; border: 1px solid #999;""" % \
		(prefs.html_editor_width, prefs.html_editor_height)

    security.declareProtected(permissions.add_edit_issues_and_relations, 'render_epoz')
    def render_epoz(self, *arguments, **keywords):
        """Renders epoz editing controls."""
        return IssueDealerEpoz.IssueDealerEpoz(*arguments, **keywords)

    def _update(self):
	if self.type == 'alternative':
            self.type = 'solution'
        if self.type == 'undefined':
            self.type = 'info'
        if not self.__dict__.has_key('tags'):
            self.tags = PersistentList()
        if self.__dict__.has_key('type'):
            self.tags.append('issue-type:' + self.type)
            del self.type
        if self.__dict__.has_key('owner_'):
            self.owners = PersistentList((self.owner_,))
            del self.owner_

    def _export(self, export):
        """Exports the issue as XML."""
        export.write("""<issue id="%s" format="%s" creator="%s" owners="%s" state="%s" modified="%s" deleted="%s">""" % \
                 (self.id, self.format, self.creator, ','.join(self.owners), self.state, self.modified, self.deleted))
        export.write("""<title>%s</title>""" % escape(self.title))
        if self.format == 'file':
            export.write("""<contents filename="%s" content_type="%s" encoding="base64">\n%s\n</contents>""" % \
                      (self.filename, getattr(self, self.filename).content_type,
                       base64.encodestring(getattr(self, self.filename).data)))
        else:
            export.write("""<contents>%s</contents>""" % escape(self.contents))
        export.write("""<order>%s</order>""" % ','.join(self.order))
        for issue_or_relation in self.get_objects(meta_type=['Issue', 'Relation']):
            issue_or_relation._export(export)
        export.write("""</issue>\n""")

    security.declareProtected(permissions.view_issue_dealer, 'is_action_issue')
    def is_action_issue(self):
        """Returns a truth value if the issue is an action issue."""
        return self.get_type() in self.get_action_issue_types()

    security.declareProtected(permissions.view_issue_dealer, 'get_contained_action_issues')
    def get_contained_action_issues(self):
        """Returns the contained action issues."""
        filter_ = lambda x, self=self: x.id != self.id
        return filter(filter_, self.catalog_search(meta_type='Issue',
			state='open', is_action_issue=True, sort_on='due',
			path='/'.join(self.getPhysicalPath())
	))

    security.declareProtected(permissions.view_issue_dealer, 'get_file_issues')
    def get_file_issues(self):
        """Returns all issues contained with the file type."""
        return self.get_objects(meta_type='Issue', format='file')

    security.declareProtected(permissions.view_issue_dealer, 'render_tag_widget')
    def render_tag_widget(self):
        " "
        tags = '\n'.join(list(self.tags))
        tags = escape(tags)
        return """<textarea name="tags" rows="%s" cols="30"
		style="font-family: 'Courier New', Courier; font-size: 1em;""
		>%s</textarea>""" % (self.get_user_preferences().textarea_height, tags)

    security.declareProtected(permissions.view_issue_dealer, 'get_type')
    def get_type(self):
        """Returns the issue type, defaults to info."""
        for tag in self.tags:
            if tag.startswith('issue-type:'):
                return tag.split(':')[1]
        else:
            return 'info'

    security.declareProtected(permissions.view_issue_dealer, 'render_tags')
    def render_tags(self):
        """Renders the issue tags."""
        return ','.join(self.tags)

    security.declareProtected(permissions.add_edit_issues_and_relations, 'reschedule')
    def reschedule(self, days=None, REQUEST=None, RESPONSE=None):
        """Reschedules the event."""
        if days:
            days = int(days)
            if self.due and self.is_action_issue():
                self.due = self.due + days
                self.modified = DateTime()
                self.index_object()
        RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.add_edit_issues_and_relations, 'remove_tags')
    def remove_tags(self, tags=(), RESPONSE=None):
        """Removes the specified tags, if they are defined."""
        for tag in tags:
            try:
                self.tags.remove(tag)
            except ValueError:
                pass
        if RESPONSE:
            RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.add_edit_issues_and_relations, 'add_tags')
    def add_tags(self, tags=(), RESPONSE=None):
        """Adds the specified tags."""
        for tag in tags:
            if not tag in self.tags:
                self.tags.append(tag)
        if RESPONSE:
            RESPONSE.redirect(REQUEST['HTTP_REFERER'])
        

InitializeClass(issue)

import relation
issue.manage_add_relation = relation.manage_add_relation
