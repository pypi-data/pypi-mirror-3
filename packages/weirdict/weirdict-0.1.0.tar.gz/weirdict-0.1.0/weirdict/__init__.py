from collections import Mapping
from functools import wraps

def normalize_key(method):
    """A decorator for dict methods that take a key argument.
    This decorator normalizes the key through the instance's keyfunc function.
    
    """
    @wraps(method)
    def wrapped(self, key, *args):
        key = self.keyfunc(key)
        return method(self, key, *args)
    return wrapped


def lenient(keyfunc=None, catch=TypeError):
    """Decorate a keyfunc function by trying to exectute it and if a
    TypeError (or whatever is passed as the catch argument) is raised,
    catch it and return the key unmodified.
    
    """
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args):
            try:
                return fn(*args)
            except catch:
                # In order for this decorator to work both on methods or plain
                # functions, we assume that the key is the last positional
                # argument passed.
                return args[-1]
        return wrapped
    
    if keyfunc is None:
        return decorator
    return decorator(keyfunc)


class BaseNormalizedDict(dict):
    """A dictionary where keys are normalized through a given function
    before being inserted in the dict.
    
    """
    keyfunc = staticmethod(lambda s: s) # do nothing
    
    def __init__(self, map_or_seq=None, **kwargs):
        """Normalize the keys before delegating to the parent's constructor.
        The signature is (hopefully) the same as the one for dict.
        
        """
        if map_or_seq is None:
            args = []
        elif isinstance(map_or_seq, Mapping):
            args = [((self.keyfunc(k), v) for k, v in map_or_seq.items())]
        else: # sequence of two-tuples
            args = [((self.keyfunc(k), v) for k, v in map_or_seq)]
        
        kwargs = {self.keyfunc(k): v for k, v in kwargs.iteritems()}
        
        super(BaseNormalizedDict, self).__init__(*args, **kwargs)
    
    def copy(self):
        return type(self)(self.iteritems())

    @normalize_key
    def __getitem__(self, key):
        return super(BaseNormalizedDict, self).__getitem__(key)

    @normalize_key
    def __setitem__(self, key, value):
        return super(BaseNormalizedDict, self).__setitem__(key, value)

    @normalize_key
    def __delitem__(self, key):
        return super(BaseNormalizedDict, self).__delitem__(key)

    @normalize_key
    def __contains__(self, key):
        return super(BaseNormalizedDict, self).__contains__(key)
    
    @normalize_key
    def get(self, key, default=None):
        return super(BaseNormalizedDict, self).get(key, default)
    
    @normalize_key
    def pop(self, key, *args):
        return super(BaseNormalizedDict, self).get(key, *args)


class NormalizedDict(BaseNormalizedDict): # XXX: Broken
    """A normalized dict where the keyfunc can be passed in the constructor.
    The keyfunc can also be changed on-the-fly.
    
    """
    def __init__(self, *args, **kwargs):
        if 'keyfunc' in kwargs:
            self._keyfunc = kwargs.pop('keyfunc')
        return super(NormalizedDict, self).__init__(*args, **kwargs)

    @property
    def keyfunc(self):
        return self._keyfunc

    @keyfunc.setter
    def keyfunc(self, keyfunc):
        """Re-normalize the keys using the new keyfunc."""
        for key in self.keys():
            value = self.pop(key)
            new_key = keyfunc(key)
            self[new_key] = value# XXX: Ugh, that's not really smart...
        self._keyfunc = keyfunc


class CaseInsensitiveDict(BaseNormalizedDict):
    """A dict whose string keys are case-insensitive."""
    @staticmethod
    @lenient
    def keyfunc(key):
        return str.lower(key)


class TruncatedKeyDict(BaseNormalizedDict):
    """A dict whose keys are truncated."""
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


class ModuloKeyDict(BaseNormalizedDict):
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


if __name__ == '__main__':
    ci = CaseInsensitiveDict(foo="bar", BAR=42)
    print ci['FOO'], ci['baR'] # "bar", 42
    print ci.copy()['FOO']
    print ci.get('FOO')
    
    tr = TruncatedKeyDict(3, foo="bar")
    print tr['fooooooo'] # "bar"
    print tr.copy()['foooooo']
    
    mo = ModuloKeyDict(10, {1: "bar"})
    print mo[51] # "bar"
    print mo.copy()[101]
