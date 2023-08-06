"""
Model layer for the distribappcontrol module that uses the CouchDB as a storage.

It currently provides two design documents, controllers and frameworks.
In both design documents there are two views, one that returns all
configuration for certain controller/framework and one that returns
one particular configuration for certain controller/framework.

Module is capable of creating/syncing the database during startup.
"""
from claun.modules.couchdb import client as db
from claun.core import container

from claun.modules.couchdb import CouchError


__docformat__ = 'restructuredtext en'
__all__ = ['all_configs_by_controller', 'config_by_controller', 'all_configs_by_framework', 'config_by_framework']

DB_NAME = container.configuration['modules']['distribappcontrol']['db_name']
"""Default db name. Database should be created if it does not exist."""

####

def controllers_by_name_map(doc):
    """
    All controllers by name.

    {controller_name, document}
    """
    if doc['type'] == 'controller':
        yield(doc['controller_name'], doc)

def controllers_by_name_and_config_map(doc):
    """
    All configurations for one controller.

    {(controller_name, configuration_name), document}
    """
    if doc['type'] == 'controller':
        yield((doc['controller_name'], doc['configuration_name']), doc)

def frameworks_by_name_map(doc):
    """
    All frameworks by name.

    {framework_name, document}
    """
    if doc['type'] == 'framework':
        yield(doc['framework_name'], doc)

def frameworks_by_name_and_config_map(doc):
    """
    All configurations for one framework.

    {(framework_name, configuration_name), document}
    """
    if doc['type'] == 'framework':
        yield((doc['framework_name'], doc['configuration_name']), doc)

# sync DB
try:
    db.touch_database(DB_NAME)
    views = [
            db.define_view('controllers', 'by_name', controllers_by_name_map),
            db.define_view('controllers', 'by_name_and_config', controllers_by_name_and_config_map),
            db.define_view('frameworks', 'by_name', frameworks_by_name_map),
            db.define_view('frameworks', 'by_name_and_config', frameworks_by_name_and_config_map),
            ]
    db.sync_views(DB_NAME, views, False)
except CouchError as ce:
    raise container.errors.FatalError(ce)

# public API

def all_configs_by_controller(controllername):
    """
    Returns all configurations available for controller `controllername` or empty list.
    """
    try:
        if controllername is None:
            return db.view(DB_NAME, 'controllers/by_name')
        return db.view(DB_NAME, 'controllers/by_name', key=controllername)
    except CouchError as ce:
        container.log.error(ce)
        return []

def config_by_controller(controllername, configname):
    """
    Returns configuration `configname` for controller `controllername`.

    None may be returned if no such configuration exists.
    """
    try:
        result = db.view(DB_NAME, 'controllers/by_name_and_config', key=(controllername, configname))
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Controller config retrieval error: %s" % e)
        return None

def all_configs_by_framework(frameworkname):
    """
    Returns all configurations available for framework `frameworkname` or empty list.
    """
    try:
        if frameworkname is None :
            return db.view(DB_NAME, 'frameworks/by_name')
        return db.view(DB_NAME, 'frameworks/by_name', key=frameworkname)
    except CouchError as ce:
        container.log.error(ce)
        return []


def config_by_framework(frameworkname, configname):
    """
    Returns configuration `configname` for framework `frameworkname`.

    None may be returned if no such configuration exists.
    """
    try:
        result = db.view(DB_NAME, 'frameworks/by_name_and_config', key=(frameworkname, configname))
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Framework config retrieval error: %s" % e)
        return None
