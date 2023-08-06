"""
Core HTTP server built on web.py framework and its integrated webserver.

Module contains some basic URI endpoints like 404 (NotFound) error page, redirect to the main page (RedirToRoot) or Favicon.

The main server class HttpServer can be configured with the passed configuration which is a dictionary that may
contain following keys:
  - ip - IP address where the server will be listening (mandatory)
  - port - Port where the server will be listening (mandatory)
  - fqdn - Fully Qualified Domain Name, which is used for some pretty output (mandatory)
  - ssl_certificate - Path to a public certificate that identifies the SSL server
  - ssl_key - Path to a private key that is used when SSL is active. Both ssl_ prefixed options have to be present to turn SSL on.
  - ssl_adapter - CherryPy webserver can provide SSL support by more adapters. Currently supported values are 'builtin' and 'pyopenssl'. 'builtin' is default.
    To use pyopenssl, you have to have the library and OpenSSL installed.
  - client_authentication - This optional section, if present, describes how any incoming requests should be treated. It is possible to limit access
    to certain resources by this configuration option.
      - handler - 'default' or module that handles the client authentication. There is a vast amount of possibilities - checking headers, using database, IP range...
        For more details, see authenticators module. Default handler is specified in DEFAULT_AUTHENTICATOR field in this module.
      - global - true|false - if set to true, all reachable endpoints will be protected by the handler (Except component root and favicon which are always public).
        If false, all endpoints will be public by default, however you can override both settings on a finer level:
          1. Module-level: Using the public|private configuration option. Both options contain list of child endpoints that should be public/private.
             You can use the '*' wildcard to apply the settings to whole module.
          2. URI-level: Each handler should provide the 'authenticate' method that can be called anywhere in your program to verify the request originator. It is wired
          in the global container during startup.
          3. URI-level: It should be possible to use a decorator for every endpoint, however this possibility is **not** currently available.
      - other options that depend on the particular handler

>>> s = HttpServer({'ip': '127.0.0.1', 'port': '80', 'fqdn': 'example.com'}) # public server with no SSL
>>> s = HttpServer({'ip': '127.0.0.1', 'port': '80', 'fqdn': 'example.com', 'ssl_certificate': 'path/to/cert', 'ssl_key': 'path/to/key'}) # server with SSL responding only on https
>>> s.start()

Security example
----------------
Note: The leading slash is important. The algorithm matches against the longest
path.

You want to keep the whole system restricted, only module 'allaccess' should be publicly accessible:
>>> ...
>>> communication:
>>>   server:
>>>     client_authentication:
>>>       global: on
>>> ...
>>> modules:
>>>   allaccess:
>>>     public: [/]

You want to keep the whole system public, only module 'restricted' should be publicly not accessible:
...
>>> communication:
>>>   server:
>>>     client_authentication:
>>>       global: off
>>> ...
>>> modules:
>>>   restricted:
>>>     public: [/]

You want to keep the whole system private, only module 'mixed' should publicly expose everything in /help:
>>> ...
>>> communication:
>>>   server:
>>>     client_authentication:
>>>       global: on
>>> ...
>>> modules:
>>>   mixed:
>>>     public: [/help]

You want to keep the whole system restricted, only module 'mixed' should be publicly accessible except everything in /secret:
>>> ...
>>> communication:
>>>   server:
>>>     client_authentication:
>>>       global: on
>>> ...
>>> modules:
>>>   public: [/]
>>>   private: [/secret]

You want to keep the whole system restricted, only module 'mixed' should publicly expose /help except everything in /help/secret:
>>> ...
>>> communication:
>>>   server:
>>>     client_authentication:
>>>       global: on
>>> ...
>>> modules:
>>>   public: [/help]
>>>   private: [/help/secret]

"""

import sys
import threading

from claun.core import container
from claun.core import log
from claun.core.communication.server.authenticators import *

from claun.vendor.web.wsgiserver import CherryPyWSGIServer

__docformat__ = 'restructuredtext en'

### Main server class
"""Default authenticator module. If the appropriate section is omitted in the configuration, **no** authenticator is used."""
DEFAULT_AUTHENTICATOR = file_authenticator

class HttpServer(threading.Thread):
    """
    Main HTTP Server class that runs as a system daemon. Uses web.py CherryPyWSGIServer.

    :param configuration: Dictionary with configuration. See module documentation for configuration options.
    """
    def __init__(self, configuration):
        """
        Initializes threading and prepares urls for the application using fill_urls method.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.configuration = configuration
        self.protocol = 'http'
        self.urls = ()
        self.fill_urls()

    def fill_urls(self):
        """
        Fills URI endpoints for all loaded modules and some basic component endpoints.

        __uri__ and __app__ module parameters are used to create basic URIs. This uses the subapplication capability of web.py
        In addition to modules are registered endpoints for favicon, component's root and default 404 fallback.
        """
        for module in container.modules.values():
            self.urls += '/' + module.__uri__, module.__app__
        self.urls += ('/favicon.ico', 'claun.core.communication.server.Favicon')
        self.urls += ('/', 'claun.core.communication.server.Root')
        self.urls += ('/(.*)', 'claun.core.communication.server.NotFound')

    def run(self):
        """
        Main server method, SSL, authenticators and web.py application are set up here.

        Firstly, the SSL. It is based on the passed configuration. If the ssl_ prefixed options are present, SSL is turned on
        using the CherryPyWSGI properties. Also the working protocol is set to https. If the ssl_adapter option
        is not one of the builtin|pyopenssl, the server is terminated.

        And client authentication follows. Again, this is optional and the appropriate configuration may be omitted.
        But if present, an allowed/restricted endpoints list is created for each module, and a handler is imported and registered.
        In addition, an authentication loadhook is registered and an 'authenticate' method is wired into the global container as client_authentication.

        The list of allowed/restricted endpoints is a dictionary that has the following format:
          - every key stands for one loaded module's uri without the leading slash.
            Systems's root has the implicit '/' key.
          - under every key is stored another dictionary that describes behaviour
            in that module
            - the key should start with a leading slash and represents settings for one path
            - the key's value is True for authenticate, False for let go
          - For every module a '/' endpoint is filled automatically based
            on the client_authentication:global option.
          - This settings is then overwritten with configuration of every module
            (public/private options)
          - In addition a key called __paths is created that contains all sorted paths,
            the longest first (to ease the matching)
          - To ease the matching, all modules are passed to the '/' as well (this is
            handy for canonical redirection to uris with trailing slash)
          - Also, favicon.ico and / are always public.

          examples:
            'applications': {'/admin/help': False, '/': True, '__paths': ['/admin/help', '/']}
            '/': {'favicon.ico': False, 'applications': True, '__paths': ['applications', 'favicon.ico', '/'], '/': False}

        See ``file_authenticator`` for matching details.

        Finally, a web.py application is started.
        """
        try:
            # SSL
            if 'ssl_certificate' in self.configuration and 'ssl_key' in self.configuration:
                adapter_type = self.configuration.get('ssl_adapter', 'builtin')
                if adapter_type in ['builtin', 'pyopenssl']:
                    if adapter_type == 'builtin':
                        from claun.vendor.web.wsgiserver.ssl_builtin import BuiltinSSLAdapter
                        CherryPyWSGIServer.ssl_adapter = BuiltinSSLAdapter(self.configuration['ssl_certificate'],self.configuration['ssl_key'])
                        container.log.info('Using BuiltInSSLAdapter')
                    elif adapter_type == 'pyopenssl':
                        CherryPyWSGIServer.ssl_certificate = self.configuration['ssl_certificate']
                        CherryPyWSGIServer.ssl_private_key = self.configuration['ssl_key']
                        container.log.info('Using pyOpenSSLAdapter')
                    container.log.info('Setting up SSL server...')
                    self.protocol = 'https'
                else:
                    container.log.critical('Unsupported SSL adapter %s' % adapter_type)
                    sys.exit(1)

            # setup the app
            self.app = container.web.application(self.urls, globals())

            self.app.add_processor(container.web.unloadhook(allow_cors_unloadhook))

            # client authentication
            if 'client_authentication' in self.configuration:
                if self.configuration['client_authentication']['handler'] == 'default':
                    cliauthhandler = DEFAULT_AUTHENTICATOR
                    container.log.info('Loading %s as default authenticator...' % DEFAULT_AUTHENTICATOR.__name__)
                else:
                    handler = self.configuration['client_authentication']['handler']
                    module = __import__('authenticators.' + handler, globals(), locals(), [handler])
                    cliauthhandler = module
                    container.log.info('Loading %s as authenticator...' % handler)

                # authentication exceptions
                default_auth = True if self.configuration['client_authentication']['global'] else False
                endpoints = {
                        '/': {
                            '/': False,
                            '/favicon.ico': False
                        }
                } # always allow root and favicon
                for module in container.modules.values(): # setup defaults
                    endpoints[module.__uri__] = {}
                    endpoints[module.__uri__]['/'] = default_auth
                    endpoints['/']['/%s' % module.__uri__] = default_auth

                mods = container.configuration['modules'] # override with yaml configuration
                for name, config in mods.iteritems():
                    if config is not None and 'public' in config:
                        for end in config['public']:
                            if end == '*':
                                endpoints[container.modules[name].__uri__]['/'] = False
                            endpoints[container.modules[name].__uri__][end] = False
                            if end in ['*', '/']:
                                endpoints['/']['/%s' % container.modules[name].__uri__] = False
                    if config is not None and 'private' in config:
                        for end in config['private']:
                            if end == '*':
                                endpoints[container.modules[name].__uri__]['/'] = True
                            endpoints[container.modules[name].__uri__][end] = True
                            if end in ['*', '/']:
                                endpoints['/']['/%s' % container.modules[name].__uri__] = True

                for name, auth in endpoints.iteritems():
                    endpoints[name]['__paths'] = sorted(auth.keys(), key=lambda x: len(x), reverse=True)

                # setup handler, register loadhook and authenticate method
                cliauthhandler.init(self.configuration['client_authentication'], endpoints)
                self.app.add_processor(container.web.loadhook(cliauthhandler.loadhook))
                container.log.info('Added authentication loadhook...')
                container.client_authentication = cliauthhandler.authenticate
                container.log.info('Registered client authentication method into container')


            # ugly, but necessary :-(
            sys.argv[1] = self.configuration['ip'] + ':' + str(self.configuration['port'])
            container.baseuri = '%s://%s:%s/' % (self.protocol, self.configuration['fqdn'], self.configuration['port'])
            self.app.run()
        except Exception as e:
            container.log.fatal("Can't start server: %s" % e)
            sys.exit(1)


# loadhook
def allow_cors_unloadhook():
    if 'cors' in container.configuration['communication']['server']:
        container.web.header('Access-Control-Allow-Origin', container.configuration['communication']['server']['cors'], True)
        container.web.header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE', True)
        container.web.header('Access-Control-Allow-Headers', 'Content-Type, Origin, Accept, X-Claun-Authentication, X-Claun-User-Token', True)
        allowheader = filter(lambda x: x[0] == 'Allow', container.web.ctx.headers)
        if allowheader:
            container.web.header('Allow', 'OPTIONS')

### Default request endpoints

class NotFound:
    """
    Default 404 Page
    """
    def GET(self, path):
        raise container.web.notfound("This is '%s' running, path '/%s' seems to be not mapped to anything...\n" % (container.configuration['communication']['server']['fqdn'], path))

class Root:
    """
    Root endpoint of the component. Displays information about version, name and all loaded modules.
    """
    def GET(self):
        return container.output({
                                "component_version": container.configuration['version'],
                                "component": container.configuration['name'],
                                "platform": container.configuration['platform'],
                                "system": "Claun",
                                "system_version": container.claun_version,
                                "available_modules": dict([(i, container.baseuri + j.__uri__ + '/') for i, j in container.modules.iteritems()]),
                                "media_types": {
                                        "produced": container.output.available,
                                        "accepted": container.input.available
                                }
                                })

class RedirToRoot:
    """
    Redirects to the root of the application. (May be used in subapplications(=modules))
    """
    def GET(self):
        raise container.web.seeother('/')

class Favicon:
    """
    Endpoint for the favicon image. It is encoded in-place to save file reads.

    No additional encoding is used, it is the rough output of the file.read() method.
    """
    def GET(self):
        container.web.header('Content-Type', 'image/x-icon')
        container.web.header('Cache-Control', 'max-age=86400, must-revalidate')
        return '\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x00\x00\x00\x00h\x05\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 ' + \
                '\x00\x00\x00\x01\x00\x08\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x002;' + \
                '\xb6\x009S\xe2\x00Kj\xf9\x00Qi\xed\x00HO\xcd\x00BP\xd9\x00\xd9\xdd\xf7\x00\xd3\xc3\xce\x00\xe8\xe0\xd3\x00AU\xdf\x00:<\xb9\x00Pn' + \
                '\xfc\x007<\xc2\x00So\xf6\x00^W\xa6\x00\xaa\xaf\xf6\x00CU\xe8\x00\x80\x86\xd7\x00@Y\xeb\x00ms\xc3\x00~}\x90\x00T`\xca\x00Fb\xf4\x00' + \
                '\xb1\xa3\xc1\x00Ie\xf4\x00`}\xfc\x00Gd\xfa\x00Kg\xf1\x00HJ\xc8\x00Lk\xf4\x0027\xbd\x00Mk\xf4\x00\xad\xac\xdc\x00\x88\x80\xb4\x00' + \
                '\x1a\x1ah\x00(\'\xa9\x00\x83\x86\xd8\x00\xd3\xd1\xd5\x00\x83\x89\xd8\x00cr\xe5\x00C^\xf2\x00CH\xba\x00LN\x9f\x00\xab\x9f\xd1\x00ZM' + \
                '\x93\x00AO\xcf\x00\x95\x94\xcc\x00##\x9e\x00\xca\xc8\xcd\x00e\x8a\xf7\x00\xd7\xdd\xf9\x00AS\xdb\x00HN|\x004>\xc1\x00>W\xe7\x00MOv' + \
                '\x00?Y\xed\x00;B\xbb\x00A[\xea\x00KC\x9a\x00@]\xf0\x008J\xc1\x00\xdc\xce\xcd\x00Fc\xf0\x00FK\xbb\x00\x99\x8f\xbe\x00\xad\xa6\xd5' + \
                '\x00Li\xf0\x00_b\xd2\x005S\xee\x00\x0f\x0c8\x00;D\xa7\x00@>\xa7\x00\xf6\xf6\xfc\x009>\xc2\x00>Z\xf1\x00\xe4\xe4\xf4\x00JE\xa1' + \
                '\x00;Ar\x00n{\xcc\x00ZZ\xcd\x00\xae\xac\xbb\x00^^\xc7\x00\xd4\xd6\xf8\x00c\x81\xf9\x00<9\xa2\x00\xf1\xf2\xfa\x00\xf5\xf0\xf4\x00JP' + \
                '\xd4\x00cp\xd0\x00\xa6\xb1\xf7\x00hm\xd0\x00Uq\xf7\x00\xfd\xf9\xf4\x00bv\xd9\x00B`\xf2\x008D\xde\x00[Yr\x00\x86\x91\xe1\x00\x9b\x91' + \
                '\xbd\x00AO\xd2\x00Lk\xf8\x00f\x86\xf7\x00BT\xd8\x00\xe3\xdf\xe7\x00eU\x93\x00Zq\xef\x00@\\\xf0\x00R[\xc9\x009J\xc4\x00B_\xf0\x00av' + \
                '\xec\x00Ea\xed\x00--\xb6\x00\xb4\xbd\xef\x00Fe\xf0\x00He\xf0\x005A\xa1\x0056\xbf\x00\xb6\xab\xcc\x00Pl\xf3\x00RS\xbb\x00:@\xb0\x00' + \
                '\xb6\xb6\xdb\x004D\xce\x00\xaf\xb4\xf0\x00A[\xee\x00=A\xc5\x00\x81~\x90\x00\xff\xff\xff\x00<G\xce\x00\x1c\x19>\x00\xc5\xbf\xc9\x00' + \
                '\xad\xa4\xca\x00;J\xd7\x00\x96\x90\xc5\x00:8\xa2\x00o|\xed\x00\\a\x8c\x00\xf2\xf5\xfd\x00kj\xca\x007E\xc0\x00\x8d\x85\xc0\x00\xf1' + \
                '\xe1\xd4\x00CY\xe9\x00\x87\x8c\xc3\x007I\xc3\x008?\xd2\x00Yv\xf7\x00Zu\xfd\x00?E\xc9\x0041\xa0\x00\xe8\xea\xf8\x0006\xaf\x00|{\xc7' + \
                '\x00Kh\xf2\x00\x8a\x93\xea\x00=R\xde\x000.t\x00@S\xd8\x00}~\xd0\x00\xcd\xc5\xd3\x00MQ\xc9\x00y\x80\xdf\x00\xaa\xaf\xec\x00@X\xe7' + \
                '\x00\xc8\xca\xeb\x00AZ\xe4\x00;F\xb2\x00\xb4\xb9\xd4\x00CZ\xe4\x00\xe0\xc9\xc4\x008A\xd0\x00^z\xe9\x009D\xd0\x00[y\xf8\x00\x9c\x91' + \
                '\xa6\x00\x9e\x8e\xaf\x00Hd\xf0\x0093\x9e\x00e`\xb7\x00\xf7\xef\xe4\x00p{\xe3\x00\x9a\x98\xbb\x00\xe5\xd5\xd6\x00\xcd\xc6\xc5\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00cc\x81\x81h.\x8cPD$\xa6\x81\x81' + \
                '\x81\x81\x81EEE!\xb3q\xaem=|\xac[V\x81\x81\x81EE\x0e#JGN7\x8a4u`\xa2I\x81\x81cc/\n\xa8\x9eH\x1cX\x04z\x96\x93&\x81\x81\x81M\x99' + \
                '\x8d\x005d3\xa5~\x90\x05\x10\x86\x98\x81\x81\x88@\x87\x85\x11\x9f\xa7?\x1b_K\x168\x06\x81\xa1\x97\x8e\xab+\x17\x9a\x01\x1f\x18' + \
                '\xb6B\xa3k2\x81\xb0UA\x07"\x83\x136eow\xb8\x8f\'\x8b\x81\xb7;y>\x14\x80l:\x0b\x15F*]\x9c\x81\x81{,\x1eR \xa0\x82p\x02YaQS\x0fc' + \
                '\x81Li9\x7fv\x0c\tts\x03\xa4}\x89EE\x0f\x81\xb1)-g\xaa\xb2\x1d\x9b\x12<EZEEE\x81W\xb4\x9dt\r\x94\\\x94xnjEEEE\x81\x81\x84\x92' + \
                '\x1a\x95\x19Tf\xaf(r\x81\x0fEE\x81\x81\x81\xb9\x91O^\xad1Cb\x81\x81\x0fcc\x81\x81\x81\x81\x81\xb5\x080\xa9%\x81\x81\x81\x81\x81' + \
                '\x810\x1f\x00\x00\x00\x07\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x80\x01\x00\x00\x80\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00' + \
                '\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\xc0\x08\x00\x00\xe0\x18\x00\x00\xf8?\x00\x00'
