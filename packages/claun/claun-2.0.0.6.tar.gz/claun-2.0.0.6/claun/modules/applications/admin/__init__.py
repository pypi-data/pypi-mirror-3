"""
Submodule: Admin
================

Description
-----------
Module for applications administration.

Module supports whole application CRUD including image management.

Endpoints
---------
All endpoints are restricted for groups admin and admin_applications. For more information, see the class documentation.

  - /list - All applications
    - GET: list all applications
    - POST: Create applications
  - /list/{application-id} - Application's detail
    - GET: List info about the application
    - PUT: Update application
    - DELETE: Delete application
  - /additional-data - Data necessary for creating an application, currently (available data-key below):
    - platforms, frameworks, controllers, type and processing_type (the last two are used when defining parameters)
  - /additional-data/{data-key}
    - GET
  - /list/{application-id}/images - Lists all images urls for application-id
    - GET
    - POST
  - /list/{application-id}/images/{image-id}
    - GET
    - PUT
    - DELETE

The environmnent and distribappcontrol dependencies are here to provide data about
available platforms, controllers and frameworks.

Users ensures access only for the allowed groups.

Implementation details
----------------------
"""



from claun.core import container
from claun.modules.applications.admin import model
from claun.modules.applications.admin.help import __app__ as helpapp # plugin the help app

from claun.modules.distribappcontrol.model import all_configs_by_controller
from claun.modules.distribappcontrol.model import all_configs_by_framework
from claun.modules.environment.model import platforms
from claun.modules.users import restrict

__uri__ = 'applications/admin'
__author__ = 'chadijir'

uris = {}

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/additional-data/(.*)', 'AdditionalData',
           '/additional-data', 'AdditionalData',
           '/list/(.*)/images/(.*)', 'ApplicationImages',
           '/list/(.*)/images', 'ApplicationImages',
           '/list/(.*)', 'Application',
           '/list', 'List',
           '/help', helpapp,
           '/', 'Root',
           )

__app__ = container.web.application(mapping, locals())

def _transform(apps, notallowed=[]):
    """
    Adds/removes some fields to/from all applications in apps.

    If an application has any _attachments, a new key `images` is created that
    contains dictionary, where each key is name of one image and its value is
    a dictionary containing keys `id` (same as name) and `url` (where to get the image).

    :param apps: List of applications
    :param notallowed: Optional list of keys that will be deleted from the passed applications (Default is empty list)
    """
    for app in apps:
        if 'images' not in notallowed and '_attachments' in app:
            app['images'] = {}
            for name in app['_attachments'].iterkeys():
                app['images'][name] = {
                        'id': name,
                        'url': container.baseuri + 'applications/list/' + app['id'] + '/images/' + name
                }

        for key in notallowed:
            if key in app:
                del app[key]
    return apps

# Endpoints

class Root:
    @restrict(['admin', 'admin_applications'])
    def GET(self):
        """
        List of child endpoints, there's no reason to access it.
        """
        return container.output({
                          'list': container.baseuri + __uri__ + '/list',
                          'additional-data': container.baseuri + __uri__ + '/additional-data'})

class List:
    """
    List of all applications
    """

    @restrict(['admin', 'admin_applications'])
    def GET(self, user=None):
        """
        List all applications, without _attachments, _id and _rev.
        """
        apps = [app.value for app in model.all_applications()]
        return container.output(_transform(apps, ['_attachments', '_id', '_rev']))

    @restrict(['admin', 'admin_applications'])
    def POST(self, user=None):
        """Create new application.

        Accepts data that has to contain following keys:
          - name - Application's name
          - framework
            - name - Framework's name
            - configuration - Framework's configuration name
          - runtime - Platform information (The key may be empty (i .e. no platform is present)))

        If any of these keys is missing, or it is not well formed, a 400 Bad Request is returned.
        If all keys are present, an id is generated from name with container.webalize_string,
        and a type: application field is added.

        If the application is successfully created, 200 OK with no body is returned.
        If some problem occurs, a 500 Internal error is returned.
        """
        try:
            contents = container.input(container.web.data())
            if 'name' not in contents or 'framework' not in contents or 'runtime' not in contents or 'name' not in contents['framework'] or 'configuration' not in contents['framework']:
                raise container.web.badrequest()

            contents.update({'id': container.webalize_string(contents['name']), 'type': 'application'})

            result = model.create_application(contents)

            if result is not None:
                return container.output(contents)
            else:
                return container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save application.'}))
        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

class Application:
    """
    Application's detail.
    """
    @restrict(['admin', 'admin_applications'])
    def GET(self, appid, user=None):
        """
        Display information about one application without _attachments, _rev and _id.
        """
        app = model.get_application(appid)
        if app is None:
            raise container.web.notfound()
        return container.output(_transform([app.value], ['_attachments', '_rev', '_id'])[0])

    @restrict(['admin', 'admin_applications'])
    def PUT(self, appid, user=None):
        """
        Update application `appid` without attachments.

        If no application with `appid` is found, a 404 Not Found is returned.
        Accepts data, if it is malformed, a 400 Bad Request is returned.
        Keys images and endpoints are always stripped before sending data to database.
        Application should contain all necessary keys (as specified in `List.POST`), only the absence of `type`
        key is checked.

        Attachments are copied from the updated application.

        If the application is successfully updated, 200 OK with no body is returned.
        If some problem occurs, a 500 Internal error is returned.
        """
        if appid == '': raise container.web.notfound()
        app = model.get_application(appid) # default values
        if app is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such application.'}))

        try:
            contents = container.input(container.web.data())
            if 'images' in contents: del contents['images']
            if 'endpoints' in contents: del contents['endpoints']

            if '_attachments' in app.value and '_attachments' not in contents:
                contents['_attachments'] = app.value['_attachments']

            if 'type' not in contents:
                contents['type'] = 'application'

            if contents['id'] != app['id']:
                contents['id'] = container.webalize_string(contents['name'])

            result = model.update_application(contents, app.id, app.value['_rev'])
            if result is not None:
                return ''
            else:
                raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save application.'}))
        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save application.'}))
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

    @restrict(['admin', 'admin_applications'])
    def DELETE(self, appid, user=None):
        """
        Delete application.

        If no application with id `appid` exists, a 404 Not Found is returned.
        """
        if appid == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such application.'}))
        app = model.get_application(appid)
        if app is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such application.'}))
        try:
            result = model.delete_application(app.value)
            if result:
                return ''
            else:
                return result
        except model.ModelError as me:
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))

class AdditionalData:
    """
    Data needed when creating an application.
    """
    @restrict(['admin', 'admin_applications'])
    def GET(self, name=None, user=None):
        """
        Returns list of all available additional data or lists the appropriate possibilities.

        May return 400 Bad Request if an invalid type is requested.

        :param name: One of the following: platforms, type, processing_type, frameworks, controllers.
        """
        if name is None or name == '':
            return container.output({
                              'platforms': container.baseuri + __uri__ + '/additional-data/platforms',
                              'type': container.baseuri + __uri__ + '/additional-data/type',
                              'processing_type': container.baseuri + __uri__ + '/additional-data/processing_type',
                              'frameworks': container.baseuri + __uri__ + '/additional-data/frameworks',
                              'controllers': container.baseuri + __uri__ + '/additional-data/controllers',
                              })

        else:
            if name not in ['platforms', 'type', 'processing_type', 'frameworks', 'controllers']:
                raise container.web.badrequest()
            process = {'platforms': platforms(),
                    'type': self._type(),
                    'processing_type': self._processing_type(),
                    'frameworks': self._frameworks(),
                    'controllers': self._controllers()
            }
            return container.output(process[name])

    def _type(self):
        """
        Handles `type` type.

        Type tells the rendering engine how to present the application's parameter to the user.
        See applications module for more documentation.
        """
        return ['dropdown', 'boolean', 'slider']

    def _processing_type(self):
        """
        Handles `processing_type` type.

        Processing type tells the apprunner how to pass the parameter to the application.
        See applications module for more documentation.
        """
        return ['cmd', 'cmdnoname', 'cmdnospace', 'envvar']

    def _frameworks(self):
        """
        List of all available framework names and their available configurations.

        Uses model from distribappcontrol module.
        """
        all = all_configs_by_framework(None)
        frameworks = {}
        for result in all:
            if result.key not in frameworks:
                frameworks[result.key] = []
            frameworks[result.key].append(result.value['configuration_name'])
        return frameworks

    def _controllers(self):
        """
        List of all available controller names and their available configurations.

        Uses model from distribappcontrol module.
        """
        all = all_configs_by_controller(None)
        controllers = {}
        for result in all:
            if result.key not in controllers:
                controllers[result.key] = []
            controllers[result.key].append(result.value['configuration_name'])
        return controllers

class ApplicationImages:
    """
    Handles application images.

    Class does not support PUT method. Use DELETE and POST instead or simply POST
    a new image with the same name.
    """

    @restrict(['admin', 'admin_applications'])
    def GET(self, appid, imageid=None, user=None):
        """
        Lists all images attached to given `appid`.

        If no `appid` exists, a 404 Not Found is returned.
        If application has no attachments, an empty list is returned.

        For the return format, see ``_transform`` method.

        If `imageid` is specified, information about only one image is returned.
        """
        app = model.get_application(appid)
        if app is None:
            raise container.web.notfound()
        if imageid is None:
            if '_attachments' not in app.value:
                return container.output([])
        conversion = _transform([app.value], ['_attachments'])[0]
        if imageid is None:
            return container.output(conversion['images'].values())
        else:
            return container.output(conversion['images'][imageid])


    @restrict(['admin', 'admin_applications'])
    def POST(self, appid, imageid=None, user=None):
        """
        Adds an image to `appid`.

        If no such application exists, a 404 Not Found is returned.

        Method can process only one file at a time and the file contents has to be stored under key `file`.
        In case of success, a 200 OK with no body is returned.
        """
        if imageid is not None:
            raise container.web.nomethod()
        app = model.get_application(appid)
        if app is None:
            raise container.web.notfound()

        contents = container.web.input(file = {})
        result = model.put_attachment(app.value, contents['file'].value, contents['file'].filename)
        if result is None:
            return ''
        return result

    @restrict(['admin', 'admin_applications'])
    def DELETE(self, appid, imageid=None, user=None):
        """
        Deletes an image belonging to `appid`.

        If the application `appid` does not exist, a 404 Not Found is returned.
        In case of success, a 200 OK with no body is returned.
        If the attachment/image does not exist, success is indicated as well,
        as no real change happened.
        """
        if imageid is None:
            raise container.web.nomethod()
        app = model.get_application(appid)
        if app is None:
            raise container.web.notfound()

        if model.delete_attachment(app.value, imageid):
            return ''
        return result
