from Globals import DTMLFile, Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog, HTMLTools
from cgi import escape
import string
from DateTime import DateTime, DateTimeZone
from Products import IssueDealer
from Products.IssueDealer import session_manager, base, mixins, functions, permissions, id_config
import subscriber_templates
from Products.IssueDealerWeblogAddon import xmlrpclib
import urllib
from Products.IssueDealer import relation
import time
import atom
import utilities
import thread
import files
import smtplib

style = """body {
	font-family: verdana, tahoma, arial, helvetica, sans-serif;
	font-size: 12px;
	padding: 10px;
	padding-right: 20px;
}

h1 {
	font-size: 180%;
}

h1 a, h1 a:hover { color: #000; text-decoration: none; }

h2 {
	font-size: 130%;
}

a {  
	color: #436976; text-decoration: none; font-weight:bold;
}

a:hover {
  text-decoration: underline;
}

hr { background: black; }

#leftMenu {
	padding: 5px;
	width: 20%;
	float: left;
}

#leftMenu a {}

#main {
	width: 75%;
	margin-top: 2em;
	margin-left: 24%;
}

.olderEntries {
    list-style-type: none;
    line-height: 1em;
    margin: 0.4em 0 0 1em;
    padding:0;
}

#copyright {
	clear: both;
	float: none;
	margin: 0em 2em 0em 2em;
	padding: 10px;
	padding-top: 25px;
	text-align: center;
}

.message {
	padding: 5px;
        margin-bottom: 5px;
        border: 1px dashed #000;
	background-color: #ffc;
}

.errorMessage {
	padding: 5px;
        margin-bottom: 5px;
        border: 1px dashed #f00;
	background-color: #ffc;
}

.blogEntrySingle {
	background-color: #e6e6e6;
	border: 1px dashed #666;
	color: #404040;
	padding: 1em;
}

.blogEntryMultiple {
	background-color: #e6e6e6;
	border: 1px dashed #666;
	color: #404040;
	margin-bottom: 1em;
	padding: 1em;
}


.inputText {
	font: 12px Verdana, Helvetica, Arial, sans-serif;
	border: 1px solid white;
	border-bottom: 1px dotted #000;
	background-color: white;
	margin-bottom: 1px;
	padding: 0.1em;
	color: #000;
}

input {
	font: 12px Verdana, Helvetica, Arial, sans-serif;
	border: 1px solid white;
	background-color: white;
	margin-bottom: 1px;
	padding: 0.1em;
	color: #000;
}

.xoxo.blogroll { 
	list-style-type: none;
	line-height: 1em;
	margin: 0.4em 0 0 1em;
	padding:0;
}
"""

def add_file_handler(self):
    self._setObject('files', files.files('files'))

def manage_add_local_weblog_publisher_edit(self, id=None, title='', REQUEST=None):
    """Add a Local Weblog publisher."""
    if id is None:
        id = self.get_unique_id()
    local_weblog_publisher_ = local_weblog_publisher(id, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id())
    self._setObject(id, local_weblog_publisher_)
    local_weblog_publisher_ = self._getOb(id)
    local_weblog_publisher_.version = self.get_issue_dealer().filesystem_version
    local_weblog_publisher_._setObject('atom', atom.atom('atom'))
    add_file_handler(local_weblog_publisher_)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')
    else:
        return local_weblog_publisher_

class local_weblog_publisher(
    ZCatalog.CatalogAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,
    mixins.relation_publisher
    ): 
    """Local Weblog publisher class.

    An weblog publisher is a publisher of Issues.
    """

    meta_type = 'Local weblog publisher'
    publisher = 1
    blogroll = ''
    show_number_of_issues = 15
    show_number_of_issues_in_sidebar = 50
    ping = 0
    weblog_url = ''
    timezone = 'GMT'
    version = (0,9,70)
    comments = 0
    show_categories = 1
    subscribers = ()
    enable_subscriptions = 1
    admin_email = 'admin@localhost'
    comment_passphrase = ''

    manage_options = (OFS.Folder.Folder.manage_options[0],) + \
        (
            {'label': 'View',       'action': ''},
            {'label': 'Security',   'action': 'admin_access'},
        )

    security = AccessControl.ClassSecurityInfo()
    security.setDefaultAccess('allow')

    security.declareProtected(permissions.publish_issues, 'edit', 'publish',
	'deal', 'edit_style', 'edit_blogroll', 'subscribers', 'render_subscribers')
    security.declarePublic('get_title')
    edit = PageTemplateFile('edit.pt', globals())
    deal = PageTemplateFile('index.pt', globals())
    remote = DTMLFile('remote', globals())
    security.declarePublic('blog', 'blog_entry', 'blog_entry_comments', 'style',
	'index_html', 'rss', 'index.xml', 'rss.xml', 'atom_feed',
	'atom.xml', 'javascript', 'search', 'subscribe', 'categories', 'get_weblog_url')
    _blog = PageTemplateFile('blog.pt', globals())
    edit_style = PageTemplateFile('edit_style.pt', globals())
    edit_blogroll = PageTemplateFile('edit_blogroll.pt', globals())
    templates = PageTemplateFile('templates.pt', globals())
    blog_style = style
    _blog_entry = PageTemplateFile('blog_entry.pt', globals())
    rss = DTMLFile('rss', globals())
    atom_feed = DTMLFile('atom', globals())
    javascript = DTMLFile('weblog.js', globals())
    _search = PageTemplateFile('search.pt', globals())
    _categories = PageTemplateFile('categories.pt', globals())
    subscribe = PageTemplateFile('subscribe.pt', globals())
    subscribers_view = PageTemplateFile('subscribers.pt', globals())
    blog_template = PageTemplateFile('blog_template.pt', globals())

    manage_add_relation = relation.relation.manage_add_relation

    def render_atom_url(self):
        """Renders the correct URL for self reference in the Atom feed."""
        request = self.REQUEST
        if request.get('QUERY_STRING', ''):
            return self.get_weblog_url() + '/atom.xml' + '?' + escape(request['QUERY_STRING'])
        else:
            return self.get_weblog_url + '/atom.xml'

    def render_subscribers(self):
        """Renders the subscribers."""
        return ','.join(self.subscribers)

    def __init__(self, id, title='Local Weblog', creator='', owner=''):
        self.id = id
        self.title = title
        self.creator = creator
        self.owner_ = owner
	self.published = []

    security.declarePublic('get_enclosures')
    def get_enclosures(self, issue):
        """Returns all the enclosures within the issue."""
        issues_ = []
        if issue.format == 'file':
            issues_.append(issue)
        for id in issue.get_referenced_ids():
            issues_.append(self.get_object(id))
        issues = []
        for issue in issues_:
            file = getattr(issue, issue.filename)
            issues.append(
		{
			'title':issue.title,
			'id':issue.id,
			'filename':urllib.quote(issue.filename),
			'size':len(file),
			'content_type':file.content_type,
		}
	    )
	return issues

    security.declarePublic('get_category_issues')
    def get_category_issues(self, parent_level=-1):
        """Returns all category issues."""
        categories = []
        categories_ = []
        contained = {}
        for issue in self.get_published_issues():
            issue = issue['issue']
            parent = issue.get_parent_ids[-parent_level]
            if issue.get_parent_meta_types[1] != 'Issue Dealer' and \
                   parent not in categories_:
                category = self.get_object(parent)
                categories.append((category.id, category.title))
                categories_.append(parent)
        categories.sort(lambda x,y: cmp(x[1], y[1]))
        return categories

    security.declarePublic('add_subscriber')
    def add_subscriber(self, subscriber, REQUEST=None):
        """Adds a subscriber."""
        if not subscriber in self.subscribers:
            self.subscribers = list(self.subscribers) + [subscriber]
            connection = smtplib.SMTP(id_config.smtp)
            message = subscriber_templates.subscribed % \
		{'title':self.get_title(), 'url':self.get_weblog_url()}
            connection.sendmail(self.admin_email, [subscriber], message)

    security.declarePublic('remove_subscriber')
    def remove_subscriber(self, subscriber, REQUEST=None):
        """Adds a subscriber."""
        if subscriber in self.subscribers:
            subscribers = list(self.subscribers)
            subscribers.remove(subscriber)
            self.subscribers = subscribers
            connection = smtplib.SMTP(id_config.smtp)
            message = subscriber_templates.unsubscribed % \
		{'title':self.get_title(), 'url':self.get_weblog_url()}
            connection.sendmail(self.admin_email, [subscriber], message)

    def index_html(self, REQUEST):
        """Returns the blog view."""
        if hasattr(self.aq_base, 'custom_blog'):
            return self.custom_blog(REQUEST)
        else:
            return self._blog(REQUEST)

    def blog_entry(self, REQUEST):
        """Returns the blog view."""
        if hasattr(self.aq_base, 'custom_blog_entry'):
            return self.custom_blog_entry(REQUEST)
        else:
            return self._blog_entry(REQUEST)

    def search(self, REQUEST):
        """Returns the search view."""
        if hasattr(self.aq_base, 'custom_search'):
            return self.custom_search(REQUEST)
        else:
            return self._search(REQUEST)

    def categories(self, REQUEST):
        """Returns the categories view."""
        if hasattr(self.aq_base, 'custom_categories'):
            return self.custom_categories(REQUEST)
        else:
            return self._categories(REQUEST)

    security.declarePublic('get_weblog_host')
    def get_weblog_host(self):
        """Returns the weblog host."""
        return urllib.splithost(urllib.splittype(self.get_weblog_url())[1])[0].split(':')[0]

    security.declarePublic('get_weblog_url')
    def get_weblog_url(self):
        """Returns the weblog URL."""
        if self.weblog_url:
            return self.weblog_url
        else:
            return self.absolute_url()

    security.declarePublic('get_timezones')
    def get_timezones(self):
       """Returns available timezones."""
       zones = DateTimeZone._data.keys()
       zones.sort()
       return zones

    def render_timezone_widget(self):
        """Renders a widget for selecting timezones."""
        html = "<select name='timezone'>"
        for timezone in self.get_timezones():
            if timezone == self.timezone:
                html += "<option selected='selected'>%s</option>" % timezone
            else:
                html += "<option>%s</option>" % timezone
        html += "</select>"
        return html

    security.declarePrivate('get_weblog_publisher')
    def get_weblog_publisher(self):
        """Returns self."""
        return self

    security.declarePublic('get_older_entries')
    def get_older_entries(self):
        """Returns older entries."""
        return self.get_weblog_issues(start=self.show_number_of_issues, size=self.show_number_of_issues + self.show_number_of_issues_in_sidebar)

    security.declarePublic('get_issue_title')
    def get_issue_title(self, issue):
        """Returns the issue title.  This is a security hack."""
        if self.been_published(issue):
            if callable(issue.get_title): return issue.get_title()
            else: return issue.get_title
        else:
            raise 'Unauthorized'

    security.declarePublic('render_issue_contents')
    def render_issue_contents(self, issue, unlinked=0):
        """Renders the issue contents.  This is a security hack."""
        if issue.id in self.get_published_ids():
            return functions.render_contents_weblog(issue, unlinked=unlinked)
        else:
            raise 'Unauthorized'

    security.declarePublic('render_issue_created')
    def render_issue_created(self, issue):
        """Renders the issue creation date."""
        return issue.created.toZone(self.timezone).strftime('%d %h %H:%M')

    security.declarePublic('render_issue_category')
    def render_issue_category_link(self, issue):
        """Renders the issue category."""
        id = issue.get_parent_ids[1]
        title = issue.get_parent_titles[1]
        meta_type = issue.get_parent_meta_types[1]
        if meta_type == 'Issue Dealer':
            title = "All"
        return """<a href="%s/search?category=%s">%s</a>""" % \
          (self.get_weblog_url(), id, escape(title)) + \
          """ <a href="%s/atom.xml?category=%s">%s</a>""" % \
          (self.get_weblog_url(), id, '(Atom feed)') 

    security.declarePublic('get_weblog_issues')
    def get_weblog_issues(self, start=0, size=15, category=''):
        """Returns a list of published issues for the weblog."""
        if category:
            issues = self.catalog_search(published_in=self.id, get_parent_ids=category, sort_on='modified', sort_order='reverse')[start:start+size]
            issues_ = []
            for issue in issues:
                relation = self.catalog_search(meta_type='Relation', get_parent_id=self.id, relation=issue.id)[0]
                issues_.append({'issue':issue, 'date':relation.created, 'relation':relation, 'id':issue.id,
                               'created':issue.created, 'creator':issue.creator, 'get_parent_ids':issue.get_parent_ids})
            return issues_
        else:
            return self.get_published_issues(start=start, size=size, reverse=1)            
            
    security.declareProtected(permissions.publish_issues, 'publish_issue')
    def publish_issue(self, issue):
        """Publishes the issue to the weblog."""
        relation = mixins.relation_publisher.publish_issue.im_func(self, issue)
        if self.ping:
            try:
                remoteServer = xmlrpclib.Server("http://rpc.pingomatic.com")
                thread.start_new_thread(remoteServer.weblogUpdates.ping,
                                        (self.title, self.get_weblog_url()))
                self.get_user_preferences().add_message('Ping dispatched to pingomatic.com')
            except:
                raise
                self.get_user_preferences().add_message('Ping dispatch failed..')
        if self.enable_subscriptions and filter(None, self.subscribers):
            message = """Subject: New issue on %s called %s
From: %s
Content-Type: text/plain; charset=utf-8

URL: %s

%s""" % (self.get_title(), self.call(issue.get_title), self.admin_email, self.get_weblog_url() + '/blog_entry?id=' + issue.id, self.call(issue.render_contents_as_text))
            from Products.IssueDealer import id_config
            import smtplib
            try:
                connection = smtplib.SMTP(id_config.smtp)
                connection.sendmail(self.admin_email, self.subscribers, message)
            except:
                self.get_user_preferences().add_message('Sending email to subscribers failed..')

    security.declareProtected(permissions.view_issue_dealer, 'get_admin_url')
    def get_admin_url(self):
        """Returns the adminstrator view."""
        return self.absolute_url() + '/deal'
 
    security.declareProtected(permissions.edit_publishers, 'admin_edit')
    def admin_edit(self, id=None, title='', 
                   show_number_of_issues=15,
                   show_number_of_issues_in_sidebar=50,
                   timezone='', ping=0, weblog_url='',
                   comments=0, show_categories=0,
                   enable_subscriptions=0,
                   admin_email='',
                   comment_passphrase='',
                   REQUEST=None):
        """Edits the publisher."""
        if id and id != self.id:
            self.getParentNode().manage_renameObjects(ids=[self.id], new_ids=[id])
            get_transaction().commit()
        self.title = title
        self.show_number_of_issues = show_number_of_issues
        self.show_number_of_issues_in_sidebar = show_number_of_issues_in_sidebar
        self.timezone = timezone
        self.ping = ping
        self.weblog_url = weblog_url
        self.comments = comments
        self.show_categories = show_categories
        self.modified = DateTime()
        self.enable_subscriptions = enable_subscriptions
        self.admin_email = admin_email
        self.comment_passphrase = comment_passphrase
        self.index_object()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declareProtected(permissions.edit_publishers, 'admin_edit_blogroll')
    def admin_edit_blogroll(self, blogroll='', REQUEST=None):
        """Edits the blogroll."""
        self.blogroll = HTMLTools.html.clean(blogroll)
	self.modified = DateTime()
        self.index_object()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declareProtected(permissions.edit_publishers, 'admin_edit_style')
    def admin_edit_style(self, blog_style='', REQUEST=None):
        """Edits the blog style."""
        self.blog_style = blog_style
	self.modified = DateTime()
        self.index_object()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declarePublic('image')
    def image(self, id=None, REQUEST=None, RESPONSE=None):
        """Returns an image related to the published issue."""
        result = self.catalog_search(id=self.get_published_ids(),
					get_local_image_ids=id,
					meta_type='Issue')
        if result:
            return base.base.image.im_func(self, id=id, REQUEST=REQUEST, RESPONSE=RESPONSE)
        else:
            raise 'Unauthorized'

    security.declarePublic('get_next')
    def get_next(self, issue):
        """Returns the next issue, or none if there aren't any."""
        try:
            published = self.get_published_ids()
            return self.get_object(published[published.index(issue) + 1])
        except IndexError:
            return None
        except ValueError:
            return None

    security.declarePublic('get_previous')
    def get_previous(self, issue):
        """Returns the previous issue, or none if there aren't any."""
        try:
            published = self.get_published_ids()
            return self.get_object(published[published.index(issue) - 1])
        except IndexError:
            return None
        except ValueError:
            return None

    security.declarePublic('get_search_results')
    def get_search_results(self):
        """Returns search results."""
        ids = self.get_published_ids()
        data = self.REQUEST.get('search_string', None)
        category = self.REQUEST.get('category', None)
        if category: category = [category]
        if data and category:
            return self.catalog_search(id=ids, get_all_text=data,
              get_parent_ids=category, sort_on='created', sort_order='reverse')
        elif category:
            return self.catalog_search(id=ids,
              get_parent_ids=category, sort_on='created', sort_order='reverse')
        else:
            return self.catalog_search(id=ids, get_all_text=data, sort_on='created',
		sort_order='reverse')

    security.declarePublic('render_as_W3CDTF')
    def render_as_W3CDTF(self, date):
        """Renders the given date in a W3C Date and Time Format."""
        return utilities.render_as_W3CDTF(date)

    def _update(self):
        "Updates the weblog"
	pass

    security.declarePublic('handle_comments')
    def handle_comments(self):
        """Handles weblog comments."""
        request = self.get_request()
        try:
	    assert self.been_published(request['id'])
            relation = self.get_objects(relation=request['id'])[0]
            request['issues'] = relation.get_objects(meta_type='Issue', sort_on='created', deleted=0)
        except IndexError:
            # We're handling a referenced issue
            request['issues'] = ()

    security.declarePublic('comment')
    def comment(self):
        """To add a comment to an entry."""
        failed = message = ""
        # Check that comments are enabled
        assert self.comments
        request = self.get_request()
        if not request.has_key('comment_passphrase'):
            return failed, message, {}
        if self.comment_passphrase.strip():
            if self.comment_passphrase.strip() != request['comment_passphrase']:
                failed = 1
                message = "Sorry..  Wrong passphrase, try again"
        if not request['title']:
            failed = 1
            message = "Sorry..  Missing title"
        if not request['contents']:
            failed = 1
            message = "Sorry..  Missing the comment"
        if not request['email']:
            failed = 1
            message = "Sorry..  Missing the email"
        if not request['name']:
            failed = 1
            message = "Sorry..  Missing the name"
        if failed:
            return failed, message, request
        else:
	    message = "Comment added, thank you."
            relation = self.get_objects(relation=request['id'])[0]        
            contents = "By: %s\n\n" % request['name']
            relation.manage_add_issue(title=request['title'], contents=contents + request['contents'],
					creator=request['email'])
            return failed, message, {}

    security.declareProtected(permissions.edit_publishers, 'get_templates', 'customize_template', 'restore_template',
                              'customize_template_edit', 'save_template')
    def get_templates(self):
        """Returns a sequence of available templates."""
        templates = []
        for template in ('blog', 'blog_entry', 'search', 'categories'):
            if hasattr(self.aq_base, 'custom_' + template):
                customized = 1
            else:
                customized = 0
            templates.append({
                'id':template,
                'title':template.capitalize().replace('_', ' '),
                'customized':customized})
        return templates

    def customize_template(self, id):
        """Method for customizing template."""
        if not hasattr(self.aq_base, 'custom_' + id):
            template = getattr(self, '_' + id)
            self.manage_addProduct['PageTemplates'].manage_addPageTemplate('custom_' + id, text=template.document_src())
        self.get_response().redirect(self.absolute_url() + '/customize_template_edit?id=' + 'custom_' + id)

    def save_template(self, id, template):
        """Saves contents of template."""
        getattr(self.aq_base, id).pt_edit(template, '')
        self.get_response().redirect(self.absolute_url() + '/templates')

    def restore_template(self, id):
        """Restores the given template."""
        self.manage_delObjects(ids=['custom_' + id])
        self.get_response().redirect(self.absolute_url() + '/templates')

    def get_template_content(self, id):
        """Returns the content of template."""
        return getattr(self.aq_base, id)._text

    customize_template_edit = PageTemplateFile('customize_template.pt', globals())
   
InitializeClass(local_weblog_publisher)

setattr(local_weblog_publisher, 'index.xml', local_weblog_publisher.rss)
setattr(local_weblog_publisher, 'rss.xml', local_weblog_publisher.rss)
setattr(local_weblog_publisher, 'atom.xml', local_weblog_publisher.atom_feed)

from Products.IssueDealer.issue_dealer import issue_dealer, base

issue_dealer.manage_add_local_weblog_publisher_edit = manage_add_local_weblog_publisher_edit
issue_dealer.all_meta_types = issue_dealer.all_meta_types + [
    {'visibility': 'Global',
     'interfaces': [],
     'action': 'manage_add_local_weblog_publisher_edit',
     'permission': 'Add Local Weblog publisher',
     'name': 'Local Weblog publisher',
     'product': 'Issue Dealer',
     'instance': ''},]
IssueDealer.add_publisher(local_weblog_publisher, manage_add_local_weblog_publisher_edit)

