# Tracking system backend. Options are 'dummy' and 'celery'
TRACKER_BACKEND = 'dummy'

# Database backend. Options are 'simple' and 'mongo'
DB_BACKEND = 'simple'

# Settings for message routing in Celery
# More information here: http://ask.github.com/celery/userguide/routing.html
ROUTING_KEY = 'littlebro'
EXCHANGE = 'littlebro'
QUEUE = 'littlebro'

# Length of time between asynchronous updates to database, in seconds.
# Also known as the length of time between celerybeat cycles.
TASK_PERIOD = 3*60

# Settings for MongoDB
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DEFAULT_MONGO_DB = 'littlebro'
DEFAULT_MONGO_COLLECTION = 'littlebro'
