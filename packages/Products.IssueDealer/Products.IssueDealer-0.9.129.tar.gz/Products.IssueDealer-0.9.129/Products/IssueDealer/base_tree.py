import AccessControl
import permissions as id_permissions
import base_utilities
from Globals import InitializeClass

class base_tree:

    security = AccessControl.ClassSecurityInfo()

    # Untested
    security.declareProtected(id_permissions.view_issue_dealer, 'render_html_title_and_link_tree')
    def render_html_title_and_link_tree(self):
        """Renders a link for tree browsing."""
        return self.render_html_title_and_link(tree=1)

    security.declareProtected(id_permissions.view_issue_dealer, 'issue_tree_expanded')
    def issue_tree_expanded(self, REQUEST):
        """Redirects to an expanded tree view."""
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/issue_tree?' + \
                                  'expand_all:int=1&show_contents:int=1')

    security.declareProtected(id_permissions.view_issue_dealer, 'generate_category_tree')
    def generate_category_tree(self, object=None):
        """Generates a tree for category selection."""
        if object:
            object = self.get_object(object)
        return self.generate_tree(levels=self.get_user_preferences().link_category_level, object=object)

    security.declareProtected(id_permissions.view_issue_dealer, 'generate_tree')
    def generate_tree(self, object=None, levels=None):
        """Generates a tree for the tree view."""
        levels = levels or self.get_level()
        object = object or self
        request = self.get_request()
        objects = []
        try:
            levels = request['SESSION']['tree_levels_%s' % object.id]
        except:
            levels = request['SESSION']['tree_levels_%s' % object.id] = levels
        try:
            expanded = request['SESSION']['tree_expanded_%s' % object.id]
        except:
            request['SESSION']['tree_expanded_%s' % object.id] = []
            expanded = []
        if request.has_key('expand'):
            expanded.append(request['expand'])
        if request.has_key('collapse'):
            try:
                expanded.remove(request['collapse'])
            except ValueError:
                # Closing a node expanded by level
                pass
        request['SESSION']['tree_expanded_%s' % object.id] = expanded
        if request.has_key('expand_level'):
            levels += 1
        elif request.has_key('collapse_level'):
            if levels > 1:
                levels -= 1
        request['SESSION']['tree_levels_%s' % object.id] = levels
        issue_dealer_level = self.get_issue_dealer().get_level()
        current_level = self.get_level()
        base_utilities.tree_get_objects(object, objects, levels, current_level, expanded)
        levels = map(lambda x, call=self.call.im_func: call(x.object, x.object.get_level) - current_level, objects)
        try:
            lowest_level = max(levels)
        except ValueError:
            lowest_level = 0
        return objects, current_level, lowest_level

InitializeClass(base_tree)