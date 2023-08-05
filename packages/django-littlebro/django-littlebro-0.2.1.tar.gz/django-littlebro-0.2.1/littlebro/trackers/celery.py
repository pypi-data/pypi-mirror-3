from datetime import timedelta
from time import time
from carrot.messaging import Publisher
from littlebro.trackers.base import BaseTracker
from littlebro.conf import settings
from littlebro.utils import _get_carrot_object, _close_carrot_object

publisher = None

class CeleryTracker(BaseTracker):
    """
    Tracker that stored events into a Celery task queue for asynchronous
    processing later.
    """
    def __init__(self, *args, **kwargs):
        BaseTracker.__init__(self, *args, **kwargs)
   
    def track_event(self, event, params={}, collection=None):
        """
        Dispatch a track event request into the queue.
    
        If the Publisher object hasn't been intialized yet, do so. If any error
        occurs during sending of the message, close the Publisher so it will be
        open automatically the next time somedy tracks an event. This will prevent
        a short-term network failure to disable one thread from commucating with
        the queue at the cost of retrying the connection every time.
        """
        global publisher
        if publisher is None:
            # no connection or there was an error last time
            # reinitiate the Publisher
            publisher = _get_carrot_object(Publisher)
    
        try:
            # put the message into the queue including current time
            publisher.send((event, time(), params, collection))
        except:
            # something went wrong, probably a connection error or something. Close
            # the carrot connection and set it to None so that the next request
            # will try and reopen it.
            _close_carrot_object(publisher)
            publisher = None
            raise