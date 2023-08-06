"""
Middle tier for the user authorization and authentication process.


"""
from datetime import datetime
from datetime import timedelta
from hashlib import sha256

from claun.core import container
from claun.modules.users.auth import model

__docformat__ = 'restructuredtext en'
__all__ = ['verify_user', 'get_permissions', 'create_tokens', 'get_user', 'verify_access_token', 'verify_refresh_token', 'DEFAULT_EXPIRATION', 'AccessTokenExpiredError', 'token_expired', 'token_expires_in']


DEFAULT_EXPIRATION = int(container.configuration['modules']['users']['expiration'])
"""Default access token expiration time in seconds"""

SALT = container.configuration['modules']['users']['salt']
"""Super secret random salt that is used for generating tokens"""


class AccessTokenExpiredError(Exception): pass


def verify_user(username, password):
    """
    Checks the model if `username` and `password` combination is valid and if the user is `allowed`.

    Uses sha256 encryption to generate password's hash.
    :return: False or user document as a dictionary
    """
    user = model.user_by_name(username)
    if user is None: return False
    if user.value['allowed'] is False: return False
    if user.value['passwordhash'] == sha256(password).hexdigest():
        return user.value
    else:
        return False

def get_user(username):
    """
    Tries to get user with given username

    :return: user document as a dictionary or None
    """
    user = model.user_by_name(username)
    return user.value if hasattr(user, 'value') else None

def get_permissions(user):
    """
    Gets list of user's permission.
    :rtype: list
    """
    u = get_user(user)
    return u['permissions'] if 'permissions' in u else []


def create_tokens(dbuser, client):
    """Creates new set of access and refresh tokens.

    The tokens are generated with generate_token method and are either newly written in the model
    or the old refresh token is overwritten.

    No copy of old tokens is stored.

    :return: (access token, refresh token)
    :rtype: tuple or None
    """
    if dbuser is None:
        return None
    tokens = dbuser['client_tokens']
    if client not in tokens:
        tokens[client] = {}
    tokens[client]['access'] = generate_token(dbuser['name'], client, SALT)
    tokens[client]['expiration'] = DEFAULT_EXPIRATION
    tokens[client]['created'] = datetime.now().isoformat()
    tokens[client]['refresh'] = generate_token(dbuser['name'], client, SALT)
    model.save(dbuser)
    return (tokens[client]['access'], tokens[client]['refresh'])


def verify_access_token(token):
    """
    Verifies access token against database and its expiration time.

    Checks expiration time and may raise AccessTokenExpiredErorr

    :return: None or user document from database
    """
    user = model.user_by_access_token(token)
    if user is None:
        return None

    if token_expired(user.value['created'], user.value['expiration']):
        raise AccessTokenExpiredError()
    else:
        return user.value['doc']

def token_expired(tokencreated, tokenexpiration):
    """
    Checks the expiration of a token.

    :param tokencreated: When was the token created, datetime in isoformat (%Y-%m-%dT%H:%M:%S.%f)
    :param tokenexpiration: expiration of the token in seconds
    :rtype: boolean
    """
    expirationtime = datetime.strptime(tokencreated, "%Y-%m-%dT%H:%M:%S.%f" ) + timedelta(seconds=tokenexpiration)
    return expirationtime < datetime.now()

def token_expires_in(tokencreated, tokenexpiration):
    """
    In how many seconds will the token expire?

    :param tokencreated: When was the token created, datetime in isoformat (%Y-%m-%dT%H:%M:%S.%f)
    :param tokenexpiration: expiration of the token in seconds
    :rtype: int
    """
    expirationtime = datetime.strptime(tokencreated, "%Y-%m-%dT%H:%M:%S.%f" ) + timedelta(seconds=tokenexpiration)
    return (expirationtime - datetime.now()).seconds


def verify_refresh_token(token, client):
    """Verifies refresh token.

    :return: False or username to which the refresh token belongs
    """
    tokens = model.get_refresh_tokens(client)
    if len(tokens) > 0:
        tok = tokens.__iter__().next().value
        for t in tok:
            if token in t:
                return t[token]
        return False
    else:
        return False


def generate_token(user, client, salt):
    """
    Generates random token.

    Concatenates user, client, salt and current datetime and encodes it with sha256.
    The resulting token consists of version number followed by dash and first thirty
    characters from hexdigest of the encoded string.

    In case of any algorithm change, change the version parameter and provide
    backwards compatibility for legacy implementations.

    :param user: username
    :param client: clientname
    :param salt: secret salt
    :return: unique token
    :rtype: str
    """
    version = 1
    tokens = model.get_all_tokens()
    while True:
        toencode = container.webalize_string(''.join([user, client, salt, datetime.utcnow().isoformat()]))
        token = str(version) + '-' + sha256(toencode).hexdigest()[0:30]
        if token not in tokens:
            return token
