def import_attribute(name):
    """Import attribute using string reference.

    Example::

      import_attribute('a.b.c.foo')

    Throws ImportError or AttributeError if module or attribute do not exist.
    """
    path, attr = name.rsplit('.', 1)
    module = __import__(path, globals(), locals(), [attr])

    return getattr(module, attr)


class classproperty(object):
    def __init__(self, method):
        self.method = method

    def __get__(self, obj, cls):
        return self.method(cls)
