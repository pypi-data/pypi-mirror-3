from string import Formatter


class SelfFormatter(Formatter):
    def __init__(self, obj): 
        self._obj = obj
        Formatter.__init__(self)

    def get_value(self, key, args, kwargs):
        if key == '__id__':
            return id(self._obj)
        if isinstance(key, str) and hasattr(self._obj, key):
            return getattr(self._obj, key)
        return Formatter.get_value(self, key, args, kwargs)

class FormatRepr(object):
    def __init__(self, format):
        self.format = format

    def render(self, instance):
        return SelfFormatter(instance).format(self.format)

    def __get__(self, instance, type=None):
        if instance is not None:
            return lambda: self.render(instance)
        return self

FormatRepr.__repr__ = FormatRepr('{__class__.__name__}({format!r})')
