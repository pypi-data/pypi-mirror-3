#-*- coding: utf8 -*-
import collections
import functools
import re
import json
import jsonlib.types as json_types
from chips.cache import dproperty


class Self(Schema):
    pass

#===============================================================================
#                           Container classes
#===============================================================================
class Container(Schema):
    def __init__(self, *args, **kwds):
        if type(self) is Container:
            raise RuntimeError('Container class should not be instantiated directly.')
        else:
            super(Container, self).__init__(*args, **kwds)

    def as_child(self, child):
        '''
        Modify 'child' Schema object to become a child of self.
        '''

        child = self.as_schema(child)
        if not (child.parent is self or child.parent is None):
            name = type(child).__name__
            pname = type(child.parent).__name__
            raise ValueError("'%s' validator already has parent '%s'" % (name, pname))
        child.parent = self
        return child

    def _raise_validation(self, key, value, validator, full_errors):
        if full_errors:
            raise ValidationError("%s object at key '%s' is not a valid '%s'"
                                  % (type(value), self.basepath(key), type(validator).__name__))
        else:
            raise ValidationError

class Object(Container, collections.Mapping):
    NULL = {}
    INFO_ATTRIBUTES = Container.INFO_ATTRIBUTES + [ 'fields', 'validation_keys' ]

    def __init__(self, *args, **kwds):
        '''
        Represents a JSON Object. JSON objects are essentially a dictionary
        in which keys must be strings.
        
        Example
        -------
        
        >>> schema = Object({ 'book': Str(), 'answer': Str() | Cte(42) })
        >>> schema.validate({'book': 'HHGTTG', 'answer': 12})
        Traceback (most recent call last):
        ...
        ValidationError: <type 'int'> object at key '$.answer' is not a valid 'OR'
        '''
        # Read Object-specific keyword arguments
        build_default = kwds.pop('build_default', False)

        # Initialize
        if len(args) == 2:
            schema = args[0]
            args = (args[1],) # default
        elif len(args) == 1:
            schema = args[0]
            args = () # no default
        super(Object, self).__init__(**kwds)

        # Check empty mapping
        if not schema:
            raise ValueError('empty mapping.')

        # Convert validators to schema instances (e.g. dicts, become Objects, 
        # strings and ints become constants, etc)
        for k, v in schema.items():
            schema[k] = Schema.as_schema(v)

        # Validation keys correspond to entries in the form of 'string': Schema().
        # Validation json_types are of the form Schema_1(): Schema_2(), and validates
        # any pair of key, values that conforms to both Schemas. To be a valid
        # JSON object, the key must be a string.
        self.validation_keys = {}
        for k, v in schema.items():
            self.add_item(unicode(k), v)

        # Compute the order each field was created
        self.fields = [ (f.ordering_index, k) for (k, f) in self.validation_keys.items() ]
        self.fields.sort(key=lambda x: x[0])
        self.fields = [ k for (i, k) in self.fields ]

    def validate(self, obj, **kwds):
        full_errors = kwds.get('full_errors', DISPLAY_FULL_ERRORS)
        implicit_defaults = kwds.get('implicit_defaults', True)
        if not implicit_defaults:
            print 'not implicit'

        # Check if obj is a dict
        if not isinstance(obj, json_types.Object):
            raise ValidationError("object of type '%s' is not a mapping." % type(obj).__name__)

        # Validate all objects
        obj_keys = set(obj)
        for key, validator in self.validation_keys.items():
            # Get value from object and check if key exists
            try:
                value = obj[key]
                obj_keys.remove(key)
            except KeyError:
                if validator.is_optional:
                    continue
                elif (not hasattr(validator, 'default')) or (not implicit_defaults):
                    self._raise_missing_key(key, full_errors)
                else:
                    continue

            # Validate value
            try:
                validator.validate(value, **kwds)
            except ValidationError, ex:
                self._raise_validation(key, value, validator, full_errors)

        # Assert obj do not have extra keys
        if obj_keys:
            self._raise_extra_keys(obj_keys, full_errors)

    def expand(self, obj, **kwds):
        expanded = {}
        expanded.update((unicode(k), v) for (k, v) in obj.items())
        for key in self:
            if key not in obj:
                try:
                    value = self[key].expand(obj[key], **kwds)
                except KeyError:
                    value = self.validation_keys[key].default_or_null
                expanded[key] = value
        return expanded

    def compress(self, obj, **kwds):
        '''
        
        obj : Object
        compress_defaults : bool
        
        >>> schema = Schema({ u'hello': Str(u'world!'), 'ham?': Str(u'spam') })
        >>> schema.compress({ u'hello': u'world!', u'ham': u'eggs' })
        {u'ham': u'eggs'}
        
        >>> schema.compress({ u'hello': u'world!' }, compress_defaults=False)
        {u'hello': u'world!'}
        '''

        compress_defaults = kwds.get('compress_defaults', True)
        compressed = {}
        for k, v in obj.items():
            sch = self[k]
            if v == sch.default_or_null:
                if sch.is_optional or compress_defaults:
                    continue
            compressed[unicode(k)] = sch.compress(v, **kwds)
        return compressed

    #===========================================================================
    # Magic methods: support the Mapping protocol
    #===========================================================================
    def __getitem__(self, item):
        return self.validation_keys[item]

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.validation_keys)

    #===========================================================================
    # Auxiliary methods
    #===========================================================================
    def _raise_missing_key(self, key, full_errors):
        if full_errors:
            raise ValidationError("missing key, '%s'" % (self.basepath(key)))
        else:
            raise ValidationError

    def _raise_extra_keys(self, keys, full_errors):
        if full_errors:
            if len(keys) > 1:
                base = self.basepath()
                keys = ', '.join(keys)
                raise ValidationError("invalid keys, '%s.(%s)'" % (base, keys))
            else:
                key = self.basepath(tuple(keys)[0])
                raise ValidationError("invalid key, '%s'" % key)
        else:
            raise ValidationError

    def add_item(self, key, value):
        '''
        Register validator 'value' in given 'key'.
        
        Example
        -------
        
        >>> schema = Object({ 'foo': Str('bar') })
        >>> schema['foo'].parent is schema
        True
        >>> schema['foo'].name
        u'foo'
        >>> schema['foo'].label
        u'Foo'
        '''

        if isinstance(key, json_types.Str):
            newvalue = self.as_child(value)
            newvalue.name = key
            try:
                newvalue.ordering_index = value.ordering_index
            except AttributeError:
                pass

            if key.endswith('?'):
                key = key.rstrip('?')
                newvalue.is_optional = True
            self.validation_keys[key] = newvalue
        else:
            raise TypeError('invalid key of type %s' % type(key))

class Array(Container):
    INFO_ATTRIBUTES = Container.INFO_ATTRIBUTES + [ 'type' ]

    def __init__(self, array_type=None, *args, **kwds):
        '''
        Validator for list-like objects.
        
        Arguments
        ---------
        
        array_type : Schema
            Type of objects in array
         
         
        Examples
        --------
        
        >>> Array().is_valid([])
        True
        >>> Array(Int).is_valid(['one', 'two'])
        False
        '''

        super(Array, self).__init__(*args, **kwds)
        if array_type is None:
            array_type = Anything()
        elif isinstance(array_type, type) and issubclass(array_type, Schema):
            array_type = array_type()
        elif not isinstance(array_type, Schema):
            print array_type
            raise ValueError('type must be a valid schema, got %s' % type(array_type))
        self.type = array_type

    def validate(self, obj, full_errors=__debug__, **kwds):
        if not isinstance(obj, json_types.Array):
            if full_errors:
                raise ValidationError(" %s object is not an Array" % type(obj))
            else:
                raise ValidationError

        v = self.type.validate
        for idx, x in enumerate(obj):
            try:
                v(x, **kwds)
            except ValidationError as ex:
                if full_errors:
                    ValidationError('invalid %s object at index %s' % (self.type, idx))
                else:
                    raise ValidationError

    def expand_compress(self, is_expand, obj, **kwds):
        # Make a super call and disable validation
        # This will raise proper errors if obj is not valid and will guarantee
        # that if obj == null than obj is null. 
        obj = super(Array, self).expand_compress(is_expand, obj, **kwds)
        kwds['validate'] = False

        if obj is self.null:
            return obj
        else:
            func = (self.type.expand if is_expand else self.type.compress)
            for i, item in enumerate(obj):
                obj[i] = func(item, **kwds)
            return obj

#===============================================================================
#                           Logical operations
#===============================================================================
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
    Examples
    --------
    
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
                raise ValidationError("%s object is not a valid '%s'" % (type(obj), type(v).__name__))

class OR(_SchemaL):
    '''
    Examples
    --------
    
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
        raise ValidationError("%s object is none of the json_types: '%s'" % (type(obj), v_json_types))

#===============================================================================
#                               Value
#===============================================================================
class Str(Schema):
    '''
    Examples
    --------
    
    >>> Str().is_valid('Forty two')
    True
    >>> Str().is_valid(42)
    False
    >>> Str(max_length=5).is_valid('Forty two')
    False
    '''

    INFO_ATTRIBUTES = Schema.INFO_ATTRIBUTES + [ 'max_length' ]
    NULL = u''

    def validation_function(self, obj, **kwds):
        if isinstance(obj, json_types.Str):
            if self.max_length is None:
                return True
            else:
                return self.max_length >= len(obj)
        else:
            return False

    @classmethod
    def from_string(cls, obj):
        return obj

    @dproperty
    def max_length(self):
        return None

class Text(Str):
    pass

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
        return isinstance(obj, json_types.Int)

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
        return isinstance(obj, json_types.Real)

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
        return isinstance(obj, json_types.Bool)

    @classmethod
    def from_string(cls, obj):
        try:
            return { 'true': True, 'false': False }[obj.lower()]
        except KeyError:
            raise ValueError("invalid boolean: '%s'" % obj)

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
        return isinstance(obj, json_types.Number)

class Null(Schema):
    '''
    Examples
    --------
    
    >>> Null().is_valid(None)
    True
    >>> Null().is_valid(42)
    False
    '''

    def validation_function(self, obj, **kwds):
        return obj is None

class Anything(Schema):
    '''
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

#===============================================================================
#                              Constant
#===============================================================================
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
            raise ValidationError("expected '%s', got '%s'" % (self.cte_value, obj))

#===============================================================================
#                         Str derived classes
#===============================================================================
class Regex(Str):
    def __init__(self, regex, *args, **kwds):
        if isinstance(regex, basestring):
            self.regex = re.compile(regex)
        else:
            self.regex = regex
        super(Regex, self).__init__(*args, **kwds)

    def validation_function(self, obj, **kwds):
        super(Regex, self).validation_function(obj, **kwds)
        return self.regex.match(obj) is not None

class Email(Regex):
    '''
    Example
    -------
    
    >>> Email().is_valid('foo@bar.com')
    True
    >>> Email().is_valid('foo_bar')
    False
    '''

    email_re = re.compile('^[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+$')
    def __init__(self, *args, **kwds):
        super(Email, self).__init__(self.email_re, *args, **kwds)

class Lang(Regex):
    '''
    Example
    -------
    
    >>> Lang().is_valid('pt-br')
    True
    >>> Lang().is_valid('pt')
    True
    >>> Lang().is_valid('portuguese')
    False
    '''

    lang_re = re.compile('^[a-z][a-z](-[a-z][a-z])?$')
    def __init__(self, *args, **kwds):
        super(Lang, self).__init__(self.lang_re, *args, **kwds)


#===============================================================================
#                                 Choices
#===============================================================================
class Choices(Schema):
    '''
    Examples
    --------
    
    # Tests if object belongs to some set of possibilities
    >>> sch = Choices(['foo', 'bar', 'ham', 'spam'])
    >>> sch.is_valid('eggs')
    False
    >>> sch.is_valid('ham')
    True
    
    # If numeric_choices is True, assumes that arguments are integers
    >>> sch.is_valid('ham', numeric_choices=True)
    False
    >>> sch.is_valid(1, numeric_choices=True)
    True
    >>> sch.is_valid(10, numeric_choices=True)
    False
    
    >>> sch.expand('ham', numeric_choices=True)
    2
    >>> sch.expand(2, numeric_choices=False)
    'ham'
    '''
    def __init__(self, choices, *args, **kwds):
        self.choices = list(choices)
        self.choices_set = set(self.choices)
        self.choices_map = dict(enumerate(self.choices))
        self.choices_inverse_map = dict((v, i) for (i, v) in enumerate(self.choices))
        self.num_choices = len(self.choices)

        super(Choices, self).__init__(*args, **kwds)

    def validation_function(self, obj, **kwds):
        if kwds.get('numeric_choices', False):
            try:
                return 0 <= obj < self.num_choices
            except:
                return False
        else:
            return obj in self.choices_set

    def expand(self, obj, **kwds):
        if 'numeric_choices' not in  kwds:
            super(Choices, self).expand(obj, **kwds)
        else:
            if kwds['numeric_choices']:
                try:
                    return self.choices_inverse_map[obj]
                except KeyError, ex:
                    try:
                        if 0 <= obj < self.num_choices:
                            return obj
                        else:
                            raise ValidationIndexError('invalid index, %s' % obj)
                    except:
                        raise ValidationError('invalid choice, %s' % obj)
            else:
                try:
                    return self.choices_map[obj]
                except KeyError, ex:
                    if obj in self.choices_inverse_map:
                        return obj
                    else:
                        if isinstance(obj, int):
                            raise ValidationIndexError('invalid index, %s' % obj)
                        else:
                            raise ValidationError('invalid choice, %s' % obj)

#===============================================================================
#                         References between objects
#===============================================================================
class Ref(Schema):
    '''
    Examples
    --------
    
    # Object must be a valid list of integers
    >>> fib_list = Array(Int)
    
    # Retrieves the the list with the first N fibonacci numbers.
    # In the context of this exercise, it is getting a valid fib_list object 
    # from an integer reference N.
    >>> def get_obj(N):
    ...     def fib_numbers():
    ...         a, b = -1, 1
    ...         for i in range(N):
    ...             a, b = b, a + b
    ...             yield b
    ...     return list(fib_numbers())
    
    >>> def get_ref(lst):
    ...     if lst == get_obj(len(lst)):
    ...         return len(lst)
    ...     else:
    ...         raise ValidationError
    
    >>> sch = Ref(fib_list, Int(), get_obj=get_obj, get_ref=get_ref)
    
    # By default, it checks the object's value
    >>> sch.is_valid([0, 1, 1, 2])
    True
    >>> sch.is_valid(4)
    False
    
    # If use_ref is True, it assumes that object is a reference
    >>> sch.is_valid(4, use_ref=True)
    True
    >>> sch.is_valid([0, 1, 1, 2], use_ref=True)
    False
    
    # Reference validators can be expanded into references
    >>> sch.expand(10, use_ref=False)
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    
    >>> sch.expand([0, 1, 1, 2, 3, 5, 8, 13, 21, 34], use_ref=True)
    10
    '''

    INFO_ATTRIBUTES = Schema.INFO_ATTRIBUTES + [ 'type', 'ref_type' ]

    def __init__(self, obj_type, ref_type=Nothing(), *args, **kwds):
        if isinstance(obj_type, basestring):
            ref_type = Anything()
        self.type = obj_type
        self.ref_type = ref_type
        self.obj_getter = kwds.get('get_obj', None)
        self.ref_getter = kwds.get('get_ref', None)

        super(Ref, self).__init__(*args, **kwds)

    def validation_function(self, obj, **kwds):
        if kwds.pop('use_ref', False):
            return self.ref_type.is_valid(obj)
        else:
            try:
                return self.type.is_valid(obj, **kwds)
            except AttributeError:
                return True

    def expand(self, obj, **kwds):
        if 'use_ref' in kwds:
            if kwds['use_ref']:
                if self.ref_type.is_valid(obj):
                    return obj
                else:
                    return self.get_ref(obj)
            else:
                if self.type.is_valid(obj):
                    return obj
                else:
                    return self.get_obj(obj)
        else:
            return super(Ref, self).expand(obj, **kwds)

    def get_obj(self, obj):
        if self.obj_getter is not None:
            try:
                return self.obj_getter(obj)
            except Exception as ex:
                raise ValidationError('invalid reference: %s', ex)
        else:
            raise ValueError("must define an 'obj_getter' function")

    def get_ref(self, obj):
        if self.obj_getter is not None:
            try:
                return self.ref_getter(obj)
            except Exception as ex:
                raise ValidationError('invalid object: %s', ex)
        else:
            raise ValueError("must define a 'ref_getter' function")


#===============================================================================
#                             Export all schemas
#===============================================================================
__all__ = ['ValidationError']
for k, v in globals().items():
    if isinstance(v, type) and issubclass(v, Schema) and not k.startswith('_'):
        __all__.append(k)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
