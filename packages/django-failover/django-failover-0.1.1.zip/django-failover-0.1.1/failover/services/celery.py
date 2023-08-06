"""
django-celery service
"""

########################################################################

from base import Service
from django.conf import settings

########################################################################

class Celery(Service):
    
    name = "celery"
    
    SOCKET_HOST = settings.BROKER_HOST
    SOCKET_PORT = settings.BROKER_PORT
    FAILOVER_SETTINGS = {
        'CELERY_ALWAYS_EAGER': True,
    }
    
########################################################################