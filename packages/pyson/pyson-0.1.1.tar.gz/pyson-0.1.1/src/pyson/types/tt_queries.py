from pyson.types.abstract import *

__all__ = ['is_value', 'is_container', 'is_mapping', 'is_sequence']

def is_sequence(obj, jsonlevel=0):
    return isinstance(obj, Sequence)

def is_mapping(obj, jsonlevel=0):
    return isinstance(obj, Mapping)

def is_container(obj, jsonlevel=0):
    return isinstance(obj, Container)

def is_value(obj, jsonlevel=0):
    return not isinstance(obj, Container)
