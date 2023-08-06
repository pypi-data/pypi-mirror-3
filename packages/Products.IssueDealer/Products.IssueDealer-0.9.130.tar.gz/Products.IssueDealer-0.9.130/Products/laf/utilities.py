import validators, converters

class simple:
    """Simple class for emulating form records."""

    def __init__(self, **keywords):
        for key, value in keywords.items():
            setattr(self, key, value)

types = (
		# Type name, default, index type
		('integer', 0, 'FieldIndex', 'An integral value, such as: 0, -8, 99 or 100000'),
		('float', 0.0, 'FieldIndex', 'A floating point value, such as: 0.1, 1000101.0 or 99991.0'),
		('line', '', 'ZCTextIndex', 'One line of text, such as: this is a line'),
		('text', '', 'ZCTextIndex', 'One or more lines of text'),
		('boolean', 0, 'FieldIndex', 'A truth value, yes or no'),
		('date', '1970-01-01', 'FieldIndex', 'A date, such as: 2001-12-31 or 2001-12-31 14:33'),
		('email', '', 'FieldIndex', 'An email address, such as morten@nidelven-it.no'),
)

def get_type_default(type):
    """Returns the type default."""
    for type_ in types:
        if type_[0] == type:
            return convert(type, type_[1])

def get_index_type(type):
    """Returns the index type of the property type."""
    for type_ in types:
        if type_[0] == type:
            return type_[2]
    else:
        raise NameError, type

def validate(type, value):
    """Validates the value."""
    return getattr(validators, type)(value)

def convert(type, value):
    """Converts the value to its correct form."""
    return getattr(converters, type)(value)

def get_parents(self, stop=None):
    reference = self
    parents = [self]
    while 1:
        try:
            parent = reference.getParentNode()
        except AttributeError:
            # We're at the end of the line
            break
        parents.append(parent)
        if stop:
            if stop(parent):
                break
        reference = parent
    return parents
