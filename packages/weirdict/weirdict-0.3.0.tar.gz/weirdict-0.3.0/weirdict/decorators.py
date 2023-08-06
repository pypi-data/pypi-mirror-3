from functools import wraps


def apply_keyfunc(method):
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
