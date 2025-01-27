class _ClassPropertyDescriptor:
    """ Implementation detail for classproperty. """

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, cls=None):
        c = cls if cls is not None else type(obj)
        #if cls is None:
        #    cls = type(obj)

        return self.fget.__get__(obj, c)()

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("no setter for property was defined")

        obj_type = type(obj)
        setter = self.fset.__get__(obj, obj_type)
        return setter(value)
        #return self.fset.__get__(obj, obj_type)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)

        self.fset = func
        return self

def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return _ClassPropertyDescriptor(func)
