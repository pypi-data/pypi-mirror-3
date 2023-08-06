"""
django-failover service monitor
"""

########################################################################

from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
import os
import logging
import datetime
import settings
from services.base import Service
from decorators import log_errors

########################################################################

logger = logging.getLogger('failover')

########################################################################

class ServiceMonitor(object):
    """Monitoring class that Service classes register with.
    
    Uses class attributes and class methods so that the state of the
    ServiceMonitor is persistent within the process space.
    """
    # Min seconds to wait before re-logging an outage
    OUTAGE_LOGGING_FREQUENCY = settings.OUTAGE_LOGGING_FREQUENCY

    services = set()
    outages = set()
        
    ####################################################################
    
    @classmethod
    def register(cls, service_cls):
        """Registers the provided Service class. Can be used as a decorator.
        """
        cls.services.add(service_cls)
        return service_cls
    
    ####################################################################
    
    @classmethod
    @log_errors
    def monitor(cls, outages_only=False, exception=None):
        """Pings each registered service. If the service is unavailable, logs
        the outage and performs failover for the service. If the service was
        down and now is back up, performs recovery.
        
        If outages_only is True, only services that are currently down will
        be pinged. If an exception is provided, the monitoring will use the
        ERROR_PING_FREQUENCY for the service.
        """
        for service_class in cls.services:
            service = service_class()

            if outages_only and service_class not in cls.outages:
                continue
            
            if exception:
                ping_frequency = service_class.ERROR_PING_FREQUENCY
            elif service_class in cls.outages:
                ping_frequency = service_class.OUTAGE_PING_FREQUENCY
            else:
                ping_frequency = service_class.MONITORING_PING_FREQUENCY
              
            # If it's not time to re-ping yet, continue 
            if (service_class.last_ping
                and service_class.last_ping > datetime.datetime.now() - datetime.timedelta(
                    seconds=ping_frequency)):
                continue
            
            try:
                service_class.last_ping = datetime.datetime.now()
                service.ping()
            except Exception, e:
                # Service down
                
                # Failover if we haven't already done so
                if service_class not in cls.outages:
                    service_class.outage = True
                    cls.outages.add(service_class)
                    service.failover()
                    
                if (
                    service_class.outage_last_notified is None
                    or service_class.outage_last_notified <= datetime.datetime.now() - datetime.timedelta(
                        seconds=cls.OUTAGE_LOGGING_FREQUENCY)):
                    
                    service_class.outage_last_notified = datetime.datetime.now()
                    logger.critical(
                        "{0} outage. Failover initiated. (Process ID: {1})".format(
                            service_class.name or service_class.__name__,
                            os.getpid()),
                        exc_info=e)
            else:
                # Service up 
                
                # If it has been down, recover and log the recovery
                if service_class in cls.outages:
                    service.recover()
                    service_class.outage = False
                    service_class.outage_last_notified = None
                    cls.outages.remove(service_class)
                    logger.info(
                        "{0} is back up. Recovery complete. (Process ID: {1})".format(
                            service_class.name or service_class.__name__,
                            os.getpid()
                        ))
                                       
    ####################################################################
    
    @classmethod
    def global_cleanup(cls):
        """Calls the global_cleanup method on each registered service class. The
        service class is responsible for determining if it needs to do any
        global cleanup (from a previous outage).
        """
        for service_class in cls.services:
            service = service_class()
            service.global_cleanup()
            
########################################################################

def register():
    """Registers the service classes defined in settings.
    """
    for path in settings.SERVICES:
        try:
            module, classname = path.rsplit('.', 1)
        except ValueError:
            raise ImproperlyConfigured('%s isn\'t a failover service class' % path)
        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing failover service module %s: "%s"' % (module, e))
        try:
            service_class = getattr(mod, classname)
        except AttributeError:
            raise ImproperlyConfigured('Failover service module "%s" does not define a "%s" class' % (module, classname))
        if not issubclass(service_class, Service):
            raise ImproperlyConfigured('Failover service class "%s" does not inherit from failover.services.base.Service' % classname)
        ServiceMonitor.register(service_class)
        
register()