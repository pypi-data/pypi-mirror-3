"""
Model layer for the user authentication scheme. Uses CouchDB.

During startup a database may be created and views will be
synchronized.

The only database modifying method in this module is the
save method, so use carefully.
"""


from claun.core import container
from claun.modules.couchdb import client as db
from claun.modules.couchdb import CouchError


__docformat__ = 'restructuredtext en'
__all__ = ['get_refresh_tokens', 'user_by_name', 'get_all_tokens', 'user_by_access_token', 'save']

DB_NAME = container.configuration['modules']['users']['db_name']
"""Default db name. It is created if it does not exist."""

####

def users_by_name(doc):
    """
    Map all documents with type 'user' by name.

    Resulting pairs: [username: {values}]
    """
    if doc['type'] == 'user':
        yield(doc['name'], doc)

def all_tokens_map(doc):
    """
    Map all refresh/access tokens from all users.

    This might be useful when generating unique token.
    Resulting pairs: [clientname: [tokens]]
    """
    if doc['type'] == 'user':
        for name, cl in doc['client_tokens'].iteritems():
            tokens = []
            if 'refresh' in cl:
                tokens.append(cl['refresh'])
            if 'access' in cl:
                tokens.append(cl['access'])
            yield(name, tokens)

def refresh_tokens_by_client_map(doc):
    """
    Map all refresh tokens for one certain client.

    Resulting pairs: [clientname: {refreshtoken: username}]
    """
    if doc['type'] == 'user':
        for name, cl in doc['client_tokens'].iteritems():
            if 'refresh' in cl:
                yield(name, {cl['refresh']: doc['name']})

def refresh_tokens_by_client_reduce(keys, values):
    return values


def users_by_access_token(doc):
    """
    Map all users with this access token.

    Resulting pairs: [accesstoken: {created: date, expiration: expirationinseconds, doc: uservalues}]
    """
    if doc['type'] == 'user':
        for k in doc['client_tokens'].itervalues():
            yield(k['access'], {'created': k['created'], 'expiration': k['expiration'], 'doc': doc})

# sync DB
try:
    db.touch_database(DB_NAME)
    views = [
            db.define_view('users', 'by_name', users_by_name),
            db.define_view('users', 'by_access_token', users_by_access_token),
            db.define_view('tokens', 'all', all_tokens_map),
            db.define_view('tokens', 'refresh_by_client', refresh_tokens_by_client_map, refresh_tokens_by_client_reduce),
            ]
    db.sync_views(DB_NAME, views, True)
except CouchError as ce:
    raise container.errors.FatalError(ce)

# public API

def get_refresh_tokens(client):
    """
    Performs the tokens/refresh_by_client view for given client.

    :return: all refresh tokens for given client or [].
    """
    try:
        result = db.view(DB_NAME, 'tokens/refresh_by_client', key=client)
        if len(result) > 0:
            return result
    except CouchError as ce:
        container.log.error(ce)
    return []


def user_by_name(name):
    """
    Tries to get a user with given name.

    :return: None or user document
    """
    try:
        result = db.view(DB_NAME, 'users/by_name', key=name)
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("User by name error: %s" % e)
        return None

def get_all_tokens():
    """
    Performs the tokens/all view.

    :return: all tokens in the system or empty list
    """
    try:
        return db.view(DB_NAME, 'tokens/all')
    except CouchError as ce:
        container.log.error(ce)
    return []

def user_by_access_token(token):
    """
    Tries to get a user object with valid access `token`.

    :return: None or user document.
    :param token: access token
    """
    try:
        result = db.view(DB_NAME, 'users/by_access_token', key=token)
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("User by access token error: %s" % e)
        return None

def save(entity):
    """
    Saves entity to DB_NAME.

    No checks are performed, nothing is returned.
    Uses save_document method from `claun.modules.couchdb.wrapper`
    """
    try:
        db.save_document(DB_NAME, entity)
    except CouchError as ce:
        container.log.error(ce)
