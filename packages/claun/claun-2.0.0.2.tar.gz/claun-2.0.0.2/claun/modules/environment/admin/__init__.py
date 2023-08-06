"""
Submodule: Admin
================

Description
-----------
Administration for the environment module, it can manage nodes and environment parameters.

Endpoints
---------
All endpoints are restricted to admin and admin_environment groups.

  - /nodes
    - GET: List all
    - POST: Create new node
  - /nodes/{node-id}
    - GET: List info about a node-id
    - PUT: Update a node-id
    - DELETE: Delete a node-id
  - /parameters
    - GET: List all parameters
    - POST: Create new parameter
  - /parameters/{parameter-id}
    - GET: List info about a parameter-id
    - PUT: Update a parameter-id
    - DELETE: Delete a parameter-id
  - /additional-data
    - GET: List all possible data-id keys (type, projections)
  - /additional-data/{data-id}
    - GET: List of additional data-id

Implementation details
----------------------
"""



from claun.core import container

from claun.modules.environment.admin import model

from claun.modules.users import restrict

__uri__ = 'environment/admin'
__author__ = 'chadijir'

uris = {}

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/additional-data/(.*)', 'AdditionalData',
           '/additional-data', 'AdditionalData',
           '/nodes/(.*)', 'Node',
           '/nodes', 'Nodes',
           '/parameters/(.*)', 'Parameter',
           '/parameters', 'Parameters',
           '/', 'Root',
           )

__app__ = container.web.application(mapping, locals())

# Endpoints

class Root:
    @restrict(['admin', 'admin_environment'])
    def GET(self):
        """
        List of child endpoints, should not be accessed at all.
        """
        return container.output({
                          'nodes': container.baseuri + __uri__ + '/nodes',
                          'additional-data': container.baseuri + __uri__ + '/additional-data'})

def _transform(nodes, notallowed=[]):
    """
    Removes keys from `notallowed` from all dictionaries in `nodes`.
    """
    if isinstance(nodes, basestring):
        nodes = [nodes]
    for node in nodes:
        for n in notallowed:
            del node[n]
    return nodes

class Nodes:
    """
    All nodes
    """
    @restrict(['admin', 'admin_environment'])
    def GET(self, user=None):
        """
        Lists all nodes without _id and _rev attribute.
        """
        return container.output(_transform([node.value for node in model.all_nodes()], ['_id', '_rev']))


    @restrict(['admin', 'admin_environment'])
    def POST(self, user=None):
        """
        Create a new node.

        Mandatory fields are hostname, ip, port, connected, fqdn and platforms.
        'platforms' may be empty, but has to be present.
        If 'projections' field is not present, an empty dictionary is created.
        Generated fields are: id (hostname, but lowercase), type (computer), masterpriority (Max + 1).

        If the message is not valid data, a 400 Bad Request is returned.
        If a ModelError occurs, a 500 Internal Server Error is returned.
        If some mandatory field is missing, a 400 Bad Request is returned.
        """
        try:
            contents = container.input(container.web.data())

            # necessary attrs
            for attr in ['hostname', 'ip', 'port', 'connected', 'fqdn', 'platforms']:
                if attr not in contents: raise container.web.badrequest()

            # optional attrs
            if 'projections' not in contents:
                contents['projections'] = {}

            # generated attrs
            priority = model.next_master_priority()
            contents.update({'id': contents['hostname'].lower().replace(' ', '-'), 'type': 'computer', 'masterpriority': 1 if priority is None else priority})
            result = model.create_node(contents)
            if result is not None:
                return container.output(contents)
            else:
                return container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save node.'}))
        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

class Node:
    @restrict(['admin', 'admin_environment'])
    def GET(self, nodeid, user=None):
        """
        Get info about one node.

        If node is not found, a 404 is returned.
        """
        node = model.get_node(nodeid)
        if node is None:
            raise container.web.notfound()
        return container.output(_transform(node.value))

    @restrict(['admin', 'admin_environment'])
    def PUT(self, nodeid, user=None):
        """
        Updates node with nodeid.

        Mandatory fields are hostname, ip, port, connected, fqdn and platforms.
        'platforms' may be empty, but has to be present.
        If 'projections' field is not present, an empty dictionary is created. (This means that projections are not copied from the old version)
        If 'masterpriority' is missing, it is copied from the old value.
        If 'masterpriority' differs from the old value, a node (if exists) with the new priority gets the old priority, so priority uniqueness is ensured.
        Generated fields are: id (hostname, but lowercase), type (computer).

        If a nodeid does not exist, a 404 Not Found is returned.
        If the message is not valid data, a 400 Bad Request is returned.
        If a ModelError occurs, a 500 Internal Server Error is returned.
        If some mandatory field is missing, a 400 Bad Request is returned.
        """
        if nodeid == '': raise container.web.notfound()
        node = model.get_node(nodeid)
        if node is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such node.'}))

        try:
            contents = container.input(container.web.data())

            # necessary attrs
            for attr in ['hostname', 'ip', 'port', 'connected', 'fqdn', 'platforms']:
                if attr not in contents: raise container.web.badrequest()

            # optional attrs
            if 'projections' not in contents:
                contents['projections'] = {}
            if 'masterpriority' not in contents:
                contents['masterpriority'] = node.value['masterpriority']

            if contents['masterpriority'] != node.value['masterpriority']:
                container.log.debug('Switching priorities')
                switch = model.get_node_by_masterpriority(contents['masterpriority'])
                if switch is not None:
                    switch.value['masterpriority'] = node.value['masterpriority']
                    model.update_node(switch.value)


            # generated attrs
            contents.update({'id': contents['hostname'].lower().replace(' ', '-'), 'type': 'computer'})

            result = model.update_node(contents, node.id, node.value['_rev'])
            if result is not None:
                return container.output(contents)
            else:
                return container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save node.'}))
        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

    @restrict(['admin', 'admin_environment'])
    def DELETE(self, nodeid, user=None):
        """
        Deletes a `nodeid`.

        If no such node exist, a 404 Not Found is returned.
        If a problem occurs, a 500 Internal Server Error is returned.
        """
        if nodeid == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such node.'}))
        node = model.get_node(nodeid)
        if node is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such node.'}))
        try:
            result = model.delete_node(node.value)
            if result:
                return ''
            else:
                return result
            pass
        except model.ModelError as me:
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))

class Parameters:
    @restrict(['admin', 'admin_environment'])
    def GET(self, user=None):
        """
        Lists all parameters.
        """
        return container.output([node.value for node in model.all_parameters()])


    @restrict(['admin', 'admin_environment'])
    def POST(self, user=None):
        """
        Create a new parameter.

        Mandatory fields are name, human_name, type, default, user_editable.
        If type is dropdown, a 'values' attribute is required.
        If type is slider, a 'max', 'min' attributes are required and if the default value is within these boundaries is checked.

        Generated attributes are empty 'help' and 'id' (name in lowercase, spaces replaced with -)

        If the message is not valid data, a 400 Bad Request is returned.
        If some fields are missing, a 400 Bad Request is returned.
        If a ModelError occurs, a 500 Internal Server Error is returned.
        If some mandatory field is missing, a 400 Bad Request is returned.
        """
        try:
            contents = container.input(container.web.data())
            # necessary attrs
            for attr in ['name', 'human_name', 'type', 'user_editable', 'default']:
                if attr not in contents: raise container.web.badrequest()

            # type dependent attrs
            if contents['type'] == 'dropdown':
                for attr in ['values']:
                    if attr not in contents: raise container.web.badrequest()
            elif contents['type'] == 'slider':
                for attr in ['min', 'max']:
                    if attr not in contents: raise container.web.badrequest()
                if contents['default'] < contents['min'] or contents['default'] > contents['max']:
                    raise container.web.badrequest()

            # optional attrs
            if 'help' not in contents:
                contents['help'] = ''

            # generated attrs
            contents.update({'id': contents['name'].lower().replace(' ', '-')})

            result = model.create_parameter(contents)
            if result is not None:
                return container.output(contents)
            else:
                return container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save parameter.'}))
        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

class Parameter:
    @restrict(['admin', 'admin_environment'])
    def GET(self, paramid, user=None):
        """
        Get info about one parameter.

        If node is not found, a 404 is returned.
        """
        param = model.get_parameter(paramid)
        if param is None:
            raise container.web.notfound()
        return container.output(param.value)

    @restrict(['admin', 'admin_environment'])
    def PUT(self, paramid, user=None):
        """
        Update a parameter with `paramid`.

        Mandatory fields are name, human_name, type, default, user_editable.
        If type is dropdown, a 'values' attribute is required.
        If type is slider, a 'max', 'min' attributes are required and if the default value is within these boundaries is checked.

        Generated attributes are empty 'help' and 'id' (name in lowercase, spaces replaced with -)

        If the message is not valid data, a 400 Bad Request is returned.
        If some fields are missing, a 400 Bad Request is returned.
        If a ModelError occurs, a 500 Internal Server Error is returned.
        If some mandatory field is missing, a 400 Bad Request is returned.
        """
        if paramid == '': raise container.web.notfound()
        param = model.get_parameter(paramid)
        if param is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such parameter.'}))

        try:
            contents = container.input(container.web.data())

            # necessary attrs
            for attr in ['name', 'human_name', 'type', 'user_editable', 'default']:
                if attr not in contents: raise container.web.badrequest()

            # type dependent attrs
            if contents['type'] == 'dropdown':
                for attr in ['values']:
                    if attr not in contents: raise container.web.badrequest()
            elif contents['type'] == 'slider':
                for attr in ['min', 'max']:
                    if attr not in contents: raise container.web.badrequest()
                if contents['default'] < contents['min'] or contents['default'] > contents['max']:
                    raise container.web.badrequest()

            # optional attrs
            if 'help' not in contents:
                contents['help'] = ''

            # generated attrs
            contents.update({'id': contents['name'].lower().replace(' ', '-')})

            result = model.update_parameter(paramid, contents)
            if result is not None:
                return container.output(contents)
            else:
                return container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save parameter.'}))
        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

    @restrict(['admin', 'admin_environment'])
    def DELETE(self, paramid, user=None):
        """
        Deletes a parameter with paramid.

        If no such parameter exists, a 404 Not Found is returned.
        If soem problem occurs, a 500 Internal Error is returned.
        """
        if paramid == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such parameter.'}))
        param = model.get_parameter(paramid)
        if param is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such parameter.'}))
        try:
            result = model.delete_parameter(paramid)
            if result:
                return ''
            else:
                return result
            pass
        except model.ModelError as me:
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))


class AdditionalData:
    """
    Data needed when creating a node or parameter.
    """
    @restrict(['admin', 'admin_environment'])
    def GET(self, name=None, user=None):
        """
        Returns list of all available additional data or lists the appropriate possibilities.

        May return 400 Bad Request if an invalid type is requested.

        :param name: One of the following: platforms, type, processing_type, frameworks, controllers.
        """
        if name is None or name == '':
            return container.output({
                              'type': container.baseuri + __uri__ + '/additional-data/type',
                              'projections': container.baseuri + __uri__ + '/additional-data/projections',
                              })

        else:
            if name not in ['type', 'projections']:
                raise container.web.badrequest()
            process = {
                    'type': self._type(),
                    'projections': self._projections()
            }
            return container.output(process[name])

    def _type(self):
        """
        Handles `type` type.

        Type tells the rendering engine how to present the application's parameter to the user.
        See applications module for more documentation.
        """
        return ['dropdown', 'boolean', 'slider']

    def _projections(self):
        """
        List of all available controller names and their available configurations.

        Uses model from distribappcontrol module.
        """
        return model.projections()
