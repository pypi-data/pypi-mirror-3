'''
>>> from pyson.schemas import * # make doctests work
'''
from pyson import types as pyson_t
from pyson.schemas.schema_class import Schema, Anything
from pyson.schemas.util import get_schemas
import collections

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
            raise self.ValidationError("%s object at key '%s' is not a valid '%s'"
                                  % (type(value), self.basepath(key), type(validator).__name__))
        else:
            raise self.ValidationError

class Object(Container, collections.Mapping):
    NULL = {}
    INFO_ATTRIBUTES = Container.INFO_ATTRIBUTES + [ 'fields', 'validation_keys' ]

    def __init__(self, *args, **kwds):
        '''
        Represents a JSON Object. JSON objects are essentially a dictionary
        in which keys must be strings.
        
        Example
        -------
        
        >>> from pyson.schemas import *
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
        self.fields = [ k for (_i, k) in self.fields ]

    def validate(self, obj, **kwds):
        full_errors = kwds.get('full_errors', self.DISPLAY_FULL_ERRORS)
        implicit_defaults = kwds.get('implicit_defaults', True)
        if not implicit_defaults:
            print 'not implicit'

        # Check if obj is a dict
        if not pyson_t.is_object(obj):
            raise self.ValidationError("object of type '%s' is not a mapping." % type(obj).__name__)

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
            except self.ValidationError, ex:
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
        
        >>> from pyson.schemas import *
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
            raise self.ValidationError("missing key, '%s'" % (self.basepath(key)))
        else:
            raise self.ValidationError

    def _raise_extra_keys(self, keys, full_errors):
        if full_errors:
            if len(keys) > 1:
                base = self.basepath()
                keys = ', '.join(keys)
                raise self.ValidationError("invalid keys, '%s.(%s)'" % (base, keys))
            else:
                key = self.basepath(tuple(keys)[0])
                raise self.ValidationError("invalid key, '%s'" % key)
        else:
            raise self.ValidationError

    def add_item(self, key, value):
        '''
        Register validator 'value' in given 'key'.
        
        Example
        -------
        
        >>> from pyson.schemas import *
        >>> schema = Object({ 'foo': Str('bar') })
        >>> schema['foo'].parent is schema
        True
        >>> schema['foo'].name
        u'foo'
        >>> schema['foo'].label
        u'Foo'
        '''

        if pyson_t.is_string(key):
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
        
        >>> from pyson.schemas import *
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
        if not pyson_t.is_array(obj):
            if full_errors:
                raise self.ValidationError(" %s object is not an Array" % type(obj))
            else:
                raise self.ValidationError

        v = self.type.validate
        for idx, x in enumerate(obj):
            try:
                v(x, **kwds)
            except self.ValidationError:
                if full_errors:
                    self.ValidationError('invalid %s object at index %s' % (self.type, idx))
                else:
                    raise self.ValidationError

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

# Save specialized schemas into the Schema class
Schema.OBJECT_SCHEMA = Object
Schema.ARRAY_SCHEMA = Array

__all__ = get_schemas(globals())
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
