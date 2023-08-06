"""
django-failover middleware
"""

########################################################################

from monitor import ServiceMonitor


########################################################################

class FailoverMiddleware(object):
    """Middleware class that monitors services and fails over if necessary.
    Recovers from failovers once the service comes back up. During outages,
    calls the outage middleware (if any) associated with the service that is
    down.
    """
    
    def process_request(self, request):
        ServiceMonitor.monitor()
        for service_class in ServiceMonitor.outages:
            if hasattr(service_class.outage_middleware_class, "process_request"):
                middleware = service_class.outage_middleware_class()
                response = middleware.process_request(request)
                if response:
                    return response
                
    def process_view(self, request, view_func, view_args, view_kwargs):
        for service_class in ServiceMonitor.outages:
            if hasattr(service_class.outage_middleware_class, "process_view"):
                middleware = service_class.outage_middleware_class()
                response = middleware.process_view(request, view_func, view_args, view_kwargs)
                if response:
                    return response
                
########################################################################