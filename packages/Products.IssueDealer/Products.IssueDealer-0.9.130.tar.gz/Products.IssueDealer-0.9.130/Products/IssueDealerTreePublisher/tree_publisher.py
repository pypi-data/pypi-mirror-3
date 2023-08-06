from Products.IssueDealerWebDAVPublisher import webdav_publisher
from Globals import InitializeClass
from Products import IssueDealer
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

def manage_add_tree_publisher_edit(self, id=None, title='', REQUEST=None):
    """Add a Tree publisher."""
    if id is None:
        id = self.get_unique_id()
    tree_publisher_ = tree_publisher(id, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id())
    self._setObject(id, tree_publisher_)
    tree_publisher_ = self._getOb(id)
    tree_publisher_.version = self.get_issue_dealer().filesystem_version
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')
    else:
        return tree_publisher_

class tree_publisher(webdav_publisher.webdav_publisher):
    "Little class"

    meta_type = "Tree publisher"

    publish = PageTemplateFile('publish.pt', globals())    

    def publish_webdav(self, issue, id, add_local_images=None, add_external_images=None, contents=None):
        " "
        issue = self.get_object(issue)
        contents = issue.tree_publisher_view()
        return webdav_publisher.webdav_publisher.publish_webdav.im_func(self, issue.id, id,
		add_local_images=add_local_images,
		add_external_images=add_external_images,
		contents=contents)

InitializeClass(tree_publisher)

from Products.IssueDealer.issue_dealer import issue_dealer, base, issue

issue.issue.tree_publisher_view = PageTemplateFile('tree.pt', globals())
issue_dealer.manage_add_tree_publisher_edit = manage_add_tree_publisher_edit
issue_dealer.all_meta_types = issue_dealer.all_meta_types + [
    {'visibility': 'Global',
     'interfaces': [],
     'action': 'manage_add_tree_publisher_edit',
     'permission': 'Add Tree publisher',
     'name': 'Tree publisher',
     'product': 'Issue Dealer',
     'instance': ''},]
IssueDealer.add_publisher(tree_publisher, manage_add_tree_publisher_edit)

