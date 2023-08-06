"""
Model layer for the distribappcontrol's admin submodule that uses the CouchDB as a storage.

Module is capable of creating/syncing the database during startup.
"""

from claun.modules.couchdb import client as db
from claun.core import container

from claun.modules.couchdb import CouchError


__docformat__ = 'restructuredtext en'

DB_NAME = container.configuration['modules']['distribappcontrol']['db_name']
"""Default db name. Database should be created if it does not exist."""

class ModelError(Exception): pass

####

def controllers_by_id_map(doc):
    """
    All controllers by id.

    ID is constructed as a controller_name-configuration_name string.

    {controller_id, document}
    """
    if doc['type'] == 'controller':
        if 'id' not in doc:
            doc['id'] = doc['controller_name'] + '-' + doc['configuration_name']

        yield(doc['id'], doc)

def frameworks_by_id_map(doc):
    """
    All frameworks.

    ID is constructed as a framework_name-configuration_name string.

    {framework_id, document}
    """
    if doc['type'] == 'framework':
        if 'id' not in doc:
            doc['id'] = doc['framework_name'] + '-' + doc['configuration_name']
        yield(doc['id'], doc)

# sync DB
try:
    db.touch_database(DB_NAME)
    views = [
            db.define_view('controllers', 'by_id', controllers_by_id_map),
            db.define_view('frameworks', 'by_id', frameworks_by_id_map),
            ]
    db.sync_views(DB_NAME, views, False)
except CouchError as ce:
    raise container.errors.FatalError(ce)

# public API

def all_framework_configurations():
    """
    All framework configurations or empty list.

    Uses frameworks/by_id.
    :rtype: ResultsView or []
    """
    try:
        return db.view(DB_NAME, 'frameworks/by_id')
    except CouchError as ce:
        container.log.error(ce)
        return []

def get_framework_configuration(id):
    """
    One framework configuration.

    Uses frameworks/by_id. If no config is found, returns None.
    :param id: Framework's configuration id
    :rtype: Document or None
    """
    try:
        result = db.view(DB_NAME, 'frameworks/by_id', key=id)
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Framework configuration retrieval error: %s" % e)
        return None

def create_framework_configuration(framework_configuration):
    """
    Creates framework_configuration.

    May raise ModelError if a configuration with this ID already exist.

    :param framework_configuration: Dictionary that has to contain an id key.
    :return: (id, rev) tuple of the newly saved document or None
    """
    try:
        if 'id' not in framework_configuration:
            raise ModelError('Missing ID')
        if get_framework_configuration(framework_configuration['id']) is not None:
            raise ModelError('Framework configuration already exists.')
        return db.save_document(DB_NAME, framework_configuration)
    except CouchError as ce:
        container.log.error(ce)
        return None

def delete_framework_configuration(framework_configuration):
    """
    Deletes framework_configuration.

    May raise ModelError.

    :param framework_configuration: Doc or dict that has to have a _id key.
    :rtype: boolean
    """
    try:
        if '_id' not in framework_configuration:
            raise ModelError('Missing _ID')
        return db.delete_document(DB_NAME, framework_configuration) is None
    except CouchError as ce:
        container.log.error(ce)
        return False


def update_framework_configuration(framework_configuration, docid=None, revid=None):
    """
    Updates framework configuration.

    You can specify `_id` and `_rev` either directly in the dictionary
    or as separate arguments. If `_id` or `_rev` are not present in either form,
    a ModelError is raised.

    :param framework_configuration: Dictionary with framework configuration
    :param docid: `_id` attribute, if `framework_configuration` contains `_id` field, may be None
    :param revid: `_rev` attribute, if `framework_configuration` contains `_rev` field, may be None
    :return: (id, rev) tuple of the newly saved document or None
    """
    if '_id' not in framework_configuration:
        if docid is None:
            raise ModelError('No ID specified!')
        framework_configuration['_id'] = docid

    if '_rev' not in framework_configuration:
        if revid is None:
            raise ModelError('No revision specified!')
        framework_configuration['_rev'] = revid
    try:
        return db.save_document(DB_NAME, framework_configuration)
    except CouchError as ce:
        container.log.error(ce)
        return None


def all_controller_configurations():
    """
    All controller configurations.

    Uses controllers/by_id.
    :rtype: ResultsView or []
    """
    try:
        return db.view(DB_NAME, 'controllers/by_id')
    except CouchError as ce:
        container.log.error(ce)
        return []


def get_controller_configuration(id):
    """
    One controller configuration.

    Uses controllers/by_id. If no config is found, returns None.
    :param id: Framework's configuration id
    """
    try:
        result = db.view(DB_NAME, 'controllers/by_id', key=id)
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Controller configuration retrieval error: %s" % e)
        return None

def create_controller_configuration(controller_configuration):
    """
    Creates controller_configuration.

    May raise ModelError if a configuration with this ID already exist.

    :param controller_configuration: Dictionary that has to contain an id key.
    :return: (id, rev) tuple of the newly saved document or None
    """
    if 'id' not in controller_configuration:
        raise ModelError('Missing ID')
    if get_controller_configuration(controller_configuration['id']) is not None:
        raise ModelError('Controller configuration already exists.')
    try:
        return db.save_document(DB_NAME, controller_configuration)
    except CouchError as ce:
        container.log.error(ce)
        return None

def delete_controller_configuration(controller_configuration):
    """
    Deletes controller_configuration.

    May raise ModelError.

    :param controller_configuration: Doc or dict that has to have a _id key.
    :rtype: boolean
    """
    if '_id' not in controller_configuration:
        raise ModelError('Missing _ID')
    try:
        return db.delete_document(DB_NAME, controller_configuration) is None
    except CouchError as ce:
        container.log.error(ce)
        return False

def update_controller_configuration(controller_configuration, docid=None, revid=None):
    """
    Updates controller configuration.

    You can specify `_id` and `_rev` either directly in the dictionary
    or as separate arguments. If `_id` or `_rev` are not present in either form,
    a ModelError is raised.

    :param controller_configuration: Dictionary with controller configuration
    :param docid: `_id` attribute, if `controller_configuration` contains `_id` field, may be None
    :param revid: `_rev` attribute, if `controller_configuration` contains `_rev` field, may be None
    :return: (id, rev) tuple of the newly saved document
    """
    if '_id' not in controller_configuration:
        if docid is None:
            raise ModelError('No ID specified!')
        controller_configuration['_id'] = docid

    if '_rev' not in controller_configuration:
        if revid is None:
            raise ModelError('No revision specified!')
        controller_configuration['_rev'] = revid
    try:
        return db.save_document(DB_NAME, controller_configuration)
    except CouchError as ce:
        container.log.error(ce)
        return None
