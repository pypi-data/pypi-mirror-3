"""
django-failover services
"""

########################################################################

from django.conf import settings
import socket
import datetime

########################################################################

class ServiceOutage(Exception):
    pass

########################################################################

class Service(object):
    """Base service class. All service classes must inherit from this class.
    """
    name = None

    # ping frequency during normal monitoring
    MONITORING_PING_FREQUENCY = getattr(settings, "FAILOVER_MONITORING_PING_FREQUENCY", 120)
    # ping frequency during outages
    OUTAGE_PING_FREQUENCY = getattr(settings, "FAILOVER_OUTAGE_PING_FREQUENCY", 30)
    # ping frequency when an error occurs that might indicate an outage
    ERROR_PING_FREQUENCY = getattr(settings, "FAILOVER_ERROR_PING_FREQUENCY", 5)
    
    last_ping = None
    
    outage = False
    outage_last_notified = None
    
    SOCKET_PROTOCOL = socket.AF_INET
    SOCKET_HOST = None
    SOCKET_PORT = None
    SOCKET_TIMEOUT = 3
    
    FAILOVER_SETTINGS  = {}
    RECOVERY_SETTINGS = {} # Recovery settings are auto-generated during failover.
    
    ####################################################################
    
    def ping(self):
        """Pings the service by making a socket connection.
        """
        s = socket.socket(self.SOCKET_PROTOCOL, socket.SOCK_STREAM)
        if hasattr(s, 'settimeout'): s.settimeout(self.SOCKET_TIMEOUT)
        host = self.SOCKET_HOST
        port = self.SOCKET_PORT
        try:
            s.connect((host, port))
        except Exception, e:
            raise ServiceOutage(
                "Socket connection error for {0}:{1}. Error was: {2}: {3}".format(
                    host, port, e.__class__.__name__, e)
            )
        else:
            s.close()
    
    ####################################################################
    
    def failover(self):
        """Performs failover for the service by switching to the
        FAILOVER_SETTINGS.
        """
        for setting, value in self.FAILOVER_SETTINGS.iteritems():
            if hasattr(settings, setting):
                self.RECOVERY_SETTINGS[setting] = getattr(settings, setting)
            setattr(settings, setting, value)
        
    ####################################################################
    
    def recover(self):
        """Performs service recovery by switching back to the original
        settings.
        """
        for setting, value in self.FAILOVER_SETTINGS.iteritems():
            if setting in self.RECOVERY_SETTINGS:
                setattr(settings, setting, self.RECOVERY_SETTINGS[setting])
            else:
                delattr(settings, setting)
        
    ####################################################################
    
    def global_cleanup(self):
        """Performs any global cleanup needed after recovery. A service may
        not need to do any global cleanup, depending on the failover
        strategy.
        """
        pass
    
########################################################################