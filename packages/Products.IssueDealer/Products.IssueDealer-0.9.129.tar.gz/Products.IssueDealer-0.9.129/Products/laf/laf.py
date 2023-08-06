from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Globals import InitializeClass, DTMLFile
import config
import utilities
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from laf_bootstrap import laf_bootstrap
from laf_class import laf_class
from laf_property import laf_property
import time

def _create_index(self, catalog, id, type):
    if type == 'ZCTextIndex':
        catalog.manage_addIndex(id, type, utilities.simple(doc_attr='',
                                     index_type='Cosine Measure',
                                     lexicon_id='lexicon'),)
    else:
        catalog.manage_addIndex(id, type)

class laf(BTreeFolder2, laf_bootstrap):
    """Lightweight application framework."""

    meta_type = 'LAF'

    index_html = PageTemplateFile('www/laf_index.pt', globals())
    edit = PageTemplateFile('www/edit.pt', globals())
    style = DTMLFile('www/style.css', globals())

    def __init__(self, id, title='Lightweight application framework'):
        BTreeFolder2.__init__(self, id=id)
        self.title = title

    def get_editable_properties(self):
        """Returns the editable properties."""
        return laf_bootstrap.get_editable_properties(self) + ()

    def get_properties(self):
        """Returns a list of the editable properties."""
        properties = []
        for property in self.objectValues('LAF Property'):
            properties.append({
		'title':property.title,
		'id':property.id,
		'type':property.type
		})
        return properties

    def get_classes(self):
        """Returns the contained LAF classes."""
        return self.get_contained_objects('LAF Class')

    def get_catalog(self):
        """Returns the catalog."""
        return getattr(self, config.catalog_name)

    def create_index(self, id, type):
        """Creates an index."""
        catalog = self.get_catalog()
        index = catalog._catalog.indexes.get(id, None)
        if index is not None:
            if index.meta_type != type:
                catalog.manage_delIndex(id)
                _create_index(self, catalog, id, type)
        else:
            _create_index(self, catalog, id, type)

    def regenerate_indexes(self, REQUEST=None):
        """Generates indexes, if necessary."""
        properties = []
        for laf_class_instance in self.get_classes():
            properties.extend(laf_class_instance.get_properties())
        for property in properties:
            self.create_index(property.id, property.get_index_type())
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())

    def get_addable_types(self):
        """Returns the addable types."""
        return ({'url':'./add_class', 'title':'Class'},)

    def get_laf(self):
        """Returns the LAF root."""
        return self

    def get_unique_id(self):
        """Returns a unique identifier."""
        try:
            return self.get_laf().getParentNode().get_unique_id()
        except AttributeError:
            integer, float = str(time.time()).split('.')
            time.sleep(0.01) # Make somewhat sure we're not getting similar IDs
            return integer + 'X' + float

    def add_class(self):
        """Adds a LAF class."""
        laf_class_instance = laf_class(self.get_unique_id())
        self._setObject(laf_class_instance.id, laf_class_instance)
        # Make sure we're getting a persisted object
        laf_class_instance = getattr(self, laf_class_instance.id)
        self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + laf_class_instance.id + '/edit')

InitializeClass(laf)
