"""
Model layer for the Applications module.

The model uses CouchDB as a storage. The application parameters can
be changed, however the changed values are not stored back
to the database, but in the personalized in-memory cache.

During startup, a database may be created and filled with views.
If views in the database are out of date, they are updated.

Every time, when querying personalized parameters, database is contacted
for current results. If the parameter was edited before by the user,
**only the edited value** is overwritten. If the parameter has
user_editable attribute set to false, its value can not be overwritten.
"""
from claun.modules.couchdb import client as db
from claun.core import container
from claun.modules.couchdb import CouchError


__docformat__ = 'restructuredtext en'
__all__ = ['all_applications', 'application_by_id', 'parameters', 'parameter_by_name', 'save_parameter', 'get_attachment']

DB_NAME = container.configuration['modules']['applications']['db_name']
"""Default db name. Database should be created if it does not exist."""

####

def visible_applications_by_id_map(doc):
    """
    All visible applications by id, gets rid of _rev, _id, visible and type attributes.

    Resulting pairs: [id: {values}]
    """
    if doc['type'] == 'application' and doc['visible']:
        notallowed = ('_rev', '_id', 'type', 'visible')
        filtered = dict((k, doc[k]) for k in doc if k not in notallowed)
        yield(filtered['id'], filtered)

def parameters_by_application_id_map(doc):
    """
    All parameters for one application.

    Resulting pair: [app.id: {app.parameters}]
    """
    if doc['type'] == 'application':
        if 'parameters' not in doc:
            yield(doc['id'], [])
        else:
            yield(doc['id'], doc['parameters'])

def parameters_by_app_and_id_map(doc):
    """
    One parameter for given app.

    Sets parameter's id from its name. Key is a tuple consisting of application id and parameter id.

    Resulting pair: [(app.id, parameter.id), parameter]
    """
    if doc['type'] == 'application' and 'parameters' in doc:
        for p in doc['parameters']:
            p['id'] = p['name']
            yield((doc['id'], p['id']), p)

# sync DB
try:
    db.touch_database(DB_NAME)
    views = [
            db.define_view('applications', 'visible_by_id', visible_applications_by_id_map),
            db.define_view('parameters', 'by_application_id', parameters_by_application_id_map),
            db.define_view('parameters', 'by_app_and_id', parameters_by_app_and_id_map),
            ]
    db.sync_views(DB_NAME, views, False) # multiple packages do this, don't remove missing
except CouchError as ce:
    raise container.errors.FatalError(ce)

# user's cache - enables per client changes
class UserCache:
    """
    Simple in-memory cache storing user edited parameters for every application.

    Derived from claun.modules.environment.model.UserCache.

    Uses dictionary as an underlying implementation.
    """
    def __init__(self):
        """Initializes the underlying dictionary."""
        self.hash = {}

    def set(self, user, appid, parameter):
        """
        Adds new parameter to the application in the user's cache. If a user does not have a cache, it is created.
        If the cache for given appid does not exist, it is created.

        Textual true|false values are transformed into True and False symbols in the parameter dictionary.

        :param user: dictionary, has to have '_id' key. Ideally, this is the raw record from couchdb.
        :param appid: Some unique application id
        :param parameter: dictionary with the parameter itself, has to have 'id' key.
        """
        if user['_id'] not in self.hash:
            self.hash[user['_id']] = {}

        if appid not in self.hash[user['_id']]:
            self.hash[user['_id']][appid] = {}

        for k, v in parameter.iteritems():
            if v == u'false':
                parameter[k] = False
            elif v == u'true':
                parameter[k] = True

        self.hash[user['_id']][appid][parameter['id']] = parameter
        return True


    def get_all(self, user, appid):
        """
        Returns all parameters saved for given user for given appid.

        If no appid cache or no user suits the parameters, None is returned.

        :param user: dictionary, has to have '_id' key. May be None, then None is returned.
        :param appid: Application id provided when setting the first parameter
        """
        if user is not None and user['_id'] in self.hash and appid in self.hash[user['_id']]:
            return self.hash[user['_id']][appid]
        return None

    def get(self, user, appid, parameter):
        """
        Returns specified parameter from specified application in user's cache.

        User and appid are passed to get_all method and then the parameter is looked up.
        If no such parameter exists in cache, None is returned.

        :param parameter: dictionary, has to have 'id' key.
        """
        conf = self.get_all(user, appid)
        if conf is None or parameter['id'] not in conf:
            return None
        else:
            return conf[parameter['id']]

# instantiate cache
cache = UserCache()

# public API
def all_applications():
    """
    All applications. Uses applications/visible_by_id view.

    :return: ViewResults or []
    """
    try:
        return db.view(DB_NAME, 'applications/visible_by_id')
    except CouchError as ce:
        container.log.error(ce)
        return []

def application_by_id(appid):
    """
    Application with id `appid`. Uses application/visible_by_id view.

    If no such application exists, None is returned.
    """
    try:
        result = db.view(DB_NAME, 'applications/visible_by_id', key=appid)
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.error("Application retrieval error: %s" % e)
        return None

def parameters(user, appid):
    """
    All parameters for application `appid`. Uses parameter/by_application_id view.

    All curent data from database is returned except for parameters that can be user_editable
    and have its edited value in the user cache (They are overwritten with the cached value).

    :return: [] or None if no parameters are found for that application
    """
    try:
        result = db.view(DB_NAME, 'parameters/by_application_id', key=appid)
        if len(result) > 0:
            result = result.__iter__().next().value
            cached = cache.get_all(user, appid)
            if cached is None:
                return result

            ret = []
            for k in result:
                if k['id'] in cached and k['user_editable']: # overwrite only if edited and editable
                    k['value'] = cached[k['id']]['value'] if 'value' in cached[k['id']] else k['default']
                ret.append(k)
            return ret
        return None
    except Exception as e:
        container.log.error("Configuration retrieval error: %s" % e)
        return []

def parameter_by_name(user, appid, paramid):
    """
    One parameter with `paramid` for application `appid`.

    Current data is obtained from DB using the parameters/by_app_and_id view and
    if edited before, the current value is overwritten with the cached value.

    May return None if some Exception occurs during the process.
    """
    try:
        result = db.view(DB_NAME, 'parameters/by_app_and_id', key=(appid, paramid))
        if len(result) > 0:
            param = result.__iter__().next()
            cached = cache.get(user, appid, paramid)
            if cached is not None and param['user_editable']:
                param['value'] = cached['value'] if 'value' in cached else param['default']
            return param
    except Exception as e:
        container.log.error("Parameter retrieval error: %s" % e)
        return None

def save_parameter(user, appid, data):
    """
    Saves parameter's new value to the `user`'s `appid` cache.

    If parameter does not exist, returns False.
    :param data: Dictionary with parameter values, has to contain 'id' key.
    """
    try:
        exists = db.view(DB_NAME, 'parameters/by_app_and_id', key=(appid, data['id']))
        if len(exists) < 1:
            return False
        return cache.set(user, appid, data)
    except CouchError as ce:
        container.log.error(ce)
        return False

def get_attachment(docid, name):
    """
    Returns the attachment of `name` for the given `docid`.

    Uses couchdb.CouchWrapper.get_attachment method. See that for more details.

    :param docid: CouchDB ID of the application document that the attachment is attached to.
    :return: File like object or None
    """
    try:
        return db.get_attachment(DB_NAME, docid, name)
    except CouchError as ce:
        container.log.error(ce)
        return None
