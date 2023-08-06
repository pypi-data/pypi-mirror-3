from Globals import InitializeClass
import AccessControl
import permissions as id_permissions
from Products.laf.laf_object import laf_object
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from base import base
from issue import issue

class id_laf_object(laf_object, base):
    """Custom laf object."""

    def __init__(self, id, klass):
        laf_object.__init__(self, id, klass)

    meta_type = 'ID LAF Object'
    index_html = PageTemplateFile('skins/issue_dealer/issue_dealer_product_index.pt', globals())
    edit = PageTemplateFile('skins/issue_dealer/laf_object_edit.pt', globals())

    security = AccessControl.ClassSecurityInfo()
    security.declareProtected(id_permissions.view_issue_dealer, 'index_html', 'render_breadcrumbs', 'get_title', 'render_title')
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'edit')

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'manage_add_issue')
    manage_add_issue = issue.manage_add_issue
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'manage_add_issue_edit')
    manage_add_issue_edit = issue.manage_add_issue_edit

    # Things we need directly from ID
    render_breadcrumbs = base.render_breadcrumbs

    def get_title(self):
        """Returns the title."""
        return getattr(self.aq_base, 'title', '').strip() or '[No title]'

    def render_contents(self):
        " "
        return "CONTENTS"

    render_title = get_title

InitializeClass(id_laf_object)
