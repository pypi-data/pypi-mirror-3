"""
Model layer for the user authentication scheme. Uses CouchDB.

During startup a database may be created and views will be
synchronized.
"""

from claun.modules.couchdb import client as db
from claun.core import container
from claun.modules.couchdb import CouchError


__docformat__ = 'restructuredtext en'

DB_NAME = container.configuration['modules']['users']['db_name']
"""Default db name. Database should be created if it does not exist."""

class ModelError(Exception): pass

####

def groups_by_name_map(doc):
    """
    All groups by name.

    Resulting pairs: [groupname: None]
    """
    if doc['type'] == 'groups':
        for name in doc['groups']:
            yield (name, None)

def groups_raw_map(doc):
    """
    Raw groups document, useful when modifying groups.
    """
    if doc['type'] == 'groups':
        yield (doc['_id'], doc)


def users_by_id(doc):
    """
    Map all documents with type 'user' by name.

    Resulting pairs: [user.id: {values}]
    """
    if doc['type'] == 'user':
        yield(doc['id'], doc)


# public API
def all_groups():
    """
    All groups, uses groups/by_name.
    :rtype: ViewResults or []
    """
    try:
        return db.view(DB_NAME, 'groups/by_name')
    except CouchError as ce:
        container.log.error(ce)
        return []

def raw_groups():
    """
    Raw group document, uses groups/raw.

    May return None, if no such document is found.
    """
    result = db.view(DB_NAME, 'groups/raw')
    try:
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Group retrieval error: %s" % e)
        return None

def get_group(name):
    """
    Get one group by name, uses groups/by_name.

    If no such group is found, returns None.
    """
    result = db.view(DB_NAME, 'groups/by_name', key=name)
    try:
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Group retrieval error: %s" % e)
        return None

def delete_group(groupname):
    """
    Tries to delete group from raw groups document.

    If no such group exists, a ModelError is raised.
    :param groupname: String
    :rtype: boolean
    """
    groups = raw_groups()
    try:
        if groups is not None and 'groups' in groups.value and groupname in groups.value['groups']:
            groups.value['groups'].remove(groupname)
            return db.save_document(DB_NAME, groups.value) is not None
    except CouchError as ce:
        container.log.error(ce)
        return False
    except ValueError:
        raise ModelError('No such group.')

def create_group(groupname):
    """
    Calls replace_group(groupname, groupname).

    :param groupname: String
    """
    return replace_group(groupname, groupname)

def replace_group(old, new):
    """
    Replaces `old` with `new` in the rwa groups document.

    May raise ModelError if no group definition is found.

    :param old: String
    :param new: String
    """
    groups = raw_groups()
    try:
        if groups is not None and 'groups' in groups.value:
            try:
                groups.value['groups'].remove(old)
            except ValueError:
                pass
            if new not in groups.value['groups']: groups.value['groups'].append(new)
            return db.save_document(DB_NAME, groups.value)
    except CouchError as ce:
        container.log.error(ce)
        return None
    raise ModelError('Cannot find group definition.')


def all_users():
    """
    All users, uses users/by_id.
    """
    try:
        return db.view(DB_NAME, 'users/by_id')
    except CouchError as ce:
        container.log.error(ce)
        return []

def get_user(name):
    """
    One user, uses users/by_id.

    If no user is found, None is returned.
    """
    result = db.view(DB_NAME, 'users/by_id', key=name)
    try:
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("User retrieval error: %s" % e)
        return None

def delete_user(user):
    """
    Tries to delete user.

    :param user: Dictionary/document, has to contain _id field.
    :rtype: boolean
    """
    if '_id' not in user:
        raise ModelError('Missing _ID')
    try:
        return db.delete_document(DB_NAME, user) is None
    except CouchError as ce:
        container.log.error(ce)
        return False

def create_user(user):
    """Creates user as a new document.

    If user with `id` already exists, a ModelError is raised.

    :param user: Dictionary with user, has to contain `id` key
    :return: (id, rev) tuple of the newly saved document
    """
    if 'id' not in user:
        raise ModelError('Missing ID')
    if get_user(user['id']) is not None:
        raise ModelError('User with that id already exists.')
    try:
        return db.save_document(DB_NAME, user)
    except CouchError as ce:
        container.log.error(ce)
        return None

def save_user(user, docid=None, revid=None):
    """Updates user.

    You can specify `_id` and `_rev` either directly in the dictionary
    or as separate arguments. If `_id` or `_rev` are not present in either form,
    a ModelError is raised.

    :param user: Dictionary with user
    :param docid: `_id` attribute, if `user` contains `_id` field, may be None
    :param revid: `_rev` attribute, if `user` contains `_rev` field, may be None
    :return: (id, rev) tuple of the newly saved document
    """
    if '_id' not in user:
        if docid is None:
            raise ModelError('No ID specified!')
        user['_id'] = docid

    if '_rev' not in user:
        if revid is None:
            raise ModelError('No revision specified!')
        user['_rev'] = revid
    try:
        return db.save_document(DB_NAME, user)
    except CouchError as ce:
        container.log.error(ce)
        return None

# sync DB
try:
    db.touch_database(DB_NAME)
    views = [
        db.define_view('groups', 'by_name', groups_by_name_map),
        db.define_view('groups', 'raw', groups_raw_map),
        db.define_view('users', 'by_id', users_by_id),
        ]
    db.sync_views(DB_NAME, views, False) # multiple packages do this, dont't remove missing

    # intial data?
    if not all_groups():
        doc = {
            "type": "groups",
            "groups": [
                "admin",
                "all",
                "admin_groups",
                "admin_users",
                "admin_environment",
                "admin_applications",
                "admin_stop_applications",
            ]
        }
        container.log.info('Creating groups definition')
        db.save_document(DB_NAME, doc)

    if not all_users():
        doc = {
            "name": "admin",
            "passwordhash": "d82494f05d6917ba02f7aaa29689ccb444bb73f20380876cb05d1f37537b7892", #adminadmin
            "allowed": True,
            "client_tokens": {},
            "type": "user",
            "id": "admin",
            "permissions": [
                "admin",
                "all"
            ]
        }
        container.log.info('Creating admin:adminadmin user')
        db.save_document(DB_NAME, doc)

except CouchError as ce:
    raise container.errors.FatalError(ce)