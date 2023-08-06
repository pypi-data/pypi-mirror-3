from laf_object import laf_object

def add_laf_object(self, laf_class):
    """Adds a LAF object."""
    laf = self.laf
    id = laf.get_unique_id()
    laf_object_instance = laf_object(id, laf_class)
    self._setObject(id, laf_object_instance)
    return getattr(self, id)