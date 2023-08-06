from Globals import Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
from Products import ZCatalog
from Products.IssueDealer import base
from cgi import escape
import string
from DateTime import DateTime
from Products import IssueDealer
from Products.IssueDealer import session_manager, base, mixins, permissions
from Products.IssueDealerWebDAVPublisher import webdav_publisher

def manage_add_faq_publisher_edit(self, id=None, title='', REQUEST=None):
    """Add a FAQ publisher."""
    if id is None:
        id = self.get_unique_id()
    faq_publisher_ = faq_publisher(id, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id())
    self._setObject(id, faq_publisher_)
    faq_publisher_ = self._getOb(id)
    faq_publisher_.version = self.get_issue_dealer().filesystem_version
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')
    else:
        return faq_publisher_

class faq_publisher(webdav_publisher.webdav_publisher):
    """FAQ publisher class.

    An FAQ publisher publishes issues (questions, and optionally solutions) to a FAQ
    """

    meta_type = 'FAQ publisher'
    publisher = 1

    manage_options = (OFS.Folder.Folder.manage_options[0],) + \
        (
            {'label': 'View',       'action': ''},
            {'label': 'Security',   'action': 'manage_access'},
        )

    security = AccessControl.ClassSecurityInfo()
    security.setDefaultAccess('allow')

    security.declareProtected(permissions.edit_publishers, 'edit', 'index_html')
    publish = PageTemplateFile('publish.pt', globals())

    security.declareProtected(permissions.publish_issues, 'publish_issue')
    def publish_issue(self, issue):
        """Publishes Issues as a FAQ."""
        self.REQUEST['issue'] = issue
        return self.publish()

    security.declareProtected(permissions.edit_publishers, 'manage_edit')
    def manage_edit(self, title='', REQUEST=None):
        """Edits the publisher."""
        self.title = title
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())

InitializeClass(faq_publisher)

from Products.IssueDealer.issue_dealer import issue_dealer, base

issue_dealer.manage_add_faq_publisher_edit = manage_add_faq_publisher_edit
issue_dealer.all_meta_types = issue_dealer.all_meta_types + [
    {'visibility': 'Global',
     'interfaces': [],
     'action': 'manage_add_faq_publisher_edit',
     'permission': 'Add FAQ publisher',
     'name': 'FAQ publisher',
     'product': 'Issue Dealer',
     'instance': ''},]

def publish_faq(self, issues=[], REQUEST=None):
    """Publishes a FAQ, based on the selected Issues."""
    if not issues:
        self.get_user_preferences().add_message('Need to select issues to generate a FAQ from', level=500)
        REQUEST.RESPONSE.redirect(self.absolute_url())
    html = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <title>FAQ</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    </head>
    <body>
    <table>
    """
    REQUEST.set('expand_text', 1)
    for issue in issues:
        issues[issues.index(issue)] = self.get_object(issue)
    html += "<tr><td colspan='2'>"
    for issue in issues:
        html += "<a href='#%s'>" % issue.id + escape(issue.get_title) + "</a><br />"
    html += "<br /></td></tr>"
    for issue in issues:
        html += "<tr><th valign='top'>Q:</th><td>"
        html += "<a name='%s'></a>" % issue.id
        if issue.title:
            html += '<b>' + escape(issue.get_title) + '</b><br />'
        html += issue.render_contents(skip_less_more=1)
        html += "</td></tr><tr><th valign='top'>A:</th><td>"
        for issue in issue.get_objects(meta_type='Issue', type='solution', state='closed'):
            if issue.title:
                html += '<b>' + escape(issue.get_title) + '</b><br />'
            html += issue.render_contents(skip_less_more=1) + '<br /><br />'
        html += "</td></tr>\n"
    return html + "</table></body></html>"

base.base.publish_faq = publish_faq
IssueDealer.add_publisher(faq_publisher, manage_add_faq_publisher_edit)
