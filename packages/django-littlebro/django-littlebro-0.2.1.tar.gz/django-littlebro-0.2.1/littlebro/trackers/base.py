from littlebro.conf import settings

class InvalidTrackerError(Exception):
    pass

class BaseTracker(object):
    """
    Abstract base tracker class. Maybe someday there will be useful methods for
    other trackers to inherit from here, but not yet.
    """
    def __init__(self, *args, **kwargs):
        self.backend = settings.DB_BACKEND
    
    def track_event(self, event, params={}, collection=None):
        raise NotImplementedError