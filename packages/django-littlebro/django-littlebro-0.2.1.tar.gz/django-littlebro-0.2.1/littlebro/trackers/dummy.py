from time import time
from django.utils import importlib
from littlebro.trackers.base import BaseTracker
from littlebro.utils import _get_backend_cls

class DummyTracker(BaseTracker):
    """
    Saves tracking events synchronously into either a regular or Mongo DB table.
    Primarily used for testing.
    """
    def __init__(self, *args, **kwargs):
        BaseTracker.__init__(self, *args, **kwargs)
        
    def track_event(self, event, params={}, collection=None):        
        backend = _get_backend_cls()
        backend.save(event, time(), params, collection)