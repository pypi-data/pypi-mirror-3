"""
django-failover logging
"""

########################################################################

import logging
import socket

########################################################################

class ServiceOutageExceptionsFilter(logging.Filter):
    """Logging filter that only allows records that contain exceptions that may
    signify a service outage, such as socket errors.
    """
    
    def filter(self, record):
        import settings
        return record.exc_info and record.exc_info[0] and issubclass(
            record.exc_info[0], settings.OUTAGE_EXCEPTION_CLASSES)
    
########################################################################

class FailoverHandler(logging.Handler):
    """Logging handler that runs the service monitor to check for outages and
    failover if necessary.
    """
    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.addFilter(ServiceOutageExceptionsFilter())
    
    def emit(self, record):
        from monitor import ServiceMonitor
        ServiceMonitor.monitor(
            exception=record.exc_info[0] if record.exc_info and record.exc_info[0] else None
        )
        
########################################################################