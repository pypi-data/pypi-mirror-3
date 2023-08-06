"""
Model layer for the Environment module.

The model layer uses CouchDB as a storage for initial data.
It is allowed to change configuration parameters, however they are not
saved back to the database, but in-memory personalized cache is kept.

During startup, a database may be created and filled with views.
If views in the database are out of date, they are updated.

Every time, when querying personalized parameters, database is contacted
for current results. If the parameter was edited before by the user,
**only the edited value** is overwritten. If the parameter has
user_editable attribute set to false, its value can not be overwritten.
"""

from claun.core import container

from claun.modules.couchdb import client as db
from claun.modules.couchdb import CouchError


__docformat__ = 'restructuredtext en'
__all__ = ['computer_by_id', 'all_computers', 'configuration', 'parameter', 'save_parameter']

DB_NAME = container.configuration['modules']['environment']['db_name']
"""Default db name. Database should be created if it does not exist."""

####

def connected_computers_by_id_map(doc):
    """
    Maps all documents with type 'computer' that have `connected` key set to true.

    The generated pairs are [id: {values}].
    """
    if doc['type'] == 'computer':
        if doc['connected']:
            yield(doc['id'], doc)

def configuration_map(doc):
    """
    Maps configuration documents into a list of single parameters.

    If not present, adds id parameter that is generated from name (lowercase, spaces replaced with dashes).
    Generated pairs are [id: {values}].
    """
    if doc['type'] == 'configuration':
        for p in doc['parameters']:
            if 'id' not in p:
                p['id'] = container.webalize_string(p['name'])
            yield(p['id'], p)

def platforms_map(doc):
    """
    Platforms for all nodes.

    [id: platform]
    """
    if doc['type'] == 'computer':
        for platform in doc['platforms']:
            yield(doc['id'], platform)

def platforms_reduce(key, values):
    """
    Returns list of platforms in values.
    """
    return dict([(v, v) for v in values]).keys()


# sync DB
try:
    db.touch_database(DB_NAME)
    views = [
            db.define_view('computers', 'connected_by_id', connected_computers_by_id_map),
            db.define_view('computers', 'platforms', platforms_map, platforms_reduce, 'python', None, group=True),
            db.define_view('parameters', 'all', configuration_map),
            ]
    db.sync_views(DB_NAME, views, False)
except CouchError as ce:
    raise container.errors.FatalError(ce)

# user's cache - enables per client changes
class UserCache:
    """
    Simple in-memory cache storing user edited parameters.

    Uses dictionary as an underlying implementation.
    """
    def __init__(self):
        """Initializes the underlying dictionary."""
        self.hash = {}

    def set(self, user, parameter):
        """
        Adds new parameter to the user's cache. If a user does not have a cache, it is created.

        Textual true|false values are transformed into True and False symbols in the parameter dictionary.

        :param user: dictionary, has to have '_id' key. Ideally, this is the raw record from couchdb.
        :param parameter: dictionary with the parameter itself, has to have 'id' key.
        """
        if user['_id'] not in self.hash:
            self.hash[user['_id']] = {}

        for k, v in parameter.iteritems():
            if v == u'false':
                parameter[k] = False
            elif v == u'true':
                parameter[k] = True

        self.hash[user['_id']][parameter['id']] = parameter
        return True


    def get_all(self, user):
        """
        Returns all parameters saved for given user.

        :param user: dictionary, has to have '_id' key. May be None, then None is returned.
        """
        if user is not None and user['_id'] in self.hash:
            return self.hash[user['_id']]
        return None

    def get(self, user, parameter):
        """
        Returns specified parameter from specified user's cache.

        User is passed to get_all method and then the parameter is looked up.
        If no such parameter exists in cache, None is returned.

        :param parameter: dictionary, has to have 'id' key.
        """
        conf = self.get_all(user)
        if conf is None or parameter['id'] not in conf:
            return None
        else:
            return conf[parameter['id']]

# instantiate cache
cache = UserCache()


# public API
def all_computers():
    """
    Returns contents of the computers/connected_by_id couchdb view.
    :rtype: ViewResults or []
    """
    try:
        return db.view(DB_NAME, 'computers/connected_by_id')
    except CouchError as ce:
        container.log.error(ce)
        return []

def computer_by_id(name):
    """
    Returns one computer with name.

    :param name: name of the computer
    :return: None, or computer's record from computers/connected_by_id view.
    """
    try:
        result = db.view(DB_NAME, 'computers/connected_by_id', key=name)
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Computer retrieval error: %s" % e)
        return None

# methods using cache
def configuration(user):
    """
    Get all available parameters and if possible, personalized values for parameters.

    All curent data from database is returned except for parameters that can be user_editable
    and have its edited value in the user cache  (They are overwritten with the cached value).
    :rtype: []
    """
    try:
        result = db.view(DB_NAME, 'parameters/all')
        if len(result) > 0:
            cached = cache.get_all(user)
            if cached is None:
                return [k.value for k in result]

            ret = []
            for k in result:
                if k.value['id'] in cached and k.value['user_editable']: # overwrite only if edited and editable
                    k.value['value'] = cached[k.value['id']]['value'] if 'value' in cached[k.value['id']] else k.value['default']
                ret.append(k.value)
            return ret
    except Exception as e:
        container.log.debug("Configuration retrieval error: %s" % e)
        return []

def parameter(user, name):
    """
    Returns one parameter.

    If the parameter does not exist in database, None is returned.
    If the parameter exists and was edited before, a cached value is set.
    Uses UserCache.get method.
    :param name: string
    """
    result = db.view(DB_NAME, 'parameters/all', key=name)
    try:
        if len(result) > 0:
            param = result.__iter__().next()
            cached = cache.get(user, name)
            if cached is not None and param['user_editable']:
                param['value'] = cached['value'] if 'value' in cached else param['default']
            return param
    except Exception as e:
        container.log.debug("Parameter retrieval error: %s" % e)
        return None

def save_parameter(user, parameter):
    """
    Saves parameter to a given user cache if the parameter exists.

    If parameter does not exist, returns False.
    Uses UserCache.set method, for param details see that method.
    :param parameter: dictionary, has to have 'id' key
    :rtype: boolean
    """
    try:
        exists = db.view(DB_NAME, 'parameters/all', key=parameter['id'])
        if len(exists) < 1:
            return False
        return cache.set(user, parameter)
    except CouchError as ce:
        container.log.error(ce)
        return False

def platforms():
    """Returns all platforms available on all machines.

    Uses computers/platforms view.
    :rtype: []
    """
    try:
        ps = db.view(DB_NAME, 'computers/platforms')
        if len(ps) > 0:
            return ps.__iter__().next().value
        return []
    except CouchError as ce:
        container.log.error(ce)
        return []
