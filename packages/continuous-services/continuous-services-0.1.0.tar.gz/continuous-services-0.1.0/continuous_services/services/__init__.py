
def _setup_all():
    import os
    import os.path
        
    here = os.path.dirname(__file__)
    services = os.listdir(here)
    return filter(lambda s: os.path.isdir(os.path.join(here, s)), services)

__all__ = _setup_all()