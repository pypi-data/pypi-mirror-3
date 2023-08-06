``django-failover`` provides automatic failover for services used by your
Django application. For example, if you are running a master and slave
database, you might configure the slave to failover to the master.
``django-failover`` will monitor the slave and, if it goes down, will modify
your settings to point the slave connection at the master. When the slave
comes back online, ``django-failover`` will restore the settings and re-point
the slave connection at the slave.

You can configure ``django-failover`` to perform monitoring, failover, and
recovery via a middleware class. You can also specify exception classes (such
as socket errors) that, when raised and logged using Python's logging module,
will trigger monitoring. ``django-failover`` provides a log handler that you
can hook up to your logger(s) for this purpose.

``django-failover`` logs when a service goes down and when it comes back up.
It also periodically re-logs a service outage if the service remains down.

Technical Note
==============
Monitoring, failover, and recovery occur on a per-process basis. That is,
``django-failover`` does not store information about which services are down,
which are up, and when they were last monitored in any global location such
as a database or cache. Rather, each process running your Django application
discovers outages for itself. Ping frequency settings (described below) only
apply to a given process; your service may be pinged more often than your
settings stipulate if multiple processes are running your Django application.
This design is intended to keep ``django-failover`` lightweight and to
prevent minor network hiccups from triggering failover globally across
large-scale applications.

``django-failover`` is best suited for environments where your webserver is
serving multiple requests per process. A service outage will trigger failover
within the process, the process will continue serving requests while in
failover, and then will resume serving requests normally once the service
comes back up. If you are working in a development environment where your
webserver is reloading your code for each request (using a setting such as
``MaxRequestsPerChild`` in Apache), you should configure your webserver not
to reload code while experimenting with ``django-failover``. Otherwise,
``django-failover`` will start each request assuming all services are
operational.

Requirements 
============ 
``django-failover`` has been tested with Django 1.3 and Python 2.6.

Installation
============
You can install ``django-failover`` with ::

    pip install django-failover

or ::

    easy_install django-failover

This will add ``failover`` to your Python path. Add ``'failover'`` to your
``INSTALLED_APPS`` if you want to run ``django-failover``'s test suite.

Service classes
===============
To use ``django-failover``, you define and register service classes, each
class corresponding to a service used by your Django application, such as a
database, a cache, a message broker, etc. Each service class should inherit
from ``failover.services.Service`` and override it as necessary. The base
``Service`` class provides the following attributes, methods, and default
behavior:

``Service.ping()``
    This method pings the service to see if it is available. Must raise an
    exception if the service is down, otherwise the service is assumed to be
    up. Default behavior: attempts to make a socket connection using
    ``Service.SOCKET_HOST`` (default None) and ``Service.SOCKET_PORT``
    (default None). Depending on your service class, you should either define
    values for ``SOCKET_HOST`` and ``SOCKET_PORT``, or override the ``ping``
    method entirely to check the service in some other way.

``Service.failover()`` 
    This method performs failover if the service is down. Default behavior:
    modifies ``django.conf.settings``, setting name=value for each name/value
    pair in ``Service.FAILOVER_SETTINGS`` (which is an empty dictionary by
    default).

``Service.recover()`` 
    This method performs recovery when a service comes back up. Default
    behavior: restores the settings that were overwritten during failover.

``Service.MONITORING_PING_FREQUENCY`` 
    Determines the maximum frequency (in seconds) with which
    ``django-failover`` will ping the service during normal monitoring.
    This means that, when monitoring is triggered, ``django-failover`` will not
    ping the service unless at least ``MONITORING_PING_FREQUENCY`` seconds
    have passed since the last ping. Default:
    ``settings.FAILOVER_MONITORING_PING_FREQUENCY`` (or ``120`` if
    undefined).

``Service.OUTAGE_PING_FREQUENCY`` 
    Like ``MONITORING_PING_FREQUENCY``, but applies when the service is down
    and is being monitored for recovery. Default:
    ``settings.FAILOVER_OUTAGE_PING_FREQUENCY`` (or ``30`` if undefined).
    
``Service.ERROR_PING_FREQUENCY`` 
    Like ``MONITORING_PING_FREQUENCY``, but applies when monitoring is
    triggered by an exception. Default:
    ``settings.FAILOVER_ERROR_PING_FREQUENCY`` (or ``5`` if undefined).


``django-failover`` provides a few ready-to-use service classes.

``failover.services.cache.Memcached``
    This service class will ping your Memcached node(s) and let you know if
    any are down. Requires ``python-memcached`` client. Doesn't perform any
    failover, as the cache fails silently and thus automatically fails over
    to the database. This service class is useful for notifying you of
    Memcached outages.

``failover.services.celery.Celery``
    Can be used with ``django-celery``. Pings your message broker (using
    ``settings.BROKER_HOST`` and ``settings.BROKER_PORT``). If the message
    broker is down, sets ``CELERY_ALWAYS_EAGER`` to ``True``, meaning your
    celery tasks will execute locally during the outage.
    
``failover.services.db.Database``
    Fails over from one of your database connections in
    ``settings.DATABASES`` to another. By default, fails over from a
    connection with alias ``"slave"`` to a connection with alias
    ``"default"``. To failover using different db aliases, subclass
    ``Database`` and define ``DB_ALIAS`` and ``FAILOVER_DB_ALIAS`` on the
    subclass.
    
``failover.services.db.MySQL``
    A subclass of ``Database`` that sets sensible timeouts when pinging in
    order to reduce false positives and avoid hanging. Database connection
    timeout settings are backend-specific; if you use a backend other than
    MySQL and want to set timeouts, subclass ``Database`` and override the
    ``set_timeout`` method.

Registering service classes
===========================
You can register a service class in several ways. The easiest way is to
define ``FAILOVER_SERVICES`` in your settings file. ``FAILOVER_SERVICES``
should be a tuple of service classes in dot notation::

    FAILOVER_SERVICES = (
        "failover.services.cache.Memcached",
        "failover.services.celery.Celery",
        "myproject.myapp.MyServiceClass",
    )

Alternatively, import ``failover.monitor.ServiceMonitor`` and call::

    ServiceMonitor.register(MyServiceClass)

for each service class you want to register. You can also use this as a
decorator::

    @ServiceMonitor.register
    class MyServiceClass(Service):

Middleware configuration
========================
Add ``failover.middleware.FailoverMiddleware`` to your
``MIDDLEWARE_CLASSES``, at or near the beginning::

    MIDDLEWARE_CLASSES = (
        "failover.middleware.FailoverMiddleware",
        "django.middleware.common.CommonMiddleware",
        ...
    )

This will trigger monitoring, failover, and recovery before each request
(taking into account your ping frequency settings).

Logging configuration
=====================
To trigger monitoring when certain exception classes are raised, add
``failover.log.FailoverHandler`` to one of your loggers. To capture
``django-failover``'s own logging, add a handler to the ``"failover"``
logger. Service outages are logged as ``CRITICAL`` and recoveries are logged
as ``INFO``, so you probably want to set your logger and handler levels to
``INFO`` so you will know when services recover. ::

    LOGGING = {
        'version': 1,
        'handlers': {
            'mail_admins': {
                'level': 'INFO',
                'class': 'django.utils.log.AdminEmailHandler',
            },
            'failover': {
                'level': 'ERROR',
                'class': 'failover.log.FailoverHandler',
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins', 'failover'],
                'level': 'ERROR',
            },
            'failover': {
                'handlers': ['mail_admins'],
                'level': 'INFO',
            },
        },
    }

By default, ``FailoverHandler`` will trigger monitoring for the following
exception classes::
    
    socket.error
    django.db.DatabaseError
    urllib2.URLError
    
To add to this list, define ``FAILOVER_OUTAGE_EXTRA_EXCEPTION_CLASSES`` in
settings. To override the list, define ``FAILOVER_OUTAGE_EXCEPTION_CLASSES``.    

Monitoring decorators
=====================
You can also trigger monitoring using several decorators ``django-failover``
provides. Decorating a function with ``failover.decorators.monitor`` will
trigger monitoring prior to the function being called. Wrapping the function
with ``failover.decorators.recover_from_outages`` will monitor services that
are currently down, but won't monitor services that are operating normally.
``recover_from_outages`` is useful in conjunction with exception-based
monitoring, as the latter provides no trigger for checking when a service
recovers. If you are only using ``django-failover``'s middleware, you
probably don't need either of these decorators.

Additional Settings
===================
``FAILOVER_OUTAGE_LOGGING_FREQUENCY``        
    Controls how often, after a service outage is discovered, the outage will
    be re-logged if the service remains down. Default: ``3600`` seconds (1
    hour).

``FAILOVER_MONITORING_PING_FREQUENCY``
    Controls the ping frequency during normal monitoring on service classes
    that don't define their own value. Default: ``120`` seconds.

``FAILOVER_OUTAGE_PING_FREQUENCY``
    Controls the ping frequency during outages on service classes
    that don't define their own value. Default: ``30`` seconds.

``FAILOVER_ERROR_PING_FREQUENCY``
    Controls the ping frequency for exception-triggered monitoring on
    service classes that don't define their own value. Default: ``5``
    seconds.
    