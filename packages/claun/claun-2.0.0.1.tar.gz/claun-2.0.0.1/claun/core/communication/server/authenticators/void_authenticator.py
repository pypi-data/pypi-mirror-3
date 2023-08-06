"""
Void client authenticator that does nothing, but shows developers how the authentication process
should be handled.

*** DO NOT USE IN PRODUCTION ***
"""

from claun.core import container

__docformat__ = 'restructuredtext en'

def init(config, endpoints):
    """
    Initialize authenticator with configuration values and properties of all modules.
    :param config: hash with parsed client_authentication section of yaml configuration
    :param modules: hash containing True or False for endpoints, if True, perform auth, if False, skip (see ``server`` module)
    """
    pass

def loadhook():
    """
    This is the _authenticate method disguised as a loadhook.

    It is used when the configuration option 'global' is true. During the server
    startup, this method is registered as an application loadhook and is
    executed before **every** request.
    """
    _authenticate()


def authenticate():
    """
    The authenticate method is used when the global authentication is turned off.

    It can be called as a first method in the flow of the request method.
    You can access the method via the global container where it is assigned during the
    server startup.

    >>> import claun.core.container as c
    >>> ...
    >>> class Root:
    >>>     def GET(self):
    >>>             c.client_authentication()
    >>>             return "Hello world"

    Such method is then protected against unauthorized access from the outside world.
    """
    _authenticate()

def decorator():
    """
    This is the _authenticate method disguised as a decorator.

    Until the proper order of resolution, it is recommended to not use
    the decorator, but simply call an authenticate method instead.
    """
    def deco(func):
        def proxyfunc(self, * args, ** kw):
            _authenticate()
            return func(self, * args, ** kw)
        return proxyfunc
    return deco

def _authenticate():
    """
    Real authentication happens here. Check some file, database, starmap or tea leaves.

    Firstly, you should check if the requested module is protected or not. Use the modules parameter
    of the init method. It could look like this:
    >>> global modules
    >>> module_name = claun.core.container.web.ctx.env.get('PATH_INFO').split('/')[1]
    >>> if module_name in endpoints and not endpoints[module_name]: return
    """
    if True:
        return True
    else:
        raise container.web.unauthorized("Unauthorized access!")
