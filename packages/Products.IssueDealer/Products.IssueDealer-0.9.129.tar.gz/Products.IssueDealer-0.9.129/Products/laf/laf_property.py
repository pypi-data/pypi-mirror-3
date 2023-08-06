from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Globals import InitializeClass
import validators, converters
from DateTime import DateTime
from laf_bootstrap import laf_bootstrap
import utilities

from utilities import types, get_type_default, get_index_type, validate, convert

class laf_property(BTreeFolder2, laf_bootstrap):
    """Simple class used to deal with user created properties."""

    meta_type = 'LAF Property'

    def __init__(self, id, type):
        BTreeFolder2.__init__(self, id)
        self.type = type
        self.title = convert('line', '')
        self.description = convert('text', '')
        self.required = convert('boolean', 0)

    def get_editable_properties(self):
        """Returns the editable properties."""
        return (
		{'title':'Title', 'id':'title', 'type':'line', 'description':'', 'required':1,
			'value':getattr(self.aq_base, 'title', utilities.get_type_default('line'))},
		{'title':'Required', 'id':'required', 'type':'boolean', 'description':'', 'required':1,
			'value':getattr(self.aq_base, 'required', utilities.get_type_default('boolean'))},
		{'title':'Default value', 'id':'default', 'type':self.type, 'description':'The default value', 'required':0,
			'value':getattr(self.aq_base, 'default', utilities.get_type_default(self.type))},
		{'title':'Description', 'id':'description', 'type':'text', 'description':'', 'required':0,
			'value':getattr(self.aq_base, 'description', utilities.get_type_default('text'))},
	)

    def get_default_value(self):
        """Returns the default value."""
        return getattr(self.aq_base, 'default', get_type_default(self.type))

    def get_index_type(self):
        """Returns the index type."""
        return get_index_type(self.type)

    def get_addable_types(self):
        """Returns the addable types."""
        return ()

    def after_successful_edit(self):
        """Called after a successful edit."""
        self.get_laf().regenerate_indexes()

InitializeClass(laf_property)
