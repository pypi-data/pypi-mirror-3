"""
Claun module: Controller
========================

Description
-----------

Controller module serves as a facade for programs that are used to track
the user or control his/hers movement. Many such programs exist and therefore
this module enables dynamic loading and adding of handlers for these programs.

Using a simple interface, you can define handler for any program and you will
be capable of starting, stopping and restarting the controller program via HTTP
API. It is also possible to pass different configurations to them.

The implementations for various programs are stored in the controllers package.

Supported programs:
  - trackd

Endpoints
---------
  - /
    - GET: List available controllers
    - PUT: Do some action

Configuration
-------------
  controller:
    available: [TrackdController, AnotherController...]

 Depends on filestorage module (Configuration files might be stored there).

Implementation details
----------------------
"""


from claun.core import container


from claun.modules.controller.controllers.abstract_controller import ControllerError
from claun.modules.filestorage import storage

__uri__ = 'controller'
__version__ = '0.1'
__author__ = 'chadijir'
__dependencies__ = ['filestorage']
mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/(.*)', 'Root'
           )

__app__ = container.web.application(mapping, locals())

class Controllers:
    """
    Container and loader for Controller facades.
    """
    def __init__(self, available, storage):
        """
        Sets attributes and tries to load all controller facades from `available`.

        If a controller facade can not be loaded, nothing happens, it just won't be available.

        :param available: List of controller facades to be loaded. Typically taken from the config file.
        :param storage: filestorage.StorageFacade
        """
        self.controllers = {}
        self.storage = storage
        for controller in available:
            cls = self._map_controller(controller)
            if cls is not None:
                inst = cls(self.storage)
                self.controllers[inst.urlname] = inst

    def available_controllers(self):
        """
        Returns all controllers and their URIs. Useful for listing all controller facades available.
        """
        return dict([(name, container.baseuri + __uri__ + '/' + name) for name in self.controllers.keys()])

    def _map_controller(self, name):
        """
        Tries to import `name` instantiatable from controllers package.

        Returns None if not found, or a reference (not instance!).
        """
        try:
            module = __import__('claun.modules.controller.controllers', globals(), locals(), [name])
            cls = getattr(module, name)
            return cls
        except AttributeError as ae:
            container.log.error(ae)
            return None

    def get_controller(self, name):
        """
        Returns facade for controller `name`.
        """
        if name not in self.controllers:
            return None
        return self.controllers[name]

filestorage = storage
controllers = Controllers(container.configuration['modules']['controller']['available'], filestorage)

class Root:
    def GET(self, name):
        """
        Provides basic information.

        If no name is provided, all controller facades are listed as endpoints.
        If a name of an invalid facade is provided, 404.
        With a valid name, list of available actions is shown (start|restart|stop) and it
        is shown if the program is running and if it is a md5 hash of the configuration that is being used.
        """
        if name == '':
            return container.output(container.module_basic_information(__name__, __version__, controllers.available_controllers()))
        else:
            ctl = controllers.get_controller(name)
            if ctl is None:
                raise container.web.notfound()
            return container.output({
                              'running': ctl.is_running(),
                              'configuration_hash': ctl.configuration_hash(),
                              'actions': {
                                'start': 'start',
                                'restart': 'restart',
                                'stop': 'stop'
                                }
                              })

    def PUT(self, name):
        """
        Used when you want to perform some action with the controller facade `name`.

        If no such controller facade exists, 404.

        The configuration and the action are passed in the HTTP message body.
        Every request has to contain 'action' field. If it is missing, a 400 is returned.

        Available actions: start, stop, restart

        When calling stop, you don't have to include any other data.

        When calling start/restart, you have to provide the **configuration** field that contains string with
        the contents of the configuration file.

        In case of success, a 202 Accepted is returned as the underlying processes may take longer time.
        If something goes wrong, the 500 Internal Error is returned containing
        the 'error_description' field.
        """
        if name == '': raise container.web.notfound()
        ctl = controllers.get_controller(name)
        if ctl is None:
            raise container.web.notfound()

        try:
            contents = container.input(container.web.data())
            if 'action' not in contents:
                raise container.web.badrequest()
            if contents['action'] == 'stop':
                if ctl.stop():
                    return self._success(name)
                else:
                    raise container.web.internalerror(container.output({'error_description': 'Undefined problem during controller stop.'}))
            elif contents['action'] in ['restart', 'start']:
                if 'configuration' not in contents:
                    raise container.web.badrequest()
                func = getattr(ctl, contents['action'])
                if func(contents['configuration']):
                    return self._success(name)
                else:
                    raise container.web.internalerror(container.output({'error_description': 'Undefined problem during controller %s.' % contents['action']}))
            else:
                raise container.web.internalerror(container.output({'error_description': 'Unsupported action.'}))
        except ControllerError as ce:
            raise container.web.internalerror(container.output({'error_description': str(ce)}))
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

    def _success(self, name):
        container.web.ctx.status = '202 Accepted'
        container.web.header('Location', controllers.available_controllers()[name])
        return ''
