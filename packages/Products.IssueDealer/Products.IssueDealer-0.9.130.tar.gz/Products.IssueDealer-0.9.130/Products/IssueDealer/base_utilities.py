class proxy:
    """Proxies catalog brains."""

    def __init__(self, object):
        self.object = object
        self._object = None

    def __getattr__(self, name):
        if hasattr(self.object.aq_base, name):
            return getattr(self.object, name)
        else:
            if name in ('catalog_search', 'REQUEST'):
                return getattr(self.object, name)
            if not self._object:
                self._object = self.object.getObject()
                #print 'loading object for', self.object.id, self.object.meta_type, name
            return getattr(self._object, name)

    def getObject(self):
        """Hackish way to deal with restricted getObject in > Zope 2.7.x"""
        obj = self.object.aq_parent.unrestrictedTraverse(self.object.getPath())
        if not obj:
            print self.object.getPath(), self.getPath()
            obj = self.REQUEST.resolve_url(self.getPath())
        return obj

class lazy:
    """Wrapper around catalog search results."""

    def __init__(self, results, reverse=0):
        self.results_ = results
        self.reverse_ = reverse

    def __add__(self, other):
        return lazy(self.results_ + other.results_, reverse=self.reverse_)

    def __getattr__(self, name):
        return getattr(self.results_, name)

    def __getitem__(self, index):
        if self.reverse_:
            if index < 0:
                index += len(self)
            if abs(index) > len(self) - 1: raise IndexError, index
            return proxy(self.results_[(len(self) - 1) - index])
        else:
            return proxy(self.results_[index])

    def __getslice__(self, start, end):
        if end > len(self):
            end = len(self)
        return map(self.__getitem__, range(start, end))

    def reverse(self):
        return lazy(self.results_, not self.reverse_)

def call(self, object):
    """Calls the object, if necessary."""
    if callable(object): return object()
    else: return object

class tree_node:
    __allow_access_to_unprotected_subobjects__ = 1
    def __init__(self, object, expanded, has_children):
        self.object = object
        self.expanded = expanded
        self.has_children = has_children

class unprotected:
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, object):
        self._object = object

    def __getattr__(self, name):
        return getattr(self._object, name)

def tree_get_objects(object, objects, levels, current_level, expanded):
    """Returns objects slated for viewing in the tree."""
    if levels and call(object, object.get_level) > current_level + levels:
        return []
    for object_ in object.get_filtered_objects(meta_type=['Issue', 'Relation']):
        if object_.id in expanded or (levels + 1) > call(object, object.get_level):
            expanded_ = 1
        else:
            expanded_ = 0
        if object_.get_filtered_objects(meta_type=['Issue', 'Relation']):
            has_children = 1
        else:
            has_children = 0
        objects.append(tree_node(object_, expanded_, has_children))
        if expanded_:
            tree_get_objects(object_, objects, levels, current_level, expanded)
