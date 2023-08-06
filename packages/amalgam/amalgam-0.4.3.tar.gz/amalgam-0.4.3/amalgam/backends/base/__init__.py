from amalgam.backends.base.backend import BaseBackend

def get_backend(*args, **kwargs):
    return BaseBackend(*args, **kwargs)
