"""
cache services
"""

########################################################################

from django.core.cache import cache
from base import Service, ServiceOutage

########################################################################

class MemcachedServiceOutage(ServiceOutage):
    pass

########################################################################

class Memcached(Service):
    """Memcached service monitoring class that works with python-memcached.
    
    Memcached fails silently (and thus automatically fails over to the
    database, etc.). This service class performs no additional failover or
    recovery.
    """
    name = "memcached"
    
    def ping(self):
        servers = cache._servers
        stats = cache._cache.get_stats()
        dead_servers = []
        for server in servers:
            if not any(stat[0].startswith(server) for stat in stats):
                dead_servers.append(server)
        if dead_servers:
            raise MemcachedServiceOutage(dead_servers)
        
########################################################################