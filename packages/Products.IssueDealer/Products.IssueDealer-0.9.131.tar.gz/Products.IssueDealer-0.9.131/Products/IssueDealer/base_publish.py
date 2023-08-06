import AccessControl
import permissions as id_permissions
from Globals import InitializeClass

class base_publish:

    security = AccessControl.ClassSecurityInfo()

    def publish_multiple_submit(self, publisher, ids=()):
        """Publishes issues directly."""
        publisher = self.get_issue_dealer()[publisher]
        for id in ids:
            publisher.publish_directly(issue=self.get_object(id))
        self.get_response().redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.publish_issues, 'publish_submit')
    def publish_submit(self, publisher=None, REQUEST=None):
        """Publishes the Issue in publisher."""
        result = self.get_issue_dealer()[publisher].publish_issue(self)
        if result:
            return result
        else:
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect(self.get_admin_url())

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_publisher_types')
    def get_publisher_types(self, publisher=None, REQUEST=None):
        """Returns a sequence of dictionaries, describing available publishers."""
        return self.publishers_

    security.declareProtected(id_permissions.view_issue_dealer, 'published_in')
    def published_in(self):
        """Returns a list of publishers self is published in."""
        try:
            return map(lambda x: x.get_publisher().id, self.catalog_search(get_published_ids=self.id))
        except AttributeError:
            return []
        except KeyError:
            return []

InitializeClass(base_publish)
