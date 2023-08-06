import AccessControl, utilities, functions, permissions, zLOG
from Globals import InitializeClass

class publisher:
    """Mixin class for publishers."""

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(permissions.view_issue_dealer, 'get_publisher')
    def get_publisher(self):
        " "
        return self

    security.declareProtected(permissions.publish_issues, 'publish_directly')
    def publish_directly(self, issue=None, REQUEST=None):
        """Publishes the Issue directly, without asking anything about how it should be published."""
        if issue is None:
            issue = self.get_object(REQUEST['id']).getObject()
        self.publish_issue(issue)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(issue.get_admin_url())

    security.declareProtected(permissions.view_issue_dealer, 'get_published_issues')
    def get_published_issues(self, start=None, size=None, reverse=None):
        """Returns a list of the published issues."""
        issues = []
        published = self.published[:]
        if reverse:
            published.reverse()
        for id, date in published[start:]:
            issues.append({'issue':self.get_object(id), 'date':date, 'id':id})
            if len(issues) == size: break
        return issues

    security.declareProtected(permissions.view_issue_dealer, 'get_published_ids')
    def get_published_ids(self):
        """Returns a list of published ids."""
        return map(lambda x: x[0], self.published)

    security.declareProtected(permissions.view_issue_dealer, 'get_number_of_published_issues')
    def get_number_of_published_issues(self):
        """Returns the number of published issues."""
        return len(self.published)

    security.declareProtected(permissions.view_issue_dealer, 'get_published_id')
    def get_published_id(self, issue):
        """Returns the ID with which the issue has been previously published."""
        for x in utilities.reverse(self.published):
            if x[0] == issue.id:
                return x[1]
        else:
            return issue.id

    security.declarePublic('been_published')
    def been_published(self, issue):
        """Returns a truth value if issue has been published before."""
        published_ids = self.get_published_ids()
        if type(issue) is type(''):
            issue = self.get_object(issue)
        if issue.id in published_ids:
            return 1
        objects = self.catalog_search(get_referenced_ids=issue.id)
        for object in objects:
            if object.id in published_ids:
                return 1
        return 0

InitializeClass(publisher)

class relation_publisher(publisher):
    """Publisher that uses relations as part of the publishing scheme."""

    security = AccessControl.ClassSecurityInfo()
    state = type = 'N/A'

    security.declareProtected(permissions.publish_issues, 'publish_issue')
    def publish_issue(self, issue):
        """Publishes the issue to the weblog."""
        relation = self.manage_add_relation.im_func(self, relation_=issue.id)
        issue.index_object()

    security.declareProtected(permissions.view_issue_dealer, 'get_published_ids')
    def get_published_ids(self):
        "Returns the published ids."
        result = map(lambda x: x.relation, self.get_objects(meta_type='Relation', sort_order='reverse', deleted=0))
        result.extend(map(lambda x: x.id, self.catalog_search(get_parent_ids=self.id, meta_type='Issue')))
        return result

    security.declareProtected(permissions.view_issue_dealer, 'get_published_issues')
    def get_published_issues(self, start=0, size=9999999, reverse=None):
        """Returns a list of the published issues."""
        issues = []
        if reverse:
            sort_order = 'reverse'
        else:
            sort_order = ''
        relations = self.get_objects(meta_type='Relation', sort_on='created', sort_order=sort_order, deleted=0)
        for relation in relations[start:size]:
            issue = functions.get_related_object(relation)
            issues.append({'issue':issue, 'date':relation.created, 'relation':relation, 'id':issue.id,
                           'created':issue.created, 'creator':issue.creator, 'get_parent_ids':issue.get_parent_ids})
            if len(issues) == size: break
        return issues

    security.declareProtected(permissions.publish_issues, 'remove')
    def remove(self, ids=[]):
        """Removes the specified issues from the weblog."""
        for id in ids:
            self.get_object(id).delete()
        self.REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declarePublic('get_published_issue')
    def get_published_issue(self, id):
        """Retrieves published issues."""
        if self.been_published(id):
            return self.get_object(id)
        else:
            raise 'Unauthorized'

    security.declareProtected(permissions.view_issue_dealer, 'render_importance')
    def render_importance(self):
        " "
        return "N/A"

InitializeClass(relation_publisher)

class catalog:

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(permissions.add_edit_issues_and_relations, 'reindex_all')
    def reindex_all(self):
        for object in self.objectValues():
            # Workaround for a nasty bug
            if hasattr(object.aq_base, 'reindex_all'):
                object.reindex_all()
            else:
                zLOG.LOG('IssueDealer', zLOG.ERROR, 'object %s does not have reindex_all' % str(object.getPhysicalPath()))
        if hasattr(self.aq_base, 'index_object'):
            self.index_object()

InitializeClass(catalog)