from pyson.schemas.schema_class import Schema
from pyson.schemas.util import get_schemas
from pyson.types import is_integer, is_real, is_boolean, is_number

class Number(Schema):
    '''
    Examples
    --------
    
    >>> Number().is_valid(42.0)
    True
    >>> Number().is_valid(42)
    True
    >>> Number().is_valid('Forty two')
    False
    '''

    def validation_function(self, obj, **kwds):
        return is_number(obj)

class Int(Schema):
    '''
    Examples
    --------
    
    >>> Int().is_valid(42)
    True
    >>> Int().is_valid('Forty two')
    False
    '''
#    INFO_ATTRIBUTES = Schema.INFO_ATTRIBUTES + [ 'range' ]

    def validation_function(self, obj, **kwds):
#        if self.range is not None:
#            a, b = self.range
#            return isinstance(obj, json_types.Int) and (a <= obj <= b)
        return is_integer(obj)

class Real(Schema):
    '''
    Examples
    --------
    
    >>> Real().is_valid(42.0)
    True
    >>> Real().is_valid(42)
    False
    '''
    def validation_function(self, obj, **kwds):
        return is_real(obj)

class Bool(Schema):
    '''
    Validate boolean objects.
    
    Example
    -------
    
    >>> Bool().validate(True)
    >>> Bool().validate(0)
    Traceback (most recent call last):
    ...
    ValidationError: <type 'int'> object is not a valid 'Bool'
    '''

    def validation_function(self, obj, **kwds):
        return is_boolean(obj)

    @classmethod
    def from_string(cls, obj):
        try:
            return { 'true': True, 'false': False }[obj.lower()]
        except KeyError:
            raise ValueError("invalid boolean: '%s'" % obj)

__all__ = get_schemas(globals())
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
