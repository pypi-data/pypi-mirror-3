import sys, traceback

from amalgam.utils import import_attribute


__version__ = '0.4.3'
__all__ = ['amalgam']


def import_backend(name):
    try:
        return import_attribute('.'.join(['amalgam', 'backends', name]))
    except ImportError:
        if len(traceback.extract_tb(sys.exc_info()[2])) > 1:
            raise
        return import_attribute(name)


def amalgam(backend, *args, **kwargs):
    '''Return initialized backend

    :param backend:

      Should be a module of backend or a string containing Python path to
      module, possibly relative to amalgam, f.e. 'sqla' for 'amalgam.sqla'

    All other parameters are determined by backend itself.
    '''
    if isinstance(backend, str):
        backend = import_backend(backend)
    return backend.get_backend(*args, **kwargs)
