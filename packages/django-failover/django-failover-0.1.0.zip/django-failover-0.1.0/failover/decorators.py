"""
django-failover decorators
"""

########################################################################

from django.utils.functional import wraps
import logging

########################################################################

logger = logging.getLogger("failover")

########################################################################

def log_errors(function):
    """Decorator that catches and logs error in the wrapped
    function.
    """
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception, e:
            logger.error(
                "Error in {0}.{1}: {2}".format(
                    function.__module__, function.__name__,e),
                exc_info=e,
            )
            
    return wraps(function)(wrapper)

########################################################################

def monitor(function):
    """Decorator that performs monitoring before calling the wrapped
    function.
    """
    from monitor import ServiceMonitor
    def wrapper(*args, **kwargs):
        ServiceMonitor.monitor()
        return function(*args, **kwargs)
    return wraps(function)(wrapper)

########################################################################

def recover_from_outages(function):
    """Decorator that attempts to recover from outages for services that are
    down, but does not perform monitoring of services that are not down.
    Intended for cases where discovery of outages is handled in some other
    way (for example, via exception logging).
    """
    from monitor import ServiceMonitor
    def wrapper(*args, **kwargs):
        ServiceMonitor.monitor(outages_only=True)
        return function(*args, **kwargs)
    return wraps(function)(wrapper)

########################################################################