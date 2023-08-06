"""
Claun submodule: Users.Auth
===========================

Description
-----------

This module is meant to authorize physical users accessing the server's resources, typically through
some kind of user interface (for example GUI module).

It is built on the OAuth 2.0 specification (http://tools.ietf.org/html/draft-ietf-oauth-v2-22)
and uses mechanisms described in the chapter 4.3, Resource Owner Password Credentials. The main difference
is the usage of non-standard headers X-Claun-Authentication for client's authentication and X-Claun-User-Token
in later requests that identifies the user himself.

This security measure is independent on the client authentication that is introduced in the claun.core.communication.server module
and serves a different purpose, to distinguish users and their level of privileges. This module only provides the
authentication and authorization methods and does not specify user privileges in any way.

Access control list (or list of users) is kept in the CouchDB and is handled by the `model` module. In the middle is
the `verification` module that provides service methods and functions that either communicate with the model or
perform mundane tasks like generating or comparing data. The logic of working with incoming data and authenticating
users lies in the endpoint classes in this main module.


Getting the initial set of tokens
---------------------------------

The OAuth 2.0 authentication schema works in this implementation roughly like this: A user wants to use one of Claun's
clients (GUIs if you will). He starts the program and it will ask for user credentials. The user fills in the form and
the client issues a Grant request that contains user credentials (both username and password) encoded as in a standard
HTTP Basic Authentication and the client's identification (which is used to distinguish between user's multiple
simultaneous login on different clients). In this implementation it is the X-Claun-Authentication HTTP header with
the same syntax as the standard HTTP Authentication header.

>>> > GET /oauth/token HTTP/1.1
>>> > Host: server
>>> > Accept: */*
>>> > Content-Type: application/x-www-form-urlencoded;charset=UTF-8
>>> > X-Claun-Authentication: Basic Z3VpOmFob2o=
>>> > Content-Length: 46
>>> grant_type=password&username=a&password=b

>>> < HTTP/1.1 200 OK
>>> < Content-Type: application/json;charset=UTF-8
>>> < Cache-Control: no-store
>>> < Pragma: no-cache
>>> <
>>> {"access_token": "1-4e28a4b1b5f6a1e6101f4e0a382620", "expires_in": 86400, "refresh_token": "1-6aed67726ce6f31a116b60e31a0d50", "permissions": ["all", "monitoring"]}

If the user credentials are correct, a pair of access and refresh token is generated that is unique for the user and client
combination. In addition the response contains list of user groups the user is a member of and the amount of seconds in which
the access token will expire. (For example communication see the Token.GET method documentation)

Every following request from the client **has to contain** the X-Claun-User-Token header that follows the OAuth specification
and contains the access token.

>>> X-Claun-User-Token: OAuth 1-4e28a4b1b5f6a1e6101f4e0a382620

(Another option is to add an access_token URI parameter, but this method is discouraged)

The access token has limited validity time and after that will become invalid, the refresh token is valid until the next
refresh is issued.


Protecting resources
--------------------

This token is then used to identify the user in the system and decide if he is authorized to access certain resources.
The protection of resources is performed on the URI level. This module provides two decorators that can be used to
limit the user access.

What they both have in common is that they can inject the user's identity into the method via a keyword argument.
>>> class Something:
>>>     @personalize
>>>     def protected_method(self, path, user=None):
>>>             # some code

They differ in their usage and error awareness.

1. @restrict(['group1', 'group2'])
   The @restrict decorator defines what groups of users can access the resource. So if the user does not belong
   in any of the listed groups, he is forbidden from using the resource and a 400 Bad Request is responded.

2. @personalize
   This decorator is not that strict and may be used when there is a different content for unauthenticated and
   authenticated users, but both groups can access the resource. If there is no valid user identified in the
   request, the user keyword argument is set to None and nothing else is performed.

**Important note:** If a user has *only* invalid access token, he will not be identified by any of the decorators. The
correct behaviour is to refresh tokens and request the resource again.


Refreshing tokens
-----------------
The client can request the refreshing of the tokens at any time, even when his old access token is still valid. This may
become useful when the access token gets compromised. To issue a new pair of tokens, another request to this
module is necessary, this time with different parameters.

>>> > GET /oauth/token HTTP/1.1
>>> > Host: server
>>> > Accept: */*
>>> > Content-Type: application/x-www-form-urlencoded;charset=UTF-8
>>> > X-Claun-Authentication: Basic Z3VpOmFob2o=
>>> > Content-Length: 46
>>> grant_type=refresh_token&refresh_token=1-6aed67726ce6f31a116b60e31a0d50

If the refresh token was correctly assigned to this client, a new pair of tokens is generated and the response has
the same format as was during the initial request. During the refreshing phase, user credentials **are not** needed.

If the refreshing procedure fails (for example there were multiple instances of the same client running), the recommended
process is to re-authenticate the user and use the initial procedure. If there is any valid access token in the system,
no new pair is generated and all client instances get synchronized until the next refreshing phase.

**This whole procedure has to be implemented on the client side of the application.**


ACL definition
--------------
The module depends on the CouchDB backend and uses a separate document for every user (see user.json for example).
User can have the following attributes:
  - name - username
  - id - username in lowercase, spaces replaced with dashes (Super User => super-user)
  - passwordhash - hash of the user's password, the sha256 encryption is used
  - permissions - list of groups the user is a member of
  - allowed - boolean value saying if the user can be logged in
  - client_tokens - dictionary that is filled with information about tokens for certain clients. May be empty.

Pay attention to the 'type' attribute that has to have a value of 'user'.

Endpoints
---------
  - /token Token endpoint

Configuration
-------------
salt: nfCiBmLHUqu4tep4hyNhL0DGy9oPT2C1QBGNJPQeaTgctiQv0YEtb7MyrNsMK2uj - Some secret salt that is used for token generation
expiration: 86400 - Default token expiration in seconds
db_name: claun_users - Database name where the data about users is stored.

Depends on couchdb.

Implementation details
----------------------
Due to the CouchDB revisions conflicts, the refresh-token request may sometimes end up with the 500 Internal Error,
feel free to ask again for the refresh of your set of tokens, it will be successful. This is a known implementation
error and will not be fixed in near future.

"""

import base64
import _strptime # thread lock workaround
from datetime import datetime
from couchdb.http import ResourceConflict

from claun.core import container

from claun.modules.users.auth.verification import *

from claun.vendor.web.webapi import HTTPError


__docformat__ = 'restructuredtext en'
__all__ = ['access_token_expired', 'Root', 'OAuthBadRequest', 'Token', 'restrict', 'personalize']

__uri__ = 'users/auth'
__author__ = 'chadijir'

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/token', 'Token',
           '/', 'Root',
           )

__app__ = container.web.application(mapping, locals())

# helpers

class OAuthBadRequest(HTTPError):
    """
    Custom HTTP Exception 400.
    """
    def __init__(self, data, status='400 BadRequest'):
        headers = {}
        HTTPError.__init__(self, status, headers, data)


def access_token_expired():
    """Fires an `OAuthBadRequest` exception.

    Should be called every time the access token has expired.
    """
    msg = 'Access token expired!'
    error = 'invalid_grant'
    ip = container.web.ctx.env.get('REMOTE_ADDR')
    port = int(container.web.ctx.env.get('REMOTE_PORT'))
    container.log.debug(msg + ' from %s:%i' % (ip, port))
    raise OAuthBadRequest(container.output({'error': error, 'error_description': msg}))


def _badrequest(error, msg):
    """
    Shorthand method for raising errors during the auth process.
    """
    ip = container.web.ctx.env.get('REMOTE_ADDR')
    port = int(container.web.ctx.env.get('REMOTE_PORT'))
    container.log.info(msg + ' from %s:%i' % (ip, port))
    raise OAuthBadRequest(container.output({'error': error, 'error_description': msg}))


# public decorators

def restrict(permissions):
    """
    This is the __restrict method disguised as a decorator. You can use it to limit access to resources to certain groups of users.

    Every decorated method has to have a keyword argument 'user' that is filled with the user identity
    retrieved from database.

    The authentication check is performed within the __restrict method of this module, for more details see
    its documentation.

    >>> class Resource:
    >>>    @restrict(['admin', 'editor'])
    >>>    def GET(self, path, user=None):
    >>>        #some protected code
    >>>        print(user)
    """
    def deco(func):
        def proxyfunc(* args, ** kw):
            kw.update({'user': __restrict(permissions)})
            return func(* args, ** kw)
        return proxyfunc
    return deco

def personalize(func):
    """
    Decorator that injects user identity into a decorated function.

    Decorated function has to have a keyword argument 'user'.
    Uses the __restrict(['all']) method, so if a user has invalid
    token, the identity may be None. No exceptions from __restrict method
    are propagated.

    You should use this method instead of restrict decorator if you want
    to keep the content public but personalized for authorized users.

    >>> class Resource:
    >>>    @personalize
    >>>    def GET(self, path, user=None):
    >>>        #some protected code
    >>>        print(user) #prints None or valid user identity
    """
    def proxyfunc(* args, ** kw):
        try:
            kw.update({'user': __restrict(['all'])})
        except OAuthBadRequest as oa:
            container.web.ctx.status = '200 OK'
            container.log.error("No authorized user found for this request in @personalize, but moving on")
        return func(* args, ** kw)
    return proxyfunc

def __restrict(permissions):
    r"""
    This method can be applied to restricted resources and it can be used for access control.

    For more comfortable usage, look at the redirect method that behaves as a decorator.

    To define restricted access to some resource:

    >>> class Resource:
    >>>   def GET(self, path):
    >>>     __restrict('resource')

    Method checks the access token either in URI or in the proprietary X-Claun-User-Token header.
    Standard Authorization header is not used as it may conflict with the component authorization.
    >>> https://server/monitoring/?access_token=1-9d73f3f66131c51231e4f9c42322d9

    >>> > GET /monitoring/ HTTP/1.1
    >>> > Host: server
    >>> > Accept: */*
    >>> > X-Claun-User-Token: OAuth 1-9d73f3f66131c51231e4f9c42322d9

    It controls the expiration of the access token and may raise OAuthBadRequest.

    :param permissions: list of user groups or one group allowed to see this resource.
    :return: user from database
    :rtype: dict
    """
    if isinstance(permissions, basestring):
        permissions = [permissions]
    # get token
    token = container.web.input(access_token=None)['access_token']
    if token is None: # no token in URI, try headers
        header = container.web.ctx.env.get('HTTP_X_CLAUN_USER_TOKEN')
        if header is None:
            _badrequest('invalid_parameter', 'Missing X-Claun-User-Token HTTP header.')
        split = header.split(' ')
        if split[0] != 'OAuth': # only OAuth method allowed
            _badrequest('invalid_parameter', 'Missing acess token')
        token = split[1]
    # verify token's validity
    try:
        user = verify_access_token(token)
        if user is None: # bad token, no user has this assigned
            _badrequest('invalid_access', 'No user found. (This may be a DB problem)')
        else: # check permissions
            allowed = False
            for p in permissions:
                if p in user['permissions']:
                    allowed = True
                    break
            if not allowed: # invalid access
                _badrequest('invalid_access', 'Not enough rights.')
            return user
    except AccessTokenExpiredError: # it might have expired
        access_token_expired()


# URI endpoints

class Root:
    def GET(self):
        return container.output({
                          'token': container.baseuri + __uri__ + '/token',
                          })

class Token:
    """
    Token endpoint class.
    """

    def _badrequest(self, error, msg):
        """
        Shorthand for module's _badrequest function.
        """
        return _badrequest(error, msg)


    def GET(self):
        r"""
        OAuth 2.0 process for Resource Owner Password Credentials (section 4.3 in http://tools.ietf.org/html/draft-ietf-oauth-v2-22).

        This endpoint can serve password and refresh_token grant types.
        It requires HTTP Basic authentication (modified to use X-Claun-Authentication header instead of standard Authorization)
        from client (name, password) and user's name and password transported in HTTP message body or query string (this differs from the spec).
        The client's X-Claun-Authentication header **IS NOT** verified here. It is however used to assign tokens to a certain client, so it has to
        be present.
        The user is verified with _do_password/_do_refresh method and in case of success issued a set of access and refresh token.

        Example token request:

        >>> > GET /oauth/token HTTP/1.1
        >>> > Host: server
        >>> > Accept: */*
        >>> > Content-Type: application/x-www-form-urlencoded;charset=UTF-8
        >>> > X-Claun-Authentication: Basic Z3VpOmFob2o=
        >>> > Content-Length: 46
        >>> grant_type=password&username=a&password=b

        >>> < HTTP/1.1 200 OK
        >>> < Content-Type: application/json;charset=UTF-8
        >>> < Cache-Control: no-store
        >>> < Pragma: no-cache
        >>> <
        >>> {"access_token": "1-4e28a4b1b5f6a1e6101f4e0a382620", "expires_in": 86400, "refresh_token": "1-6aed67726ce6f31a116b60e31a0d50", "permissions": ["all", "monitoring"]}

        Example refresh request differs only in parameters issued in HTTP message body:
        >>> grant_type=refresh_token&refresh_token=1-6aed67726ce6f31a116b60e31a0d50

        In case of bad request, the response is something like this:
        >>> < HTTP/1.1 400 BadRequest
        >>> < Content-Type: application/json;charset=UTF-8
        >>> < Cache-Control: no-store
        >>> < Pragma: no-cache
        >>> <
        >>> {"error_description": "This token does not go with this client", "error": "invalid_grant"}

        """
        params = container.input(container.web.data(), keep_blank_values=True)
        querystring = container.web.input()

        #normalize parameters
        possible = ['username', 'password', 'grant_type', 'refresh_token']
        for p in possible:
            if p not in params and p in querystring:
                params[p] = querystring[p]
            if p in params:
                if isinstance(params[p], list) and len(params[p]) == 1:
                    params[p] = params[p][0]

        # verify parameters
        if 'grant_type' not in params:
            self._badrequest('invalid_request', "Missing grant type")

        # identify client
        try:
            authheader = container.web.ctx.env.get('HTTP_X_CLAUN_AUTHENTICATION')
            if not authheader:
                self._badrequest('invalid_request', "Missing X-Claun-Authentication HTTP header")
            method, auth = authheader.split(' ')
            clientname, pwd = base64.b64decode(auth).split(':')
        except (AttributeError, TypeError) as e:
            self._badrequest('invalid_request', "Error %s occured" % (e))


        if params['grant_type'] == 'refresh_token': # refresh
            if 'refresh_token' not in params:
                self._badrequest('invalid_request', "Missing refresh token")
            return self._do_refresh(params['refresh_token'], clientname)
        elif params['grant_type'] == 'password': # grant
            if 'username' not in params or 'password' not in params:
                self._badrequest('invalid_request', "Missing username or password")
            return self._do_password(params['username'], params['password'], clientname)
        else:
            self._badrequest('unsupported_grant_type', "Unsupported grant type '%s'" % params['grant_type'][0])

    def _do_password(self, username, password, client):
        """
        Authenticates user with given password and username combination.

        Incorrect password and username combination will raise `_badrequest` and subsequently HTTP 400.

        :param username: Username
        :param password: Password
        :param client: client's name
        :return: data as described in OAuth 2.0 documentation with permissions parameter (for example see GET method)
        """
        # no caching
        container.web.header("Cache-Control", "no-store")
        container.web.header("Pragma", "no-cache")

        # verify user
        user = verify_user(username, password)
        if user: # user exists
            if client in user['client_tokens']: # has tokens
                if token_expired(user['client_tokens'][client]['created'], user['client_tokens'][client]['expiration']): # tokens expired, create new pair
                    access, refresh = create_tokens(user, client)
                    return self._get_success_data(DEFAULT_EXPIRATION, refresh, access, user['permissions'], user['name'], user['id'])
                else: # tokens are still valid
                    return self._get_success_data(token_expires_in(user['client_tokens'][client]['created'], user['client_tokens'][client]['expiration']), user['client_tokens'][client]['refresh'], user['client_tokens'][client]['access'], user['permissions'], user['name'], user['id'])
            else: # no tokens, create new pair
                access, refresh = create_tokens(user, client)
                return self._get_success_data(DEFAULT_EXPIRATION, refresh, access, user['permissions'], user['name'], user['id'])

        else: # invalid user
            self._badrequest('invalid_grant', "Invalid user credentials")

    def _do_refresh(self, refresh_token, client):
        """
        Refresh access token.

        Verifies refresh token and creates a new pair of access and refresh tokens for given client and user
        if the refresh token is valid.
        Wrong combination of client and refresh_token may result into _badrequest and subsequently 400 HTTP.

        :param refresh_token: refresh token
        :param client: client's name
        :return: data compliant to OAuth 2.0 documentation with permissions parameter (for example see GET method)
        """
        # headers
        container.web.header("Cache-Control", "no-store")
        container.web.header("Pragma", "no-cache")

        username = verify_refresh_token(refresh_token, client)
        if not username: # bad client-token combo
            self._badrequest('invalid_grant', "This token does not go with this client")
        user = get_user(username) # get user from db and create new pair of tokens
        if user is None: # bad client-token combo
            self._badrequest('bad_user', "No user found")
        try:
            access, refresh = create_tokens(user, client)
        except ResourceConflict as rc:
            container.log.error('Resource conflict during updating tokens: %s' % rc)
            raise container.web.internalerror(container.output({'error': 'Token creation conflict.', 'error_description': 'Problem when creating new tokens, try again, please.'}))

        return self._get_success_data(DEFAULT_EXPIRATION, refresh, access, user['permissions'], user['name'], user['id'])


    def _get_success_data(self, expiration, refresh, access, permissions, name, id):
        """
        Shorthand for creating the correct response.
        """
        return container.output({
                          'expires_in': expiration,
                          'refresh_token': refresh,
                          'access_token': access,
                          'permissions': permissions,
                          'name': name,
                          'id': id
                          })
