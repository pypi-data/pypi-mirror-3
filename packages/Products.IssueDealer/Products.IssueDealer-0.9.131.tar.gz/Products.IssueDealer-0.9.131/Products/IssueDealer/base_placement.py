import AccessControl
import permissions as id_permissions
from DateTime import DateTime
from Globals import InitializeClass

class base_placement:

    security = AccessControl.ClassSecurityInfo()

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_order')
    def render_order(self):
        """Renders links to changing the Issue's order."""
        if self.get_user_preferences().sort_on == 'get_order':
            return  '&nbsp;&nbsp;&nbsp;' + self.create_hyperlink(self.absolute_url() + '/move_down', '&#8595;&#8595;', escape=0) + \
              '&nbsp;' + self.create_hyperlink(self.absolute_url() + '/move_up', '&#8593;&#8593;', escape=0) + '&nbsp;&nbsp;&nbsp;'
        else:
            return  '&nbsp;&nbsp;&nbsp;' + '&#8593;&#8593;'+ '&nbsp;' + '&#8595;&#8595;' + '&nbsp;&nbsp;&nbsp;'

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'move_down')
    def move_down(self, step=1):
        """Moves self down on the list."""
        parent = self.getParentNode()
	objects = parent.get_filtered_objects(meta_type='Issue')
        order = map(lambda x: x.id, objects)
        index = order.index(self.id)
        next = index + int(step)
        if next == len(order):
            pass
        else: 
            order[index] = order[next]
            order[next] = self.id
            parent.order = order
            parent[parent.order[index]].index_object()
            parent[parent.order[index]].modified = DateTime()
            parent[parent.order[next]].index_object()
            parent[parent.order[next]].modified = DateTime()
        self.REQUEST.RESPONSE.redirect(self.REQUEST['HTTP_REFERER'])

    # Untested
    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'move_up')
    def move_up(self, step=1):
        """Moves self up on the list."""
        parent = self.getParentNode()
	objects = parent.get_filtered_objects(meta_type='Issue')
        order = map(lambda x: x.id, objects)
        index = order.index(self.id)
        previous = index - int(step)
        if not index:
            pass
        else: 
            tmp = order[previous]
            order[previous] = order[index]
            order[index] = tmp
        parent.order = order
        parent[parent.order[index]].index_object()
        parent[parent.order[index]].modified = DateTime()
        parent[parent.order[previous]].index_object()
        parent[parent.order[previous]].modified = DateTime()
        self.REQUEST.RESPONSE.redirect(self.REQUEST['HTTP_REFERER'])

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'get_order')
    def get_order(self):
        """Returns the order of the object."""
        try:
            return self.getParentNode().order.index(self.id)
        except ValueError:
            return -1

InitializeClass(base_placement)