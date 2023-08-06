from pyson.schemas.schema_class import Schema
from pyson.schemas.util import get_schemas

class _SchemaL(Schema):
    INFO_ATTRIBUTES = Schema.INFO_ATTRIBUTES + [ 'validation_list' ]
    def __init__(self, *args, **kwds):
        # Save list of validators
        validators = []
        cls = type(self)
        for v in args:
            v = self.as_schema(v)
            if isinstance(v, cls):
                validators.extend(v.validation_list)
            else:
                validators.append(v)
        self.validation_list = validators
        super(_SchemaL, self).__init__(**kwds)

        # Save default value
        if not hasattr(self, 'default'):
            for v in self.validation_list:
                try:
                    self.default = v.default
                    break
                except AttributeError:
                    pass

class AND(_SchemaL):
    '''
    Logical **and** or between two schemas.
    
    Examples
    --------
    
    >>> from pyson.schemas import *
    >>> AND(Int(), Cte(42)).is_valid(42)
    True
    >>> (Int() & Cte(42)).is_valid(12)
    False
    '''

    name = '<and>'

    def validate(self, obj, **kwds):
        kwds.pop('full_errors')
        for v in self.validation_list:
            if not v.is_valid(obj, **kwds):
                raise self.ValidationError("%s object is not a valid '%s'" % (type(obj), type(v).__name__))



class OR(_SchemaL):
    '''
    Logical **or** between two schemas.
    
    Examples
    --------
    
    >>> from pyson.schemas import *
    >>> OR(Int(), Real()).is_valid(42)
    True
    >>> (Int() | Str()).is_valid(42.0)
    False
    '''

    def validate(self, obj, **kwds):
        kwds.pop('full_errors', __debug__)
        for v in self.validation_list:
            if v.is_valid(obj, **kwds):
                return
        v_json_types = ', '.join(set(type(v).__name__ for v in self.validation_list))
        raise self.ValidationError("%s object is none of the json_types: '%s'" % (type(obj), v_json_types))

# Save specialized schemas into the Schema class
Schema.OR_SCHEMA = OR
Schema.AND_SCHEMA = AND

__all__ = get_schemas(globals())
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
