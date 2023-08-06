"""
Primitive authenticator that reads username and passwords from yaml file.

This is the default authenticator that is used in the claun system. It is based on simple
comparison of provided Basic HTTP Authorization in custom header against a local YAML file containing allowed
clients with mandatory clients section.

Example YAML:
clients:
  client_a: password_a
  client_b: password_b

For more implementation details, please see void_authenticator.

To see how to get to more request parameters, please see web.py context documentation:
  - http://webpy.org/cookbook/ctx

"""
import base64


from claun.core import configurator
from claun.core import container
from claun.core import log

__docformat__ = 'restructuredtext en'

"""
Hash for clients created from configuration file passed to the init method.
"""
clients = {}
modules = {}

def init(config, mods):
    """
    Authenticator reads clients username:password pairs from config.credentials_file option.

    Config requires credentials_file field containing path to the credentials file in the config.
    :param mods: hash of pathbeforefirstslash: True|False
    """
    global clients, modules
    configreader = configurator.Configurator(config['credentials_file'])
    clients = configreader.parse()['clients']
    modules = mods

def loadhook():
    """
    This is the _authenticate method disguised as a loadhook.
    """
    _authenticate()


def authenticate():
    """
    The authenticate method is used when the global authentication is turned off.
    """
    _authenticate()

def decorator():
    """
    This is the _authenticate method disguised as a decorator. It is currently not used
    """
    def deco(func):
        def proxyfunc(self, * args, ** kw):
            _authenticate()
            return func(self, * args, ** kw)
        return proxyfunc
    return deco

def _authenticate():
    """
    Authorizes clients using the __do_auth method.

    The first step is to determine if the security check should be performed.
    Global modules hash and the first part of the PATH_INFO is used. PATH_INFO contains the PATH of the request with leading slash.
    String between this leading and the first following slash is used to identify the module. If module with such name
    is registered and is set to not be authorized, the check is skipped and logged. If it is set to be authenticated or not registered at all,
    the authentication process follows:

    Firstly, it checks the Authorization header of the incoming request.
    Only Basic HTTP authorization method is supported by this authenticator.
    After getting the credentials from the correct header, they are
    decoded using the standard base64 algorithm.
    If the credentials in the authorization header are valid, nothing is done.
    If the credentials are bad, web.unauthorized exception is risen and 401 HTTP is provided as a response.

    An optional (but discouraged) way how to pass the component's authentication is the `claun_authentication` GET/POST parameter.
    It may be useful when using a client where you have no control over request headers. The parameter contains only
    base64 encoded credentials and not the authentication method.
    """
    global modules
    module_name = container.web.ctx.env.get('PATH_INFO').split('/')[1]
    if module_name in modules and not modules[module_name]:
        container.log.debug('Skipping authentication for %s module...' % module_name)
        return

    auth = container.web.input(claun_authentication=None)['claun_authentication']
    if auth is None:
        header = container.web.ctx.env.get('HTTP_X_CLAUN_AUTHENTICATION')
        if header is None:
            raise container.web.unauthorized(container.output({'error': '401', 'error_description': "Missing X-Claun-Authentication header!"}))
        method, auth = header.split(' ')
        if method != 'Basic':
            raise container.web.unauthorized(container.output({'error': '401', 'error_description': "Bad authentication method. Supported methods: Basic"}))
    try:
        uname, pwd = base64.b64decode(auth).split(':')
    except TypeError as e:
        raise container.web.unauthorized(container.output({'error': '401', 'error_description': e}))

    if not __do_auth(uname, pwd):
        container.log.info("Cannot authorize %s:%s" % (uname, pwd))
        raise container.web.unauthorized(container.output({'error': '401', 'error_description': "Bad credentials!"}))
    container.log.debug("Authorized %s" %uname)


def __do_auth(username, password):
    """
    Checks the global clients hash for given username, password pair.
    """
    global clients
    return (username in clients and clients[username] == password)
