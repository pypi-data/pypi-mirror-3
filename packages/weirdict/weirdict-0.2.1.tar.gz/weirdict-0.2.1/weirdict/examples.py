from .base import AbstractNormalizedDict
from .decorators import lenient


class CaseInsensitiveDict(AbstractNormalizedDict):
    """A dict whose string keys are case-insensitive."""
    @staticmethod
    @lenient
    def keyfunc(key):
        return str.lower(key)


class TruncatedKeyDict(AbstractNormalizedDict):
    """A dict whose keys are truncated to a given length."""
    def __init__(self, key_length, *args, **kwargs):
        self._key_length = key_length
        super(TruncatedKeyDict, self).__init__(*args, **kwargs)

    def copy(self):
        return type(self)(self.key_length, self.iteritems())

    @property
    def key_length(self):
        return self._key_length

    @lenient
    def keyfunc(self, key):
        return key[:self.key_length]


class ModuloKeyDict(AbstractNormalizedDict):
    """A dict whose keys are normalized modulo a given parameter.
    Note: a side-effect of the implementation is that strings containing a
    formatting parameter will be formatted using the modulo.
    
    """
    def __init__(self, modulo, *args, **kwargs):
        self._modulo = modulo
        super(ModuloKeyDict, self).__init__(*args, **kwargs)

    def copy(self):
        return type(self)(self.modulo, self.iteritems())

    @property
    def modulo(self):
        return self._modulo

    @lenient
    def keyfunc(self, key):
        return key % self.modulo
