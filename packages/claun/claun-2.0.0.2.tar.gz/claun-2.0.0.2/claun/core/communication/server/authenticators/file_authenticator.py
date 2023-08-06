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

__docformat__ = 'restructuredtext en'

"""
Hash for clients created from configuration file passed to the init method.
"""
clients = {}
endpoints = {}

def init(config, endps):
    """
    Authenticator reads clients username:password pairs from config.credentials_file option.

    Config requires credentials_file field containing path to the credentials file in the config.
    :param endps: hash with endpoints' accessibility
    """
    global clients, endpoints
    configreader = configurator.Configurator(config['credentials_file'])
    clients = configreader.parse()['clients']
    endpoints = endps

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
    Global endpoints hash and the server PATH_INFO variable are used to determine
    the accessibility of an endpoint. If it is a root request (i.e. server.com/, server.com/module/),
    the endpoint is taken from the root endpoints specification.
    
    If the request is for a deeper uri, the module's path list is matched from
    longest to shortest path. If some path matches with public setting, the method
    immediately returns. If a private setting is found, authentication is performed.

    If an endpoint access is to be authenticated or is not registered at all,
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
    global endpoints

    endpoint = container.web.ctx.env.get('PATH_INFO')[1:].split('/', 1)

    # root child or module root
    if len(endpoint) == 1:
        module, uri = ('/', endpoint[0])
    else: # module child
        module, uri = endpoint

    if module in endpoints:
        uri = '/%s' % uri if len(uri) else '/'
        for path in endpoints[module]['__paths']:
            if uri.startswith(path) and endpoints[module][path]:
                container.log.debug('Matching %s against %s: %s' % (uri, path, endpoints[module][path]))
                break
            elif uri.startswith(path) and not endpoints[module][path]:
                container.log.debug('Matching %s against %s: %s' % (uri, path, endpoints[module][path]))
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
