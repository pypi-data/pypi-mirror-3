from __future__ import absolute_import
from propertylib import auto_property, default_property
from pyson.schemas.util import get_schemas
from pyson.serialize import loads
from pyson.types import is_object_t, is_container_t

#===============================================================================
#                             Base Schema class
#===============================================================================
class Schema(object):
    # Constants ----------------------------------------------------------------
    DISPLAY_FULL_ERRORS = __debug__
    INSTANCE_COUNTER = 0
    NULL = None

    # Special attributes and meta information ----------------------------------
    INFO_ATTRIBUTES = ['default', 'parent', 'null', 'name', 'desc', 'label',
                       'label_plural', 'is_optional', 'is_ref', 'is_unique',
                       'ordering_index']
    EXTRA_ATTRIBUTES = [ 'meta', 'default_or_null' ]

    class META(object):
        def update_attrs(self, dic):
            for k, v in dic.items():
                setattr(self, k, v)

    # Error Classes ------------------------------------------------------------
    class ValidationError(ValueError):
        '''Exception raised when object does not validate.'''
        pass

    class ValidationIndexError(ValidationError):
        pass

    # Schemas ------------------------------------------------------------------
    OBJECT_SCHEMA = None
    ARRAY_SCHEMA = None
    CTE_SCHEMA = None
    AND_SCHEMA = None
    OR_SCHEMA = None

    #===========================================================================
    # Initialization
    #===========================================================================
    def __new__(cls, *args, **kwds):
        if cls is Schema:
            # Choose the constructor from the type of the first argument
            if not args:
                raise TypeError('Schema() takes exactly one positional argument (0 given)')
            tt = type(args[0])

            # Creates templates from container objects
            if is_container_t(tt):
                if is_object_t(tt):
                    return cls.OBJECT_SCHEMA(*args, **kwds)
                else:
                    if not (1 <= len(args[0]) <= 2):
                        raise TypeError('Array() takes one or two positional arguments (%s given)' % len(args[0]))
                    return cls.ARRAY_SCHEMA(*args, **kwds)
            else:
                return cls.CTE_SCHEMA(*args, **kwds)
        else:
            return object.__new__(cls)

    def __init__(self, *args, **kwds):
        """
        Base class for validation of JSON/JSONExt objects. 
        
        Arguments
        ---------
        
        default : JSONExt
            Default value of the field. In most classes, the default value can
            also be set by the first positional argument.
            
        null : JSONExt
            The null value for the field. It is None for most fields, but it
            might make sense to assign a different value.
                
        label : str
            Optional label. Used to print error messages.
            
        desc : str
            Object's description. Useful if one wants to introspect the field.
            
            
        Observations
        ------------
                
        The ability to change the null value of the field is specially useful 
        in Str fields. The default behavior distinguishes "the field is empty" 
        (in which the field evaluates to None) from "the field is filled with 
        an empty string" (in which it is ''). If this distinction is not 
        desirable, one should assign null='', making empty Str fields evaluate 
        to '' rather than None.
        
        The behavior is sometimes similar to defining the default value for the
        field. If an optional field is empty, it will be evaluated to the 
        default value, if a default value exists, otherwise the null value is 
        used. If the field is obligatory, it evaluates to the default value, but 
        if not default value exists, a ValidationError is raised.
        
        Another important difference is that the null value does not need to 
        validate, while the default value must.
        
    
        Example
        -------
        
        Implements a validator that tests if numbers are greater than 3.1415

        >>> from pyson.schemas import *
        >>> class GreaterThanPi(Number):
        ...     def validation_function(self, obj, *args, **kwds):
        ...         try:
        ...             return float(obj) > 3.1415
        ...         except ValueError: 
        ...             return False
        >>>
        >>> GreaterThanPi().is_valid(1)
        False
        >>> GreaterThanPi().is_valid(5)
        True
        >>> GreaterThanPi().is_valid('some string')
        False
        """

        Schema.INSTANCE_COUNTER += 1
        self.ordering_index = Schema.INSTANCE_COUNTER

        # Save and validate the default value
        if len(args) == 1:
            if 'default' in kwds:
                raise TypeError('default value defined twice')
            else:
                self.default = args[0]
        elif len(args) == 0:
            if 'default' in kwds:
                self.default = kwds.pop('default')
        else:
            raise TypeError('Schema() takes one or zero positional arguments (got %s)' % len(args))
        if hasattr(self, 'default'):
            self.validate(self.default)

        # Get other parameters from dictionary
        try:
            kwds['is_unique'] = bool(kwds['is_ref'])
        except KeyError:
            pass
        for k, v in kwds.items():
            if k in self.INFO_ATTRIBUTES:
                setattr(self, k, v)
                del kwds[k]

        # Fill-in the meta attributes
        self.meta = self.META()
        self.meta.update_attrs(kwds)

    #===========================================================================
    # Validation
    #===========================================================================
    def validate(self, obj, **kwds):
        """Raise a ValidationError exception if 'obj' does not conforms to 
        the given JSON-schema.
        
        Arguments
        ---------
        
        obj : JSONExt
            Object to be validated.
        
        implicit_defaults : bool
            If False, it will not validate objects with an empty required  
            field, even if the field has a default value. (default is True)
        
        full_errors : bool
            If True, creates useful error strings for debug purposes. The 
            default value is the Python variable __debug__.
            
        Example
        -------
        
        >>> from pyson.schemas import *
        >>> schema = Schema({ 'name': Str(), 'age?': Int(), 'color': Str('blue') })
        
        # Valid object: nothing happens
        >>> schema.validate({ 'name': 'Arthur'})
        
        # Defaults are filled implicitly, but this can be overridden
        >>> schema.validate({ 'name': 'Arthur'}, implicit_defaults=False)
        Traceback (most recent call last):
         ...
        ValidationError: missing key, '$.color'
        
        # Invalid object: the field 'favorite_color' is not present in the
        # Schema. 
        >>> schema.validate({ 'name': 'Arthur', 'favorite_color': 'Blue' })
        Traceback (most recent call last):
         ...
        ValidationError: invalid key, '$.favorite_color'
        """

        if not self.validation_function(obj, **kwds):
            raise self.ValidationError("%s object is not a valid '%s'" % (type(obj), type(self).__name__))

    def is_valid(self, obj, **kwds):
        """Return True if 'obj' is valid and False otherwise."""

        try:
            kwds.pop('full_errors', True)
            self.validate(obj, full_errors=False, **kwds)
            return True
        except self.ValidationError:
            return False

    def validation_function(self, obj, **kwds):
        raise NotImplementedError

    #===========================================================================
    # Transformations
    #===========================================================================
    @staticmethod
    def as_schema(obj):
        '''
        Return 'Schema(obj)' if other is not a Schema, and return 'obj' otherwise.  
        '''

        if isinstance(obj, type) and issubclass(obj, Schema):
            raise TypeError('needs to instantiate %s class' % obj.__name__)
        elif isinstance(obj, Schema):
            return obj
        else:
            return Schema(obj)

    def copy(self, keep_parent=True):
        '''Deep copy of object.'''

        # Copy object by updating its dict
        new = object.__new__(type(self))
        for k, v in self.__dict__.items():
            setattr(new, k, v)
        new.meta = self.META(**self.meta.__dict__)

        # Update counter
        Schema.INSTANCE_COUNTER += 1
        new.ordering_index = Schema.INSTANCE_COUNTER

        # Save parent
        if not keep_parent:
            new.parent = None
        return new

    def expand_compress(self, is_expand, obj, **kwds):
        # Only container objects must do something when expanding.
        # Most objects simply return themselves.
        if obj is self.null or obj == self.null:
            return self.null

        if kwds.get('validate', False):
            self.validate(obj, **kwds)

        return obj

    def expand(self, obj, **kwds):
        """Return a copy of 'obj' with all optional empty fields assigned to 
        the default value or to null, if not default value exists. 
        
        Observations
        ------------
        
        In most fields, 'null' is mapped to python's None. However, container
        fields Object and Array use respectively {} and [] as the default 'null'
        value. This can be overridden by the keyword argument 'null' on object's
        initialization. 
        
        Example
        -------
        
        Expand the default value
        
        >>> from pyson.schemas import *
        >>> schema = Schema({ 'name': Str(), 'age?': Int(18) })
        >>> schema.expand({ 'name': 'Chips' })
        {u'age': 18, u'name': 'Chips'}
        
        Fill empty entries with null
        
        >>> schema = Schema({ 'name': Str(), 'age?': Int() })
        >>> schema.expand({ 'name': 'Chips' })
        {u'age': None, u'name': 'Chips'}
        """

        return self.expand_compress(True, obj, **kwds)

    def compress(self, obj, **kwds):
        """Return a copy of obj with none of the optional fields that are equal
        to the default values (or null).
        """
        return self.expand_compress(False, obj, **kwds)

    def equals_default(self, obj):
        try:
            return self.default == obj
        except AttributeError:
            return False

    @classmethod
    def from_string(cls, obj):
        try:
            return loads(obj)
        except ValueError as ex:
            msg = "%s: '%s' as %s()" % (ex, obj, cls.__name__)
            raise ValueError(msg)

    #---------------------------------------------------------------------------
    #                             Magical methods
    #---------------------------------------------------------------------------
    def __and__(self, other):
        return self.AND_SCHEMA(self, Schema.as_schema(other))

    def __or__(self, other):
        return self.OR_SCHEMA(self, Schema.as_schema(other))

    def __call__(self, **kwds):
        '''
        Creates copy of self and re-init them. By calling a schema object one
        can create a copy and simultaneously reset any desired property (default
        value, desc, label, etc). 
        
        The default value can only be set explicitly as a keyword argument.
        
        Example
        -------
        
        >>> from pyson.schemas import *
        >>> v1 = Str(null='', label='Some string')
        >>> v2 = v1(label='Other string')
        >>> v1.null == v2.null
        True
        >>> v2.label
        'Other string'
        '''

        new = self.copy()
        for attr, v in kwds.items():
            if attr in new.INFO_ATTRIBUTES:
                setattr(new, attr, v)
            else:
                setattr(new.meta, attr, v)
        return new

    #===========================================================================
    # Object's location within JSON structure 
    #===========================================================================
    def basepath(self, key=None):
        '''
        Location of root's object within the JSON structure. The optional 
        argument 'key' is appended to the returning path.
        '''

        path = []
        node = self
        while node is not None:
            path.append(node.name)
            node = node.parent
        path.reverse()
        if not path[0]:
            path[0] = '$'

        if key is None:
            return '.'.join(path)
        else:
            return '.'.join(path + [str(key)])

    #===========================================================================
    # Properties
    #===========================================================================
    def get_value(self, *args):
        '''
        Return the value of property 'key'.
        
        Example
        -------
        
        >>> from pyson.schemas import *
        >>> sch = Str(null='<empty>', ham='spam')
        >>> sch.get_value('null')
        '<empty>'
        >>> sch.get_value('ham')
        'spam'
        
        # Raises a KeyError if value does not exist
        >>> sch.get_value('foo') #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        KeyError: "<class '...Str'> has no property 'foo'"
        
        # Caller Can provide a default value
        >>> sch.get_value('foo', 'bar')
        'bar'
        
        
        '''
        if len(args) == 1:
            key = args[0]

            # Since args is in the local scope, identity test should always fail
            # if an object from the outer scope is passed.
            # We set default to args to confirm that a second argument was not 
            # set by the caller.
            default = args
        else:
            try:
                key, default = args
            except IndexError:
                raise TypeError('get_value() takes 1 or 2 arguments (%s given)' % len(args))

        try:
            return getattr(self, key)
        except AttributeError:
            try:
                return getattr(self.meta, key)
            except AttributeError:
                if default is args:
                    raise KeyError("%s has no property '%s'" % (type(self), key))
                else:
                    return default

    #===========================================================================
    # Properties
    #===========================================================================
    parent = default_property(None)

    @auto_property
    def null(self):
        return self.NULL

    @auto_property
    def default_or_null(self):
        try:
            return self.default
        except AttributeError:
            return self.null

    name = default_property(u'')
    desc = default_property(u'')

    @auto_property
    def label(self):
        return self.name.title().replace('_', ' ')

    @auto_property
    def label_plural(self):
        return self.label + 's'

    is_optional = default_property(False)

class Cte(Schema):
    '''
    Examples
    --------
    
    >>> Cte(42).is_valid(42)
    True
    >>> Cte(42).is_valid(12)
    False
    '''

    def __init__(self, cte, **kwds):
        self.cte_value = cte
        super(Cte, self).__init__(cte, **kwds)

    def validate(self, obj, **kwds):
        if obj != self.cte_value:
            raise self.ValidationError("expected '%s', got '%s'" % (self.cte_value, obj))

class Anything(Schema):
    '''
    A validator that validates any object. 
    
    Examples
    --------
    
    >>> Anything().is_valid('Forty two')
    True
    >>> Anything().is_valid(42)
    True
    >>> Anything().is_valid(None)
    True
    '''

    def validation_function(self, obj, **kwds):
        return True

class Nothing(Schema):
    '''
    A validator that invalidates all objects.
    
    Examples
    --------
    
    >>> Nothing().is_valid('Forty two')
    False
    >>> Nothing().is_valid(42)
    False
    >>> Nothing().is_valid(None)
    False
    '''
    def validation_function(self, obj, **kwds):
        return False

# Save specialized schemas into the Schema class
Schema.CTE_SCHEMA = Cte

__all__ = get_schemas(globals())
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
