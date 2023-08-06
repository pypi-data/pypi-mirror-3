def get_schemas(dic):
    'Return a list of all subtypes of the Schema type to feed to __all__'
    from pyson.schemas.schema_class import Schema

    ret_lst = []
    for k, v in dic.items():
        if isinstance(v, type) and issubclass(v, Schema) and not k.startswith('_'):
            ret_lst.append(k)

    return ret_lst
