"""
django-failover middleware
"""

########################################################################

from monitor import ServiceMonitor


########################################################################

class FailoverMiddleware(object):
    """Middleware class that monitors services and fails over if necessary.
    Recovers from failovers once the service comes back up.
    """
    
    def process_request(self, request):
        ServiceMonitor.monitor()
        
########################################################################