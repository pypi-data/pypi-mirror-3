"""
credentials_decorators module contains classes that can be used
to 'sign' requests leaving the component. They can handle HTTP authentication or some other
mechanisms like OAuth.

Decorator has to be specified in the component's configuration file and is injected into
the component during the HttpClient startup. The configuration section is optional.
"""
import base64

__docformat__ = 'restructuredtext en'
__all__ = ['BasicHTTPAuthDecorator']


class VoidAuthDecorator:
    """
    Mock class showing the interface of every credentials decorator.

    *** DO NOT USE IN PRODUCTION ***
    """
    def __init__(self, config):
        """
        Initializes the decorator class.

        :param config: dictionary containing configuration information
        """
        pass

    def request(self, http, url, method, body, headers):
        """
        Sends the real HTTP request.

        :param http: httplib2.Http object
        :param url: URL that is requested
        :param method: HTTP method
        :param body: Message body
        :param headers: HTTP headers as a dictionary. If None, it should be created here if necessary.
        """
        pass


class BasicHTTPAuthDecorator(VoidAuthDecorator):
    """
    HTTP credentials decorator using Basic HTTP authentication in X-Claun-Authentication header.

    X-Claun-Authentication header is used for compatibility only, it has the same syntax as standard HTTP Authorization header.
    The implementation provided here is fully compatible with the claun.core.communication.server.authenticators.file_authenticator module.
    This method is set as a default mechanism for identifying the outgoing requests.
    """
    def __init__(self, config):
        """
        Constructs the authorization string using base64 encoding.

        Requires username and password fields in config dictionary.
        :param config: {username: 'aa', password: 'bb'}
        """
        self.authstring = base64.b64encode(config['username'] + ':' + config['password'])

    def request(self, http, url, method, body, headers):
        """
        Performs request that is enhanced with X-Claun-Authentication header.

        No error checking is done here.

        :param http: httplib2.Http object
        :param url: URL that is requested
        :param method: HTTP method
        :param body: Message body
        :param headers: HTTP headers as a dictionary. If None, it is created here.
        """
        if headers is None:
            headers = {}
        headers['X-Claun-Authentication'] = "Basic %s" % self.authstring
        return http.request(url, method = method, body = body, headers = headers)
