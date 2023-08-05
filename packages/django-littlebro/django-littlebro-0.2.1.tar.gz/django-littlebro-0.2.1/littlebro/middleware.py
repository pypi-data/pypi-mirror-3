from littlebro.trackers import tracker

class TrackerMiddleware(object):
    """
    Middleware to track all requests to pages in your app. Not much of a use for
    it at this point if you have analytics enabled, but more functionality is
    to come. For the love of God, don't use this synchronously in production.
    
    Usage:
    
    In your app's settings.py, add littlebro.middleware.TrackerMiddleware to the
    end of your MIDDLEWARE_CLASSES setting.
    """
    def process_request(self, request):
        event = 'page-accessed'
        params = {
            'path': request.get_full_path(),
            'user': str(request.user),
        }
        tracker.track_event(event, None, params)
        return None