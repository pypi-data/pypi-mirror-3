"""
Simple HTTP client that can be used throughout the whole application. It can use SSL which is turned off by default.

Uses httplib2 library available on http://code.google.com/p/httplib2/. that is included in the vendor package.

There are plenty of configuration possibilities passed here as a dictionary. Possible keys are:
  - default_protocol - http|https, if not specified a http protocol is set as a default protocol
  - ssl_certificates_file - File with the list of allowed/verified certificates, this is an useful option when we
      have self-signed certificates. We do not have to place them in the system wide repository, the simple file is sufficient. During every SSL request, the Httplib then verifies the certificate
      that the contacted server issued. If it is not contained in this file, the certificate is considered invalid and the request is not completed. Such error is propagated as a ClientException and
      has to be handled by the caller of the request. Debugging of such error is not straightforward, so you should always ensure proper list of certificates for all components in the claun system.
      If no file is specified, the default system certificate repository is used.
  - credentials - an optional dictionary that may be used to specify the method of 'signing' all outgoing requests (see credentials_decorators module). If the section is omitted, no 'signing' is done.
    - handler - 'default' or class that will handle/decorate the outgoing requests. (see credentials_decorators module for examples). Default handler is specified in DEFAULT_DECORATOR field in this module.
    - other keys are handler-specific

>>> c = HttpClient({'default_protocol': 'https', 'ssl_certificates_file': 'list', 'credentials': {'handler': 'BasicHTTPAuthDecorator', 'username': 'a', 'password': 'b'}})
>>> cx = HttpClient({})
>>> c.request(address='http://example.com/resource')
>>> c.request(address='https://example.com:8088/resource')
>>> c.request('example.com', '8088', 'resource')
>>> c.request('example.com', '8088', 'resource', body='{"Hello": "world"}', headers={'content-type': 'application/json'}, method = POST, protocol = 'http') # you can override the protocol, method, or some headers
"""

import socket

from claun.core import log
from claun.core import container
from claun.core.communication.client.credentials_decorators import *

import httplib2

__docformat__ = 'restructuredtext en'

GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'
HEAD = 'HEAD'
TIMEOUT = 10

DEFAULT_DECORATOR = BasicHTTPAuthDecorator

class HttpClient:
    def __init__(self, configuration):
        """
        Sets up the HTTP client. For configuration dictionary options, see the module documentation.

        Apart from SSL, a credentials_decorator may be instantiated based on the passed configuration.
        Credentials decorators are implemented in credentials_decorators module in this package.
        They are used to 'sign' all outgoing requests to provide higher level of security when
        requesting the server. This might include Basic HTTP authentication, Digest HTTP authentication
        or other (even application specific) methods. It is possible to implement more logic in the decorator
        and sign requests for different resources with different methods.

        The key principle is the delegation of the whole request to the decorator when one is defined.
        Thanks to this delegation even multiple requests may be performed to obtain a protected resource.

        For more credentials decorator information see the credentials_decorators module.

        :param configuration: configuration of the client (see module documentation)
        """
        self.configuration = configuration

        # protocol and ssl checking
        self.protocol = self.configuration.get('default_protocol', 'http')
        self.certificates = self.configuration.get('ssl_certificates_file', None)
        if self.certificates:
            container.log.info('Client will verify server certificates...')
        else:
            container.log.info('Client will recognize only system specified certificates...')

        # credentials
        self.credentials_decorator = None
        if 'credentials' in self.configuration:
            if self.configuration['credentials']['handler'] == 'default':
                self.credentials_decorator = DEFAULT_DECORATOR(self.configuration['credentials'])
                container.log.info('Going with %s as a default...' % DEFAULT_DECORATOR)
            else:
                try:
                    handlername = self.configuration['credentials']['handler']
                    self.credentials_decorator = globals()[handlername](self.configuration['credentials'])
                    container.log.info('Going with %s as a credentials decorator...' % handlername)
                except KeyError:
                    container.log.fatal('Credentials decorator %s not found!' % handlername)
                    raise ClientException('Credentials decorator %s not found!' % handlername)

    def request(self, server = None, port = None, path = None, address = None, body = None, headers = {}, method = GET, protocol = None):
        """
        Performs request to given address.

        This method should be used as the only mean of communication with the world outside of the component.
        It is just decorated request method from httplib2.Http object. For every request, new Http object is created.
        if no address is given, it is constructed from protocol, server, port and path.
        If no address is specified, server and port and path **must** be specified. (ClientException is risen otherwise)

        If a credentials decorator was registered during the startup, the request itself is delegated
        to the decorator. Otherwise, plain httplib2.Http.request method is called.

        When issuing the request, information about acceptable media types is injected as Accept header
        if it is not present in ``headers``. Response is then decoded based on the content-type header
        by claun.core.communication.io.input method taken from the global container.

        If the response has not code 200, a ClientException is always risen. (This might change to reflect REST principles)

        :param server: Server name, i. e. stuff.example.com
        :param port: Server port, i. e. 8080
        :param path: Path after the server name. It **must** contain the leading slash!
        :param address: Whole address, i. e. https://stuff.example.com/elephants (including the protocol)
        :param body: Message HTTP body, no headers or encoding is done here
        :param headers: HTTP headers as a dictionary (empty by default)
        :param method: HTTP method, GET by default
        :param protocol: If no protocol is specified, protocol given in the class configuration is used.
        :return: Response tuple, (stats, content)
        """
        try:
            protocol = self.protocol if protocol is None else protocol
            self.http = httplib2.Http(timeout = TIMEOUT, ca_certs = self.certificates) # no caching

            # address construction
            if address is None:
                if server is None or port is None or path is None:
                    raise ClientException("Cannot create a request url!")
                url = '%s://%s:%i%s' % (protocol, server, port, path)
            else:
                url = address

            if 'accept' not in [h.lower() for h in headers.keys()]:
                headers['Accept'] = ', '.join(container.input.all_available())

            # credentials decorator?
            if self.credentials_decorator is not None:
                container.log.debug("Requesting %s (with credentials)" % url)
                response = self.credentials_decorator.request(self.http, url, method, body, headers)
            else:
                container.log.debug("Requesting %s" % url)
                response = self.http.request(url, method = method, body = body, headers = headers)

            if response[0]['status'] != '200':
                raise ClientException('Remote error: %s - %s' % (response[0]['status'], response[1]), response)

            return (response[0], container.input(response[1], header=response[0]['content-type']))
        except httplib2.HttpLib2Error as she:
            raise ClientException(she)
        except socket.error as se:
            raise ClientException(se)

class ClientException(Exception):
    def __init__(self, msg, response=None):
        Exception.__init__(self, msg)
        self.response = response


container.errors.ClientException = ClientException
container.http_methods = container.ObjectContainer()
container.http_methods.GET = GET
container.http_methods.POST = POST
container.http_methods.PUT = PUT
container.http_methods.DELETE = DELETE
container.http_methods.HEAD = HEAD
