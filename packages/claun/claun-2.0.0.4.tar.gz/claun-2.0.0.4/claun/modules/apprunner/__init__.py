"""
Claun module: App Runner
========================

Description
-----------

App Runner should be used as a direct parent for applications run on destination nodes.
This implementation is based on the fact that applications might use various frameworks
and therefore can dynamically load runtimes for various frameworks and launch applications
on them.

A user requests to start some application with some framework, provides necessary information
and the application is launched on this machine. This module does not contact other components.

The implementations for various frameworks are stored in the frameworks package.

Supported frameworks:
  - CAVELib

Endpoints
---------
  - /
    - GET: List all available frameworks
    - PUT: Do some action

Configuration
-------------
  apprunner:
    frameworks: [CaveLibFramework, AnotherFramework]

Depends on filestorage (Configuration files might be stored there).

Implementation details
----------------------
"""

from claun.core import container

from claun.modules.apprunner.frameworks.abstract_framework import FrameworkError
from claun.modules.filestorage import storage

__docformat__ = 'restructuredtext en'

__uri__ = 'apprunner'
__version__ = '0.1'
__author__ = 'chadijir'
__dependencies__ = ['filestorage']

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/(.*)', 'Root',
           )

__app__ = container.web.application(mapping, locals())

class Frameworks:
    """
    Container and loader for framework runners.
    """
    def __init__(self, available, storage):
        """
        Sets attributes and tries to load all framework runners from `available`.

        If a framework can not be loaded, nothing happens, it just won't be available.

        :param available: List of framework runners to be loaded. Typically taken from the config file.
        :param storage: filestorage.StorageFacade
        """
        self.frameworks = {}
        self.storage = storage
        for framework in available:
            cls = self._map_framework(framework)
            if cls is not None:
                inst = cls(self.storage)
                self.frameworks[inst.urlname] = inst

    def available_frameworks(self):
        """
        Returns all frameworks and their URIs. Useful for listing all frameworks.
        """
        return dict([(name, container.baseuri + __uri__ + '/' + name) for name in self.frameworks.keys()])

    def _map_framework(self, name):
        """
        Tries to import `name` instantiatable from frameworks package.

        No instances are created, only a reference (or None if no such thing is found) is returned.
        """
        try:
            module = __import__('claun.modules.apprunner.frameworks', globals(), locals(), [name])
            cls = getattr(module, name)
            return cls
        except AttributeError as ae:
            container.log.error(ae)
            return None

    def get_framework(self, name):
        """
        Returns runner for `name` framework or None.
        """
        if name not in self.frameworks:
            return None
        return self.frameworks[name]

filestorage = storage
frameworks = Frameworks(container.configuration['modules']['apprunner']['frameworks'], filestorage)

class Root:
    def GET(self, name):
        """
        Provides basic information.

        If no name is provided, all frameworks are listed as endpoints.
        If a name of an invalid framework is provided, 404.
        With a valid name, list of available actions is shown (start|stop) and AbstractFramework.applications_stats() result is shown.
        """
        if name == '':
            return container.output(container.module_basic_information(__name__, __version__, frameworks.available_frameworks()))
        else:
            frmwrk = frameworks.get_framework(name)
            if frmwrk is None:
                raise container.web.notfound()


            return container.output({
                              "actions": {
                              "start": 'start',
                              "stop": 'stop',
                              },
                              "applications": frmwrk.applications_stats()
                              })

    def PUT(self, name):
        """
        Used when you want to start/stop some application on framework `name`.

        If no such framework exists, 404.

        Information about application and action are passed in HTTP messages' body.
        Every request has to contain 'action' which is either **start** or **stop**.

        When calling stop, you have to include application_id key as well.

        When calling start, you have to include following keys. For more information, please see AbstractFramework.start() method.
          - application
          - configuration
          - runtime
          - master

        If some problem occurs, a 500 Internal Error is returned that contains object with 'error_description' key.
        In case of success, a 202 Accepted with Location header is returned. The Location points to the framework's detail page.
        """
        if name == '': raise container.web.notfound()
        frmwrk = frameworks.get_framework(name)
        if frmwrk is None:
            raise container.web.notfound()

        try:
            contents = container.input(container.web.data())
            if 'action' not in contents:
                raise container.web.badrequest()
            if contents['action'] == 'stop':
                if frmwrk.stop(contents['application_id']):
                    return self._success(name)
                else:
                    raise container.web.internalerror(container.output({'error_description': 'Undefined problem during application stop.'}))
            elif contents['action'] == 'start':
                if frmwrk.start(contents['application'], contents['configuration'], contents['runtime'], contents['master']):
                    return self._success(name)
                else:
                    raise container.web.internalerror(container.output({'error_description': 'Undefined problem during application %s.' % contents['action']}))
            else:
                raise container.web.internalerror(container.output({'error_description': 'Unsupported action.'}))
        except FrameworkError as are:
            raise container.web.internalerror(container.output({'error_description': str(are)}))
        except KeyError as ke:
            container.log.error('Missing value: %s' % str(ke))
            raise container.web.badrequest()
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

    def _success(self, name):
        """
        Shorthand for providing 202 Accepted and Location of framework `name`.
        """
        container.web.ctx.status = '202 Accepted'
        container.web.header('Location', frameworks.available_frameworks()[name])
        return ''
