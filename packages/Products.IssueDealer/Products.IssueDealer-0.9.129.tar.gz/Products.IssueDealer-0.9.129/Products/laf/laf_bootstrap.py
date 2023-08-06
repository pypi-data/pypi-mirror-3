from Globals import InitializeClass
import widgets
import utilities
from cgi import escape
from id_compatability import id_compatability

class laf_bootstrap(id_compatability):
    """Class used to bootstrap LAF classes."""

    def get_editable_properties(self):
        """Returns the editable properties."""
        return (
		{'title':'Title', 'id':'title', 'type':'line', 'description':'The title of this instance', 'required':1,
			'value':getattr(self.aq_base, 'title', utilities.get_type_default('line'))},
	)

    def get_form_properties(self):
        """Returns a list of properties for form editing."""
        if self.REQUEST.has_key('properties_with_failures'):
            return self.REQUEST['properties_with_failures']
        properties = self.get_editable_properties()
        for property in properties:
            if not property.has_key('value'):
                property['value'] = getattr(self.aq_base, property['id'], utilities.get_type_default(property['type']))
            property['widget'] = getattr(widgets, property['type'])(property['id'], property['value'])
            property['failure_message'] = ''
        return properties

    def validate(self, property, value):
        """Validates the propety."""
        if property['required']:
            if not value.strip():
                return 0, 'This field needs input'
        return utilities.validate(property['type'], value)

    def convert(self, property, value):
        """Validates the propety."""
        return utilities.convert(property['type'], value)

    def after_successful_edit(self):
        """Called after a successful edit."""
        pass

    def edit_submit(self, REQUEST):
        """Used for submitting an edit screen."""
        failed = 0
        properties = self.get_editable_properties()
        for property in properties:
            try:
                value = REQUEST[property['id']]
                status, message = self.validate(property, value)
                if status != 1:
                    failed += 1
                    property['failure_message'] = message
                else:
                    value = self.convert(property, value)
                    setattr(self, property['id'], value)
                property['widget'] = getattr(widgets, property['type'])(property['id'], value)
            except AttributeError:
                # In case a class is updated between edit and submit
                raise
        if failed:
            REQUEST.set('properties_with_failures', properties)
            return self.edit(properties_with_failures=properties, REQUEST=REQUEST, RESPONSE=REQUEST.RESPONSE)
        else:
            self.after_successful_edit()
            REQUEST.RESPONSE.redirect(self.absolute_url())

    def get_contained_objects(self, *a, **kw):
        """Returns contained objects."""
        return filter(lambda x: not x.deleted, self.objectValues(*a, **kw))

InitializeClass(laf_bootstrap)
