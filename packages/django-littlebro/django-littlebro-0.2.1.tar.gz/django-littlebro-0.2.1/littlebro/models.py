from django.db import models

class Event(models.Model):
    """
    Simple model for storing events. Best to use Mongo in production if you can,
    but this will work in a pinch (or on low-traffic apps).
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.SlugField()
    params = models.TextField()