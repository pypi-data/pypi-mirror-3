"""
db services
"""

########################################################################

from base import Service
from django.conf import settings
from django.db import connections

########################################################################

class Database(Service):
    
    name = "database"
    DB_ALIAS = "slave"
    FAILOVER_DB_ALIAS = "default"
    connection = None
    
    def __init__(self):
        # cache a connection object early so we'll have the original settings
        # for pinging, rather than possibly the failover settings
        if not self.connection:
            self.__class__.connection = connections[self.DB_ALIAS]
    
    def set_timeout(self):
        """Hook for setting timeouts on the connection before pinging.
        (Timeout options vary per backend.)
        """
        return
    
    def ping(self):
        self.set_timeout()
        self.connection.cursor()
        self.connection.close()
        
    @classmethod
    def reload_settings(cls):
        """Reload settings into connection handler
        (django.db.utils.ConnectionHandler)
        """
        if cls.DB_ALIAS in connections._connections:
            del connections._connections[cls.DB_ALIAS]
        connections.databases = settings.DATABASES
        
    def failover(self):
        connections[self.DB_ALIAS].close()
        self.RECOVERY_SETTINGS[self.DB_ALIAS] = settings.DATABASES[self.DB_ALIAS]
        settings.DATABASES[self.DB_ALIAS] = settings.DATABASES[self.FAILOVER_DB_ALIAS]
        self.reload_settings()
        
    def recover(self):
        connections[self.DB_ALIAS].close()
        settings.DATABASES[self.DB_ALIAS] = self.RECOVERY_SETTINGS[self.DB_ALIAS]         
        self.reload_settings()
        
########################################################################

class MySQL(Database):
    
    def set_timeout(self):
        # set a longer timeout if we're monitoring and a shorter timeout if
        # we're down. This reduces false positives during monitoring, and
        # prevents pinging from hanging too long during outages.
        if self.outage:
            self.connection.settings_dict['OPTIONS']['connect_timeout'] = 1
        else:
            self.connection.settings_dict['OPTIONS']['connect_timeout'] = 10