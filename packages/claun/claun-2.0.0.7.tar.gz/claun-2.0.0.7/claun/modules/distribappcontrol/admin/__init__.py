"""
Submodule: Admin
======================

Description
-----------
Module that supports CRUD for controllers and frameworks.

Endpoints
---------
All endpoints are restricted to groups admin and admin_distribappcontrol

  - /framework-configurations
    - GET: List all
    - POST: Create new
  - /framework-configurations/{framework-configuration-id}
    - GET: List info about given {framework-configuration-id}
    - PUT: Update configuration with given {framework-configuration-id}
    - DELETE: Delete configuration with given {framework-configuration-id}
  - /controller-configurations
    - GET: List all
    - POST: Create new
  - /controller-configurations/{controller-configuration-id}
    - GET: List info about given {controller-configuration-id}
    - PUT: Update configuration with given {controller-configuration-id}
    - DELETE: Delete configuration with given {controller-configuration-id}

"""
import json


from claun.core import container

from claun.modules.distribappcontrol.admin.help import __app__ as helpapp # plugin the help app
from claun.modules.distribappcontrol.admin import model
from claun.modules.users.auth import restrict


__docformat__ = 'restructuredtext en'

__uri__ = 'distribappcontrol/admin'
__author__ = 'chadijir'

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/framework-configurations/(.*)', 'FrameworkConfiguration',
           '/framework-configurations', 'FrameworkConfigurations',
           '/controller-configurations/(.*)', 'ControllerConfiguration',
           '/controller-configurations', 'ControllerConfigurations',
           '/help', helpapp,
           '/', 'Root',
           )
__app__ = container.web.application(mapping, locals())

class Root:
    """
    Provides basic information.
    """
    def GET(self):
        return container.output({
                          'framework-configurations': container.baseuri + __uri__ + '/framework-configurations',
                          'controller-configurations': container.baseuri + __uri__ + '/controller-configurations',
                          })

def _transform(list, notallowed=[]):
    """
    Deletes all keys from `notallowed` from all documents in `list`.

    :param list: List of CouchDB documents.
    :param notallowed: List of strings (keys) to be stripped from all docs in list. Default is empty list
    :return: List of doc.value values
    """
    ret = []
    for l in list:
        for n in notallowed:
            if n in l.value: del l.value[n]
        ret.append(l.value)

    return ret


class FrameworkConfigurations:
    """
    Framework configurations.
    """
    @restrict(['admin', 'admin_distribappcontrol'])
    def GET(self, user=None):
        """
        List all framework configurations except _id and _rev.
        """
        return container.output(_transform(model.all_framework_configurations(), ['_id', '_rev']))

    @restrict(['admin', 'admin_distribappcontrol'])
    def POST(self, user=None):
        """
        Create new framework configuration.

        In case of success, 200 OK with no body is returned.
        If a request is not valid, 400 Bad Request is returned.
        If a ModelError occurs, 500 Internal Error is returned.

        Required keys are parameters, framework_name and configuration_name.
        `parameters` key has to be a valid JSON document.
        Generated/appended fields are id (framework_name-configuration_name) and type (framework).
        """
        try:
            contents = container.input(container.web.data())
            for p in ['parameters', 'framework_name', 'configuration_name']:
                if p not in contents:
                    raise container.web.badrequest()

            contents['id'] = contents['framework_name'] + '-' + contents['configuration_name']
            contents['type'] = 'framework'
            contents['parameters'] = json.loads(contents['parameters'])

            result = model.create_framework_configuration(contents)
            if result is not None:
                return ''
            else:
                return result

        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()


class FrameworkConfiguration:
    @restrict(["admin", "admin_distribappcontrol"])
    def GET(self, id, user=None):
        """
        Get detail about framework configuration with `id`.

        If no such configurarion exists, 404 Not Found is returned.
        """
        config = model.get_framework_configuration(id)
        if config is None:
            return container.web.notfound()
        return container.output(_transform(config, ['_id', '_rev'])[0])

    @restrict(["admin", "admin_distribappcontrol"])
    def PUT(self, id, user=None):
        """
        Update framework configuration `id`.

        If id is empty, or does not exist, 404 Not Found is returned.
        In case of success, 200 OK with no body is returned.
        If a request is not valid, 400 Bad Request is returned.
        If a ModelError occurs, 500 Internal Error is returned.

        Required keys are parameters, framework_name and configuration_name.
        `parameters` key has to be a valid JSON document.
        Generated/appended fields are id (framework_name-configuration_name) and type (framework).
        ID will be always overwritten with a newly passed values.
        """
        if id == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such group.'}))
        config = model.get_framework_configuration(id) # default values
        if config is None:
            raise container.web.notfound()

        try:
            contents = container.input(container.web.data())
            for p in ['parameters', 'framework_name', 'configuration_name']:
                if p not in contents:
                    raise container.web.badrequest()

            contents['id'] = contents['framework_name'] + '-' + contents['configuration_name']
            contents['type'] = 'framework'
            contents['parameters'] = json.loads(contents['parameters'])

            result = model.update_framework_configuration(contents, config.id, config.value['_rev'])
            if result is not None:
                return ''
            else:
                return result

        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

    @restrict(["admin", "admin_distribappcontrol"])
    def DELETE(self, id, user=None):
        """
        Deletes one framework configuration with `id`.

        If no such configuration exists, a 404 Not Found is returned.
        In case of success, 202 OK with no message body is returned.
        """
        if id == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such configuration.'}))
        config = model.get_framework_configuration(id)
        if config is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such configuration.'}))
        try:
            result = model.delete_framework_configuration(config.value)
            if result:
                return ''
            else:
                return result
        except model.ModelError as me:
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))


class ControllerConfigurations:
    @restrict(['admin', 'admin_distribappcontrol'])
    def GET(self, user=None):
        """
        List all controller configurations except _id and _rev.
        """
        return container.output(_transform(model.all_controller_configurations(), ['_id', '_rev']))

    @restrict(['admin', 'admin_distribappcontrol'])
    def POST(self, user=None):
        """
        Create new controller configuration.

        In case of success, 200 OK with no body is returned.
        If a request is not valid, 400 Bad Request is returned.
        If a ModelError occurs, 500 Internal Error is returned.

        Required keys are parameters, controller_name and configuration_name.
        `parameters` key has to be a valid JSON document.
        Generated/appended fields are id (controller_name-configuration_name) and type (controller).
        """
        try:
            contents = container.input(container.web.data())
            for p in ['parameters', 'controller_name', 'configuration_name']:
                if p not in contents:
                    raise container.web.badrequest()

            contents['id'] = contents['controller_name'] + '-' + contents['configuration_name']
            contents['type'] = 'controller'
            contents['parameters'] = json.loads(contents['parameters'])

            result = model.create_controller_configuration(contents)
            if result is not None:
                return ''
            else:
                return result

        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()


class ControllerConfiguration:
    @restrict(["admin", "admin_distribappcontrol"])
    def GET(self, id, user=None):
        """
        Get detail about controller configuration with `id`.

        If no such configurarion exists, 404 Not Found is returned.
        """
        config = model.get_controller_configuration(id)
        if config is None:
            return container.web.notfound()
        return container.output(_transform(config, ['_id', '_rev'])[0])

    @restrict(["admin", "admin_distribappcontrol"])
    def PUT(self, id, user=None):
        """
        Update controller configuration `id`.

        If id is empty, or does not exist, 404 Not Found is returned.
        In case of success, 200 OK with no body is returned.
        If a request is not valid, 400 Bad Request is returned.
        If a ModelError occurs, 500 Internal Error is returned.

        Required keys are parameters, controller_name and configuration_name.
        `parameters` key has to be a valid JSON document.
        Generated/appended fields are id (controller_name-configuration_name) and type (framework).
        ID will be always overwritten with a newly passed values.
        """
        if id == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such group.'}))
        config = model.get_controller_configuration(id) # default values
        if config is None:
            raise container.web.notfound()

        try:
            contents = container.input(container.web.data())
            for p in ['parameters', 'controller_name', 'configuration_name']:
                if p not in contents:
                    raise container.web.badrequest()

            contents['id'] = contents['controller_name'] + '-' + contents['configuration_name']
            contents['type'] = 'controller'
            contents['parameters'] = json.loads(contents['parameters'])

            result = model.update_controller_configuration(contents, config.id, config.value['_rev'])
            if result is not None:
                return ''
            else:
                return result

        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

    @restrict(["admin", "admin_distribappcontrol"])
    def DELETE(self, id, user=None):
        """
        Deletes one controller configuration with `id`.

        If no such configuration exists, a 404 Not Found is returned.
        In case of success, 202 OK with no message body is returned.
        """
        if id == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such configuration.'}))
        config = model.get_controller_configuration(id)
        if config is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such configuration.'}))
        try:
            result = model.delete_controller_configuration(config.value)
            if result:
                return ''
            else:
                return result
        except model.ModelError as me:
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))
