"""
django-failover settings
"""
from django.conf import settings
from django.db import DatabaseError
import socket
import urllib2

OUTAGE_EXCEPTION_CLASSES = getattr(
    settings, "FAILOVER_OUTAGE_EXCEPTION_CLASSES", (socket.error,
                                                    DatabaseError,
                                                    urllib2.URLError
                                                    )
    ) + getattr(settings, "FAILOVER_OUTAGE_EXTRA_EXCEPTION_CLASSES", ()) 

SERVICES = getattr(settings, "FAILOVER_SERVICES", ())

OUTAGE_LOGGING_FREQUENCY = getattr(settings, "FAILOVER_OUTAGE_LOGGING_FREQUENCY", 3600) # 1 hour