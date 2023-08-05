from littlebro.conf import settings

class InvalidBackendError(Exception):
    pass

class BaseBackend(object):
    """
    Abstract base backend class. Maybe someday there will be some useful methods
    that other backends need to inherit from here, but not yet.
    """
    def __init__(self, *args, **kwargs):
        self.host = None
        self.port = None
        self.collection = None
        self.db = None
    
    def save(self, event, params={}, collection=None):
        raise NotImplementedError