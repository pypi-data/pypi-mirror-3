"""
Model layer for the Environment's admin module.

Uses CouchDB, can create database and synchronize views during the startup.

"""

from claun.core import container
from claun.modules.couchdb import client as db
from claun.modules.couchdb import CouchError
from claun.modules.environment.model import computer_by_id

__docformat__ = 'restructuredtext en'

DB_NAME = container.configuration['modules']['environment']['db_name']
"""Default db name. Database should be created if it does not exist."""

class ModelError(Exception): pass

####

def computers_by_id_map(doc):
    """
    Maps all documents with type 'computer'.

    The generated pairs are [id: {values}].
    """
    if doc['type'] == 'computer':
        yield(doc['id'], doc)

def computers_by_masterpriority_map(doc):
    """
    Gets all computers by masterpriority.

    The generated pairs are [doc.masterpriority: {doc}].
    """
    if doc['type'] == 'computer':
        yield(doc['masterpriority'], doc)


def masterpriority_map(doc):
    """
    Gets masterpriority for all computers by id.

    This is helpful when determnining for example the max master priority.

    The generated pairs are [doc.id: doc.masterpriority].
    """
    if doc['type'] == 'computer':
        yield(doc['id'], doc['masterpriority'])

def projections_map(doc):
    """
    Lists all available projections.

    If a parameter in a configuration document has a 'group' attribute with value
    'projection', it is considered as a projection.

    Generated pairs: [projection.name, projection.name]
    """
    if doc['type'] == 'configuration':
        for p in doc['parameters']:
            if 'group' in p and p['group'] == 'projection':
                yield(p['name'], p['name'])

def projections_reduce(keys, values):
    """
    Returns only values.
    """
    return values

def raw_parameters_map(doc):
    """
    Gets raw configuration document.

    Useful for parameter deletion/update.
    """
    if doc['type'] == 'configuration':
        yield(doc['_id'], doc)

# public API

def all_nodes():
    """
    Uses computers/by_id.
    :rtype: ViewResults or []
    """
    try:
        return db.view(DB_NAME, 'computers/by_id')
    except CouchError as ce:
        container.log.error(ce)
        return []

def get_node(id):
    """
    Uses computers/by_id.

    If no such computer is found, None is returned.
    """
    result = db.view(DB_NAME, 'computers/by_id', key=id)
    try:
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Node retrieval error: %s" % e)
        return None

def get_node_by_masterpriority(priority):
    """
    Uses computers/by_masterpriority.

    If no such computer is found, None is returned.
    """
    result = db.view(DB_NAME, 'computers/by_masterpriority', key=priority)
    try:
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Node retrieval error: %s" % e)
        return None


def create_node(node):
    """
    Creates new node.

    If a node with given id already exists, a ModelError is raised.

    :param node: Has to contain id key.
    """
    if 'id' not in node:
        raise ModelError('Missing ID')
    if computer_by_id(node['id']) is not None:
        raise ModelError('Node already exists')
    try:
        return db.save_document(DB_NAME, node)
    except CouchError as ce:
        container.log.error(ce)
        return None

def update_node(node, docid=None, revid=None):
    """Updates node.

    You can specify `_id` and `_rev` either directly in the dictionary
    or as separate arguments. If `_id` or `_rev` are not present in either form,
    a ModelError is raised.

    :param node: Dictionary with node
    :param docid: `_id` attribute, if `node` contains `_id` field, may be None
    :param revid: `_rev` attribute, if `node` contains `_rev` field, may be None
    :return: (id, rev) tuple of the newly saved document or None
    """
    if '_id' not in node:
        if docid is None:
            raise ModelError('No ID specified!')
        node['_id'] = docid

    if '_rev' not in node:
        if revid is None:
            raise ModelError('No revision specified!')
        node['_rev'] = revid
    try:
        return db.save_document(DB_NAME, node)
    except CouchError as ce:
        container.log.error(ce)
        return None

def delete_node(node):
    """
    Deletes node, `node` has to contain _id attribute.
    """
    if '_id' not in node:
        raise ModelError('Missing _ID')
    try:
        return db.delete_document(DB_NAME, node) is None
    except CouchError as ce:
        container.log.error(ce)
        return False

def next_master_priority():
    """
    Returns next free master priority. (max + 1).

    Uses computers/max_masterpriority. May return None.
    """
    try:
        result = db.view(DB_NAME, 'computers/max_masterpriority')
        if len(result) > 0:
            return 1 + result.__iter__().next().value['max']
    except CouchError as ce:
        container.log.error(ce)
    return None

def projections():
    """
    Returns all projections available in the system.

    Uses parameters/projections.
    May return [].
    """
    try:
        result = db.view(DB_NAME, 'parameters/projections')
        if len(result) > 0:
            return result.__iter__().next().value
    except CouchError as ce:
        container.log.error(ce)
    return []

def raw_parameters():
    """
    Returns raw parameters document or None
    """
    try:
        result = db.view(DB_NAME, 'parameters/raw')
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Parameters retrieval error: %s" % e)
        return None

###

def all_parameters():
    """
    Lists all parameters.

    Uses parameters/all.
    """
    try:
        return db.view(DB_NAME, 'parameters/all')
    except CouchError as ce:
        container.log.error(ce)
        return []

def get_parameter(paramname):
    """
    Uses parameters/all.

    If no such parameter is found, None is returned.
    """
    result = db.view(DB_NAME, 'parameters/all', key=paramname)
    try:
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Parameter retrieval error: %s" % e)
        return None

def create_parameter(param):
    """
    Creates new parameter.

    If a parameter with given id already exists or configuration document cannot be found, a ModelError is raised.

    :param param: Has to contain id key.
    :return: (id, rev) tuple of the newly saved document
    """
    if 'id' not in param:
        raise ModelError('Missing ID')
    parameters = raw_parameters()
    try:
        if parameters is not None and 'parameters' in parameters.value:
            for p in parameters.value['parameters']:
                if p['id'] == param['id']:
                    raise ModelError('Parameter already exists')
            parameters.value['parameters'].append(param)
            return db.save_document(DB_NAME, parameters.value)
    except CouchError as ce:
        container.log.error(ce)
        return None
    raise ModelError('Cannot find parameters definition.')

def update_parameter(oldid, param):
    """Updates param.

    Because param.id might have changed, an oldid is required to
    remove the old attribute would that be the case.

    May raise ModelError if a parameter with new paramid already exists or
    a configuration document can not be found.

    :param oldid: Old parameter id
    :param param: Dict with param, has to contain id
    :return: (id, rev) tuple of the newly saved document
    """
    parameters = raw_parameters()
    try:
        if parameters is not None and 'parameters' in parameters.value:
            for idx, p in enumerate(parameters.value['parameters']):
                if p['id'] == param['id'] and oldid != param['id']:
                    raise ModelError('Parameter already exists')
                if p['id'] == oldid:
                    parameters.value['parameters'][idx] = param
                    break
            return db.save_document(DB_NAME, parameters.value)
    except CouchError as ce:
        container.log.error(ce)
        return None
    raise ModelError('Cannot find parameters definition.')

def delete_parameter(paramid):
    """
    Deletes parameter wit paramid.

    May raise ModelError if a configuration document can not be found.
    :return: True if deleted, False otherwise
    """
    parameters = raw_parameters()
    try:
        if parameters is not None and 'parameters' in parameters.value:
            for idx, p in enumerate(parameters.value['parameters']):
                if p['id'] == paramid:
                    del parameters.value['parameters'][idx]
                    return db.save_document(DB_NAME, parameters.value) is not None
    except CouchError as ce:
        container.log.error(ce)
        return False
    raise ModelError('Cannot find parameters definition.')

# sync DB
try:
    db.touch_database(DB_NAME)
    views = [
        db.define_view('computers', 'by_masterpriority', computers_by_masterpriority_map),
        db.define_view('computers', 'by_id', computers_by_id_map),
        db.define_view('computers', 'max_masterpriority', masterpriority_map, '_stats'),
        db.define_view('parameters', 'projections', projections_map, projections_reduce),
        db.define_view('parameters', 'raw', raw_parameters_map),
    ]
    db.sync_views(DB_NAME, views, False)

    if not all_parameters():
        doc = {
            "type": "configuration",
            "parameters": []
        }
        container.log.info('Creating parameters definition')
        db.save_document(DB_NAME, doc)

except CouchError as ce:
    raise container.errors.FatalError(ce)

