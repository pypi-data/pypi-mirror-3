def dproperty(name, defvalue):
    """
    Property attribute with a default value. If this value is overridden,
    it is saved in the "._name" attribute of the object.
    """

    name = '_' + name

    def get(self):
        try:
            return getattr(self, name)
        except AttributeError:
            setattr(self, name, defvalue)
            return getattr(self, name)
    def set_(self, value):
        if value != defvalue:
            setattr(self, name, value)

    def del_(self):
        delattr(self, name)

    return property(get, set_, del_)
