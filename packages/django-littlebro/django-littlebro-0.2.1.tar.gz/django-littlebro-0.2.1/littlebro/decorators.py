from littlebro.trackers import tracker

def track_view(event):
    """
    Decorator for view-level tracking. Usage looks like this:
    
    @track_view('event-name-here')
    def my_view(request):
       ...
    """
    def _dec(func):
        def _wrap(request, *args, **kwargs):
            params = {
                'path': request.get_full_path(),
                'user': str(request.user),
            }
            tracker.track_event(event, None, params)
            return func(request, *args, **kwargs)
        return _wrap
    return _dec