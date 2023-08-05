from django.utils import importlib
from carrot.connection import DjangoBrokerConnection
from littlebro.conf import settings
from littlebro.backends.base import InvalidBackendError

BACKEND_CLASSES = {
    'simple': 'simple.SimpleBackend',
    'mongo': 'mongo.MongoBackend'
}

def _get_backend_cls():
    """
    Helper function to dynamically get the appropriate database backend according
    to settings.
    """
    try:
        backend = 'littlebro.backends.%s' % BACKEND_CLASSES[settings.DB_BACKEND]
        mod_path, cls_name = backend.rsplit('.', 1)
        mod = importlib.import_module(mod_path)
        backend_cls = getattr(mod, cls_name)
    except (AttributeError, ImportError, ValueError, KeyError), e:
        raise InvalidBackendError(
            'Could not find a backend named %s' %  e)
    return backend_cls()

def _get_carrot_object(klass, **kwargs):
    """
    Helper function to create Publisher and Consumer objects.
    """
    return klass(
            connection=DjangoBrokerConnection(),
            exchange=settings.EXCHANGE,
            routing_key=settings.ROUTING_KEY,
            exchange_type="topic",                                                                                     
            **kwargs
        )
    
def _close_carrot_object(carobj):
    """
    Helper function to close Consumer or Publisher safely.
    """
    if carobj:
        try:
            carobj.close()
        except:
            pass
        try:
            carobj.connection.close()
        except:
            pass