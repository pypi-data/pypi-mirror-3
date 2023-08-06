"""
Claun module: Applications
==========================

Description
-----------
Applications module provides endpoints for getting info about, starting and stopping applications available in the system.

The application parameters can be (and are) personalized thanks to the users module.

Information about the applications is stored in the couchdb. Accessing the DB is separated
into an applications.model module. An example application document can be seen in the application.json
file. Every application has its own document.

The fields in the **application** document can be these:
  - name - Humanly readable name of the application, can contain special characters. (mandatory)
  - id - ID is used in URL, so it should be unique and contain no special characters. (mandatory)
  - visible - If the application is visible in the list of all applications. (mandatory)
  - description - Description of the application. Can be a longer text. (mandatory)
  - framework - This section is mandatory and denotes what framework for distributed applications does this application use.
    This information is used when the application is run. Current implementation uses the 'distribappcontrol' module that
    takes care about configuration of the applications etc. See its documentation/source for more information. (mandatory)
    - name - Name of the framework.
    - configuration - Name of the basic configuration.
  - framework_configuration - A key: value object where you can override certain configuration keys from the configuration stated in the framework section. (optional)
  - controller - Similar to the framework section, this specifies what controller program the application uses (i. e. trackd).
    Again, this is reflected when starting the app with the 'distribappcontrol'. Controller section is *optional* as some applications
    may implement the control of the movement themselves.
    - name - Name of the controller program.
    - configuration - Name of the controller program configuration.
    - survive_controller - Boolean attribute, that says if the application can survive crashing of the controller program. If false, than
      if the controller stops working, the application will be stopped too. If true, it is possible to restart the controller and the application will
      work again. Optional, if not present, it is presumed that the application will not survive the controller crash.
  - controller_configuration - In this key: value object, you can override the options from the configuration stated in the controller section. (optional)
  - parameters - Application parameters that have no relation to the used framework (i. e. command line switches, input files etc.)
    The concept is very similar to parameters in the `environment` module. If there are any issues, its documentation might help.
    Every parameter can have the following options:
    - name - name of the parameter for the application. It has to be unique as it is used in URI.
    - processing_type - cmdnoname|cmd|envvar - this specifies how the parameter will be passed to the application.
      - cmd - This is named command line attribute (uses the 'name' field): './binary name value' (If the param name is for example "-i", you have to **explicitly** set the name to "-i")
      - cmdnospace - Same as 'cmd' option, only places no space between the name and value: './binary namevalue'
      - cmdnoname - This is the command line attribute without name: './binary value'
      - envvar - Pass the argument as the environment variable: 'name=value'
      For particular implementation, please see the module responsible for running the application on the target machines.
    - human_name - Name for the user, like 'Map file' or 'Number of animals'
    - type - dropdown|boolean|slider - or other, this field should tell clients how to render the field when the user can edit it
      - values - specific for dropdown, this is a list of values from which can the user select (mandatory)
      - min - specific for slider, minimal selectable value (mandatory)
      - max - specific for slider, maximal selectable value (mandatory)
      It is possible that the 'fileselection' will be added. However, if it is to search the disk for certain files, it has to be backed up by some server-side implementation.
      One quick idea: For clients, disguise the fileselection as dropdown and fill values with the filenames.
    - default - default value for this parameter, it is pre-selected when presenting to the user, or used when there is no other value
    - help - some helpful text that can explain what the parameter does
    - user_editable - whether a user can edit the parameter; you may want some parameters to be fixed to some value
  - runtime - This section contains information on how to run the application on different platforms.
    For every platform there is a separate section named after the platform (i. e. "gentoo", or "windows-x86") containing information required
    to run the application on this platform. The usage of the attributes is highly specific and relies on the implementation of
    the module used to run the application on the actual cluster nodes.

    Moreover, the attributes are with high probability platform specific, but the proposed set for *nix environments is:

    - directory - An absolute path to the working directory for the application. (mandatory)
    - binary - An absolute path to the binary. (mandatory)
    - md5sum - md5 checksum of the binary that might be used to run only certain version (optional)
    - terminate - How to terminate the application, typically some string sent to the stdin, or key combination. (optional)
    - kill - How to kill the application if for example not responding. (optional)

    The idea for terminate and kill attributes is that in the runner's implementation there will be a dictionary of supported commands
    and the values written here will be the keys of this dictionary.
  - type - 'application', helps to distinguish the documents in the database

Do not forget the `type` field that is used in the map and reduce functions.

Endpoints
---------
  - /list
    - GET: List of all applications
  - /list/{appid}
    - GET: Information about application
    - PUT: start/stop application when sending data like {'action': 'start'} or {'action': 'stop'}
  - /list/{appid}/images
    - GET: list of links to images for this application
  - /list/{appid}/images/{imagename}
    - GET: image data
  - /list/{appid}/parameters
    - GET: list of parameters for appid
  - /list/{appid}/parameters/{paramid}
    - GET: Information about parameter
    - PUT: Update parameter
  - /admin - Administrator's access, see admin submodule for details.
  - /admin/help - Administrator's help pages

Configuration
-------------
db_name: somename - name of the database in couchdb where the information is stored

Depends on couchdb, users and distribappcontrol modules.
Admin submodule depends on couchdb, users, applications, environment (admin submodule), distribappcontrol and rstprocessor (for admin/help).

Implementation details
----------------------
"""



from claun.core import container
from claun.modules.applications import model
from claun.modules.applications.admin import __app__ as adminapp # plugin the admin app

from claun.modules.distribappcontrol import distributor
from claun.modules.users import personalize
from claun.modules.users import restrict

__uri__ = 'applications'
__version__ = '0.2'
__author__ = 'chadijir'
__dependencies__ = ['couchdb', 'users', 'environment', 'distribappcontrol', 'rstprocessor']

uris = {}


mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/admin', adminapp,
           '/list', 'List',
           '/list/(.*)/parameters', 'ApplicationParameters',
           '/list/(.*)/images/(.*)', 'ImageServer',
           '/list/(.*)/images', 'ApplicationImages',
           '/list/(.*)/parameters/(.*)', 'ApplicationParameterDetail',
           '/list/(.*)', 'Application',
           '/', 'Root',
           )

__app__ = container.web.application(mapping, locals())

def _transform(apps, notallowed=[]):
    """
    Transforms apps list of app dictionaries into a publishable form.

    If not in `notallowed`, the keys actions, images, endpoints and status are added to
    the original app dictionary.
    The endpoints are absolute links to these resources:
      - parameters
      - images
    The actions are key: value records for actions callable on each application with PUT.
      - actions

    The status key contains value obtained from the distribappcontrol.Distributor.status method.

    The images key containes list of links to all images attached to the application in the database
    (uses _attachments key provided from couchdb). If there are no attachments, the key results into an empty list.

    All links are absolute.

    :param apps: list of app dictionaries
    :param notallowed: list of keys that are not to be publixhed, optional, default is empty
    """
    for app in apps:
        if 'endpoints' not in notallowed:
            app['endpoints'] = {"parameters": container.baseuri + __uri__ + '/list/' + app['id'] + '/parameters',
                    "images": container.baseuri + __uri__ + '/list/' + app['id'] + '/images',
                    }
        if 'actions' not in notallowed:
            app['actions'] = {'start': 'start', 'stop': 'stop'}

        if 'images' not in notallowed and '_attachments' in app:
            app['images'] = []
            for name in app['_attachments'].iterkeys():
                app['images'].append(container.baseuri + __uri__ + '/list/' + app['id'] + '/images/' + name)
        if 'status' not in notallowed:
            app['status'] = distributor.status(app['id'])

        for key in notallowed:
            if key in app:
                del app[key]
    return apps


class Root:
    def GET(self):
        """
        Basic information.
        """
        return container.output(container.module_basic_information(__name__, __version__, {'list': container.baseuri + __uri__ + '/list'}))


class List:
    def GET(self):
        """
        List all applications, without _attachments and parameters.
        """
        apps = [app.value for app in model.all_applications()]
        return container.output(_transform(apps, ['_attachments', 'parameters']))


class Application:
    def GET(self, name):
        """
        Display information about one application without _attachments and parameters.
        """
        app = model.application_by_id(name)
        if app is None:
            raise container.web.notfound()
        return container.output(_transform([app.value], ['_attachments', 'parameters'])[0])

    @restrict('all')
    def PUT(self, appid, user=None):
        """
        Restricted to 'all'.

        Do some action with the application.

        Currently available are start and stop, the kind of action is transported in HTTP message
        body as message's parameter action: {"action": "start"}.

        A distribappcontrol.Distributor instance is then called.

        If no action is specified, 400.
        If unsupported action is specified, 500.
        """
        if appid == '': raise container.web.notfound()
        app = model.application_by_id(appid) # default values
        if app is None:
            raise container.web.notfound()

        try:
            contents = container.input(container.web.data())
            if 'action' not in contents:
                raise container.web.badrequest()
            if contents['action'] == 'stop':
                result = distributor.stop(user, app.value)
                container.web.ctx.status = result['status']
                return container.output(result['body'])
            elif contents['action'] == 'start':
                app.value['parameters'] = model.parameters(user, appid) # personalized parameters
                result = distributor.launch(user, app.value)
                container.web.ctx.status = result['status']
                if result['status'] == '202 Accepted':
                    container.web.header("Location", container.baseuri + __uri__ + '/list/' + appid)
                return container.output(result['body'])
            else:
                raise container.web.internalerror(container.output({'error_description': 'Unsupported action.'}))
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()


class ApplicationParameters:
    """
    Public, but personalized information about application's parameters.
    """
    @personalize
    def GET(self, appname, user=None):
        """
        Display all parameters of application `appname`.

        If no such application is found, 404.
        Delegated to model.parameters method.
        """
        params = model.parameters(user, appname)
        if params is None:
            raise container.web.notfound()
        return container.output(params)


class ApplicationParameterDetail:
    """
    Application's parameter. Restricted endpoint (group 'all').
    """
    @restrict('all')
    def GET(self, appname, paramname, user=None):
        """
        Information about one parameter for application appname.

        Delegated to model.parameter_by_name. If no parameter, 404.
        """
        param = model.parameter_by_name(user, appname, paramname)
        if param is None:
            raise container.web.notfound()
        return container.output(param.value)

    @restrict('all')
    def PUT(self, appname, paramname, user=None):
        """
        Update a parameter.

        Delegated to model.save_parameter.
        Returns either 200, or 404.
        """
        if model.save_parameter(user, appname, container.input(container.web.data())):
            return container.output({'status': 'OK'})
        else:
            raise container.web.notfound()


class ApplicationImages:
    """
    Public endpoint serving list of all images for given app.
    """
    def GET(self, appname):
        """
        List of links to all images of given appname. Uses _transform.

        If no such appname exists, 404.
        """
        app = model.application_by_id(appname)
        if app is None:
            raise container.web.notfound()
        if '_attachments' not in app.value:
            return container.output([])
        return container.output(_transform([app.value], ['_attachments'])[0]['images'])


class ImageServer:
    """
    Provides images stored as application's attachments.
    """
    def GET(self, appname, imagename):
        """
        Tries to get an image of `imagename` for `appname`.

        If no application or no image is found, 404.
        Otherwise the Content-Type and Cache-Control headers are set and the image's binary data is returned.
        """
        app = model.application_by_id(appname)
        if app is None:
            raise container.web.notfound()
        body = model.get_attachment(app.id, imagename)
        if body is None:
            raise container.web.notfound()
        type = app.value['_attachments'][imagename]['content_type']
        container.web.header("Content-Type", type)
        if type.startswith('image'):
            container.web.header("Cache-Control", "max-age=86400, must-revalidate")
        contents = body.read()
        body.close()
        return contents
