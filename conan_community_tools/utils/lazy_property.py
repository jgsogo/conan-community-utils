

def lazy_property(fn):
    """Decorator that makes a property lazy-evaluated."""

    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if attr_name not in self.__dict__:
            self.__dict__[attr_name] = fn(self)
        return self.__dict__[attr_name]

    return _lazy_property
