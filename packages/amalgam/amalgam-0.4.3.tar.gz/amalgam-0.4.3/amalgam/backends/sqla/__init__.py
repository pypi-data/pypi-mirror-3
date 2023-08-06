from amalgam.backends.sqla.backend import SABackend

def get_backend(*args, **kwargs):
    return SABackend(*args, **kwargs)
