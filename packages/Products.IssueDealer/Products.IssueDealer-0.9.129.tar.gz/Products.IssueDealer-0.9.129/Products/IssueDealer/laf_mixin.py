from Globals import InitializeClass
import AccessControl
import permissions as id_permissions
from Products.laf import laf_bridge
from Products.laf.laf_object import laf_object
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

def add_id_laf_object(self, laf_class):
    " "
    laf = self.laf
    id = laf.get_unique_id()
    from laf_object import id_laf_object
    id_laf_object_instance = id_laf_object(id, laf_class)
    self._setObject(id, id_laf_object_instance)
    return getattr(self, id)

class laf_mixin:

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(id_permissions.add_edit_issues_and_relations, 'add_laf_object')
    def add_laf_object(self, id, REQUEST=None):
        """Adds a LAF class."""
        object = add_id_laf_object(self, id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(object.absolute_url() + '/edit')

    security.declareProtected(id_permissions.view_issue_dealer, 'get_laf_objects')    
    def get_laf_objects(self):
        """Returns the contained LAF objects."""
        return self.objectValues('ID LAF Object')

InitializeClass(laf_mixin)
