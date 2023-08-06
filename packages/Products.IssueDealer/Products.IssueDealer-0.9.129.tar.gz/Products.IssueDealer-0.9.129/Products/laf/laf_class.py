from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from laf_property import laf_property
import utilities
from laf_bootstrap import laf_bootstrap

class laf_class(BTreeFolder2, laf_bootstrap):
    """Simple class used to deal with user created classes."""

    meta_type = 'LAF Class'

    index_html = PageTemplateFile('www/laf_index.pt', globals())
    edit = PageTemplateFile('www/edit.pt', globals())

    def __init__(self, id):
        BTreeFolder2.__init__(self, id)
        self.title = 'LAF Class'

    def get_editable_properties(self):
        """Returns the editable properties."""
        return laf_bootstrap.get_editable_properties(self) + (
		{'title':'Enabled', 'id':'enabled', 'type':'boolean', 'description':'Whether or not this class is enabled', 'required':1,
			'value':getattr(self.aq_base, 'enabled', utilities.get_type_default('boolean'))
		},
	)

    def get_class_editable_properties(self):
        """Returns a list of the editable properties."""
        properties = []
        for property in self.get_contained_objects('LAF Property'):
            properties.append({
		'title':property.title,
		'id':property.id,
		'type':property.type,
		'description':'',
		'required':property.required,
		})
        return list(laf_bootstrap.get_editable_properties(self)) + properties

    def get_properties(self):
        """Returns the contained LAF properties."""
        return self.get_contained_objects('LAF Property')

    def get_addable_types(self):
        """Returns the addable types."""
        types = []
        for type in map(lambda x: x[0], utilities.types):
            types.append({'url':'./add_property?type=' + type, 'title':type.capitalize() + ' property'},)
        return types

    def add_property(self, type='line'):
        """Adds a LAF property."""
        assert type in map(lambda x: x[0], utilities.types)
        laf_property_instance = laf_property(self.get_unique_id(), type)
        self._setObject(laf_property_instance.id, laf_property_instance)
        self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + laf_property_instance.id + '/edit')

InitializeClass(laf_class)
