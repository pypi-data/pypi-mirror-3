from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Globals import InitializeClass
import widgets
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import utilities
from laf_bootstrap import laf_bootstrap
from Products.ZCatalog import CatalogPathAwareness

class laf_object(BTreeFolder2, laf_bootstrap, CatalogPathAwareness.CatalogAware,):
    """Simple class used to deal with user created content."""

    meta_type = 'LAF Object'

    edit = PageTemplateFile('www/edit.pt', globals())

    def __init__(self, id, klass):
        BTreeFolder2.__init__(self, id)
        self.klass = klass

    def _get_class(self):
        """Returns the class object."""
        return getattr(self.laf, self.klass)

    def get_editable_properties(self):
        """Hook to get the editable properties."""
        return self._get_class().get_class_editable_properties()

    def validate_property(self, id, value):
        """Used to validate the value of a property."""
        return self._get_class()[id].validate(value)

    def convert_property(self, name, value):
        """Used to convert the value of a property."""
        return self._get_class()[id].convert(value)

    def after_successful_edit(self):
        " "
        self.index_object()

InitializeClass(laf_object)
