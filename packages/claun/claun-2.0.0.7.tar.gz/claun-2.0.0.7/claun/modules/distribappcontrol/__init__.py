"""
Claun module: Distrib App Control
=================================

Description
-----------
Distrib App Control is initially designed to be used in CAVE environment and
should be used to run/stop applications in a distributed system.

Module provides support for two kinds of 'things', frameworks and controllers.
Every CAVE application depends on some framework and may use some controller.
Framework represents the library used to sync and render the application.
Controller represents an optional piece of software that is used to control user's movement
within the application's scene.

Both frameworks and controllers may have many configurations which are stored in the CouchDB
and accessed via model module. Every configuration is stored as a separate document whose
structure fully depends on the implementation of configuration generator builder
(see controllerconfiguration and frameworkconfiguration modules).

Apart from frameworks and controllers specification, there is a **Distributor** class that controls
launch, runtime and stop of the application. All applications should be controlled via instance of this class.

During the distributors lifetime, it is possible to register event listeners
which are informed every time that something interesting happens (start, stop,
etc.).

Frameworks
----------

An example document of one framework's configuration (framework CAVELib) can be found in framework.json file.
Mandatory fields are:
  - type - framework (Crucial attribute)
  - framework_name - Some identification of the framework that is then used in application's configuration (framework.name field).
    Multiple configurations of the same framework has to have the same framework_name.
  - configuration_name - Some identification of this configuration that is then used in application's configuration (framework.configuration field)
  - parameters - This is the field where framework specific settings goes

All other fields are framework specific and should be documented in the appropriate Builder implementation.

Controllers
-----------

An example configuration for the trackd program can be found in controller.json file.
Mandatory fields are:
  - type - controller (Critical attribute)
  - controller_name - Name of the controller program that is then used in application's configuration (controller.name field)
    Multiple configurations of the same controller has to have the same framework_name.
  - configuration_name - Some identification of this configuration that is then used in application's configuration (controller.configuration field)
  - parameters - This is the field where controller specific settings goes.

All other fields are framework specific and should be documented in the appropriate Builder implementation.

Endpoints
---------
There are no public endpoints except the admin submodule.

Configuration
-------------
  distribappcontrol:
    db_name: claun_distribappcontrol

 Depends on couchdb and environment. From environment the module uses the references to cluster.apprunnerclient and
 cluster.controllerclient instances.

 The admin submodule depends on users.

Implementation details
----------------------

"""
import hashlib
import time
from threading import Thread
import collections

from claun.core import container

from claun.modules import environment
from claun.modules.distribappcontrol.admin import __app__ as adminapp # plugin admin app
from claun.modules.distribappcontrol.controllerconfiguration import *
from claun.modules.distribappcontrol.frameworkconfiguration import *

__docformat__ = 'restructuredtext en'

__uri__ = 'distribappcontrol'
__version__ = '0.2'
__author__ = 'chadijir'
__dependencies__ = ['couchdb', 'environment', 'users']

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/admin', adminapp,
           '/', 'Root',
           )

__app__ = container.web.application(mapping, locals())


class Root:
    """
    Provides basic information.
    """
    def GET(self):
        return container.output(container.module_basic_information(__name__, __version__, {}))


class EventBroadcaster:
    """
    Broadcaster can inform registered objects about some event.

    It is useful for the application startup process, for particular events,
    please see the source code.

    Every event is specified as a named class constant with numeric value.
    When triggering an event, use these constants. A numeric value will be
    passed, but Broadcaster will translate the code to a proper method name.

    Every listener is expected to implement a ``receive_event`` method.

    >>> a = ...
    >>> b = EventBroadcaster() # PLATFORMS_OK = 6
    >>> b.eventListeners.append(a)
    >>> b.broadcast_event(b.PLATFORMS_OK) # calls a.receive_event('platforms_ok')
    """

    APPLICATION_STARTING = 0 # application
    APPLICATION_DISTRIBUTING = 1 # application
    APPLICATION_ERROR = 2 # application, error
    APPLICATION_DISTRIBUTING = 3 # application
    APPLICATION_STOP_REQUESTED = 4 # application
    APPLICATION_STOPPED = 5 # application
    APPLICATION_CRASHED = 6 # application, message

    INFORMATION_GATHERED = 7

    PROJECTIONS_MISSING = 8
    PROJECTIONS_UNCOVERED = 9 # projections
    PROJECTIONS_OK = 10 # projections

    PLATFORMS_CHOSEN = 11 # platform
    PLATFORMS_INCONSISTENCY = 12
    PLATFORMS_UNSUPPORTED = 13 # platform
    PLATFORMS_OK = 14 #platform

    CONTROLLER_REQUIRED = 15
    CONTROLLER_UNREACHABLE = 16 # controller
    CONTROLLER_CONFIGURATION_BUILT = 17 # controller, configuration
    CONTROLLER_RESTART = 18 # controller
    CONTROLLER_START = 19 # controller
    CONTROLLER_ERROR = 20 # controller, error
    CONTROLLER_OK = 21 # controller

    FRAMEWORK_SETUP = 22
    FRAMEWORK_ERROR = 23 # framework, configuration, error
    FRAMEWORK_CONFIGURATION_BUILT = 24 # framework, configuration

    def __init__(self):
        """Initiates structures and calls _generate_method_names."""
        self.eventListeners = []
        self.eventNames = {}
        self._generate_method_names()

    def _generate_method_names(self):
        """
        For every numeric member of the class creates a record in the
        ``eventNames`` dictionary.

        The record has a numeric value as a key and a lowercased name as a
        value. These values are useful when propagating events.
        """
        members = [a for a in dir(self) if not isinstance(a, collections.Callable) and isinstance(getattr(self, a), int)]
        for name in members:
            value = getattr(self, name)
            self.eventNames[value] = name.lower()
            self.eventNames[name.lower()] = value

    def broadcast_event(self, event, *args, **kwargs):
        """
        Broadcasts event to all listeners with various parameters.

        If an unknown event is passed, an error is logged and nothing happens.

        :param event: Numeric code of the event, it is translated to a string.
        """
        for el in self.eventListeners:
            try:
                el.receive_event(self.eventNames[event], *args, **kwargs)
            except KeyError:
                container.log.error('Unknown event %s' % event)
            except AttributeError:
                container.log.error('Broken event listener %s' % el)

class Distributor:
    """
    Controls distributed applications.

    This class contains method for the whole lifecycle of the distributed application.
    """

    CONTROLLER_START_TIMEOUT = 30
    """
    How long will the startup process wait for controller start (seconds).
    """

    def __init__(self, broadcaster):
        """
        :param broadcaster: Instance of ``claun.modules.distribappcontrol.EventBroadcaster``
        """
        self.stalkers = {}
        self.broadcaster = broadcaster

    def add_event_listener(self, object):
        """Add `object` to the broadcaster instance"""
        self.broadcaster.eventListeners.append(object)

    def remove_event_listener(self, object):
        """Remove `object` from the broadcaster instance"""
        self.broadcaster.eventListeners.remove(object)
        
    def launch(self, user, app):
        """
        Starting procedure for the `app`.

        The startup process may be very complex and might take certain amount of time.

        1) Projections: If any projection is selected and if all selected projections are maintained by running computers.
        2) Platforms: All nodes required for selected projections have to run the winning platform, which is taken from the master node
           (i. e. node with the lowest masterpriority, see environment module) and the application can be run on such platform.
        3) If an application needs a controller program:
           The configuration is built, the master node is checked if it can run this controller.
           If this controller with the exact same configuration is running, go to step 4.
           If it is running with different configuration, it is stopped.
           Controller is then started with new configuration. The startup process waits for successful startup for CONTROLLER_START_TIMEOUT seconds.
           If the controller is not started, the application startup is not successful.
        4) Framework configuration is built for all required nodes.
        5) A start method of environment.apprunner is invoked and that is considered as a successful start of the application.

        However it should be possible to control the application during its runtime, so for every started application an ApplicationStalker
        instance is created and started as a separate thread. This instance is responsible for polling the application status on end nodes
        and keeping track of what is happening with it.

        :param user: Raw user instance from DB (ideally filled by users module), it is used to get personalized configuration and says who started the application
        :param app: Application dict, expected keys:
          - framework_configuration - Dict with app specific framework configuration (Optional)
          - parameters - Application attributes. For details see applications module.
          - controller_configuration - Dict with app specific controller configuration. (Optional)
          - framework - {name: framework name, configuration: base config name}
          - controller - {name: controller name, configuration: base controller name, survive_controller: If an application can survive controller program crash} (Optional)
          - runtime - Dict with information for all platforms that the application can run on. Platform name is key, and the contents is platform specific.
          - id - Identifier
        """
        # gather all information
        application = app
        self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_STARTING, application=application['id'])
        envconfig = environment.model.configuration(user)
        computers = environment.clusterclient.enhance()
        container.log.debug('Info gathered')
        self.broadcaster.broadcast_event(self.broadcaster.INFORMATION_GATHERED)

        # check projections
        activeprojections = [a['name'] for a in envconfig if 'group' in a and a['group'] == 'projection' and (('value' in a and a['value'] is True) or ('value' not in a and a['default'] is True))]
        if not activeprojections:
            self.broadcaster.broadcast_event(self.broadcaster.PROJECTIONS_MISSING)
            return self._result(500, "no_projections", "No projections were selected.")

        availableprojections = dict([(k, c) for c in computers.itervalues() if c['online'] is True for k in c['projections'].keys()])
        uncoveredprojections = [active for active in activeprojections if active not in availableprojections.keys()]
        if uncoveredprojections:
            self.broadcaster.broadcast_event(self.broadcaster.PROJECTIONS_UNCOVERED, projections=uncoveredprojections)
            return self._result(500, "uncovered_projections", "Some projections are not covered by running computers.")

        container.log.debug('Projections checked')
        self.broadcaster.broadcast_event(self.broadcaster.PROJECTIONS_OK, projections=activeprojections)

        # check platforms
        #requiredcomputers = sorted([(c['hostname'], c) for projection, c in availableprojections.iteritems() if projection in activeprojections], cmp=lambda x, y: x[1]['masterpriority'] > y[1]['masterpriority'])
        requiredcomputers = sorted([(c['hostname'], c) for projection, c in availableprojections.iteritems() if projection in activeprojections], key=lambda x: x[1]['masterpriority'])
        master = requiredcomputers[0][1]
        requiredcomputers = dict(requiredcomputers)
        winningplatform = master['platform'] # select platform that is run on master (there might probably be another algorithm for that, like the majority)
        self.broadcaster.broadcast_event(self.broadcaster.PLATFORMS_CHOSEN, platform=winningplatform)

        for c in requiredcomputers.itervalues(): # platform consistency in cluster
            if c['platform'] != winningplatform:
                self.broadcaster.broadcast_event(self.broadcaster.PLATFORMS_INCONSISTENCY)
                return self._result(500, "platform_inconsistency", "One or more computers is not running the winning platform (%s)." % winningplatform)

        if winningplatform not in application['runtime']: # can an application run on that platform?
            self.broadcaster.broadcast_event(self.broadcaster.PLATFORMS_UNSUPPORTED, platform=winningplatform)
            return self._result(500, "bad_platform", "Application can not run on the 'master' platform (%s)." % winningplatform)

        container.log.debug('Platforms checked')
        self.broadcaster.broadcast_event(self.broadcaster.PLATFORMS_OK, platform=winningplatform)

        # setup controller
        if 'controller' in application: # controller is required
            self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_REQUIRED)
            try:
                if 'controller_configuration' not in application: application['controller_configuration'] = {} # fill missing values
                controller = environment.clusterclient.controller(master['hostname'])
                result = controller.status(application['controller']['name'])
                if result is None:
                    self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_UNREACHABLE, controller=application['controller']['name'])
                    return self._result(500, "controller_error", "There was some problem when starting the controller. (Probably a network issue)")
                builder = ControllerConfigurationBuilder(application['controller']['name'], application['controller']['configuration'], application['controller_configuration'])
                controllerconfig = builder.build()
                self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_CONFIGURATION_BUILT, controller=application['controller']['name'], configuration=application['controller']['configuration'])
                if result['running'] is True: # is controller running?
                    if result['configuration_hash'] != hashlib.md5(controllerconfig).hexdigest():
                        container.log.debug('Requesting controller restart')
                        self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_RESTART, controller=application['controller']['name'])
                        status = controller.restart(application['controller']['name'], controllerconfig)
                    else:
                        status = True
                else:
                    container.log.debug('Requesting controller start')
                    self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_START, controller=application['controller']['name'])
                    status = controller.start(application['controller']['name'], controllerconfig)

                if status != True:
                    container.log.error('Cannot start controller: %s' % status['error_description'])
                    self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_ERROR, controller=application['controller']['name'], error=status['error_description'])
                    return self._result(500, "no_controller", "Cannot start the desired controller: %s." % status['error_description'])

                container.log.debug('Controller start accepted, waiting when it\'s ready...')
                # wait for the controller startup
                attempts = 0
                while True:
                    result = controller.status(application['controller']['name'])
                    if result is None or attempts == self.CONTROLLER_START_TIMEOUT: # wait 30 seconds for controller
                        self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_ERROR, controller=application['controller']['name'], error='Timeout reached')
                        return self._result(500, "controller_error", "Controller did not start.")
                    if result['running']:
                        self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_OK, controller=application['controller']['name'])
                        container.log.debug('Controller ready')
                        break
                    time.sleep(1)
                    attempts += 1
            except environment.ControllerClientError as cce:
                container.log.error(cce)
                self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_ERROR, controller=application['controller']['name'], error=str(cce))
                return self._result(500, "controller_error", str(cce))
            except ControllerConfigurationBuilderError as cbe:
                container.log.error(cbe)
                self.broadcaster.broadcast_event(self.broadcaster.CONTROLLER_ERROR, controller=application['controller']['name'], error=str(cbe))
                return self._result(500, "controller_error", str(cbe))

        # setup framework and distribute
        self.broadcaster.broadcast_event(self.broadcaster.FRAMEWORK_SETUP)
        try:
            if 'framework_configuration' not in application: application['framework_configuration'] = {}
            builder = FrameworkConfigurationBuilder(application['framework']['name'], application['framework']['configuration'], requiredcomputers, master, envconfig, application['framework_configuration'])
            configurations = builder.build()
        except FrameworkConfigurationBuilderError as fcbe:
            container.log.error(fcbe)
            self.broadcaster.broadcast_event(self.broadcaster.FRAMEWORK_ERROR, framework=application['framework']['name'], error=str(fcbe))
            return self._result(500, "framework_error", str(fcbe))
        container.log.debug('Framework configuration generated')
        self.broadcaster.broadcast_event(self.broadcaster.FRAMEWORK_CONFIGURATION_BUILT, framework=application['framework']['name'], configuration=application['framework']['configuration'])

        try:
            runtime = application['runtime'][winningplatform]
            container.log.debug('Starting application')
            self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_DISTRIBUTING, application=application['id'])
            environment.clusterclient.apprunner.start(master['hostname'], configurations, application, runtime)
        except environment.AppRunnerClientError as arce:
            container.log.error(arce)
            self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_ERROR, application=application['id'], error=str(arce))
            return self._result(500, "cannot_start", str(arce))

        # run polling
        if 'controller' in application:
            stalker = ApplicationStalker(environment.clusterclient.apprunner, application, controller, controllerconfig, user=user)
        else:
            stalker = ApplicationStalker(environment.clusterclient.apprunner, application, user=user)

        stalker.start()
        self.stalkers[application['id']] = stalker

        return self._result("202 Accepted", "ok", "sent")

    def stop(self, user, application):
        """
        Tries to stop `application`.

        Uses ApplicationStalker to stop `application`. After successful stop or crash of the application,
        the appropriate ApplicationStalker instance is deleted.

        A user-level stopping of applications is implemented. If a user is not in group 'admin' or
        'admin_stop_applications', he/she can not stop applications started by other users.

        For return uses self._result method.

        :param user: Raw user instance from DB (ideally filled by users module)
        :param application: Dict. Has to contain an 'id' key that was used when the app was started.
        """
        try:
            if application['id'] not in self.stalkers:
                return self._result(500, "stopping_error", "This application was not started by this instance.")

            # check user's permissions
            requester = user
            starter = self.stalkers[application['id']].user

            if requester['id'] != starter['id']: # different user tries to turn it off
                if 'admin' not in requester['permissions'] and 'admin_stop_applications' not in requester['permissions']:
                    return self._result(500, 'stopping_error', 'Application was started by someone else and you don\'t have enough rights to stop it.')

            self.stalkers[application['id']].stop_application()
            self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_STOP_REQUESTED, application=application['id'])
            container.log.debug('Waiting for app to stop everywhere...')
            while self.stalkers[application['id']].running():
                time.sleep(0.3)
            if self.stalkers[application['id']].stopped():
                container.log.debug('App stopped')
                self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_STOPPED, application=application['id'])
                ret = self._result(200, "ok", "stopped")
            else:
                container.log.debug('App probably crashed.')
                self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_CRASHED, application=application['id'], message=self.stalkers[application['id']].crashed())
                ret = self._result(200, "ok", "Crashed: %s" % self.stalkers[application['id']].crashed())
            self.stalkers[application['id']].stop()
            del self.stalkers[application['id']]
            return ret
        except KeyError as ke:
            container.log.error(ke)
            return self._result(200, "ok", "Already stopped before")
        except environment.AppRunnerClientError as arce:
            container.log.error(arce)
            self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_ERROR, application=application['id'], error=str(arce))
            if not self.stalkers[application['id']].running():
                del self.stalkers[application['id']]
            return self._result(500, "stopping_error", str(arce))

    def status(self, appname):
        """
        Returns current status of `appname`.

        Uses running polling thread (ApplicationStalker). If no such thread exists, returns None.
        Otherwise returns 'running' or 'stopped' or 'crashed: crashmessage'.
        """
        if appname not in self.stalkers:
            return None

        if self.stalkers[appname].running():
            return 'running'
        elif self.stalkers[appname].stopped():
            self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_STOPPED, application=appname)
            return 'stopped'
        elif self.stalkers[appname].crashed():
            self.broadcaster.broadcast_event(self.broadcaster.APPLICATION_CRASHED, application=appname, message=self.stalkers[appname].crashed())
            return 'crashed: %s' % self.stalkers[appname].crashed()
        return None

    def _result(self, status, name, description):
        """
        Shorthand for returning well-formed result states.

        :param status: 500, 200 or full HTTP Status (e. g. "202 Accepted")
        :param name: Name of the error, or status
        :param description: Some message.
        """
        if status == 500:
            return {
                'status': "500 Internal Server Error",
                'body': {"error": name, "error_description": description}
            }
        elif status == 200:
            return {
                'status': "200 OK",
                'body': {"status": name, "message": description}
            }
        else:
            return {
                'status': status,
                'body': {"name": name, "description": description}
            }


class ApplicationStalker(Thread):
    """
    Thread that checks application status on cluster nodes.

    The thread keeps track of application state in three levels:
      - RUNNING - The application is up and running
      - STOPPED - Application was properly stopped or at least is not running does not seem to have crashed.
      - CRASHED - Application looks like it crashed.
    """

    REFRESH_TIME = 3
    """
    How often the thread should check the application (in seconds).
    """
    RUNNING = 1
    CRASHED = 2
    STOPPED = 3

    def __init__(self, apprunner, application, controllerrunner=None, controllerconfiguration=None, user=None):
        """
        Assigns fields.

        :param apprunner: environment.apprunnerclient instance
        :param application: Application dict as in Distributor.launch method.
        :param controllerrunner: If an application needs controller, the  environment.controllerclient instance for master node.
        :param controllerconfiguration: String with controller configuration in case a restart will be needed.
        :param user: User dict saying who is responsible for the application's start.
        """
        Thread.__init__(self)
        self.daemon = True
        self.kill = False
        self.apprunner = apprunner
        self.application = application
        self.controller = controllerrunner
        self.controllername = None if 'controller' not in self.application else self.application['controller']['name']
        self.survive_controller = False if ('controller' not in self.application) or ('survive_controller' not in self.application['controller']) else self.application['controller']['survive_controller']
        self.controller_configuration = controllerconfiguration
        self.status = self.RUNNING
        self.message = None
        self.stop_app = False
        self.user = user

    def running(self):
        """
        Is application running?
        """
        return self.status == self.RUNNING

    def stopped(self):
        """
        Is application stopped?
        """
        return self.status == self.STOPPED

    def crashed(self):
        """
        Has application crashed?

        If yes, returns string, False otherwise.
        """
        if self.status == self.CRASHED:
            return self.message
        else:
            return False

    def stop(self):
        """
        Stop the thread.
        """
        self.kill = True

    def _stop_application(self, message):
        """
        Real stop application procedure.

        Currently it does not wait for stop confirmation, it just presumes it was sucessful
        if no AppRunnerClientError was encountered.
        """
        container.log.debug(message)
        try:
            self.apprunner.stop(self.application) # implement waiting loop?
            self.message = message
        except environment.AppRunnerClientError as arce:
            container.log.error(arce)
            self.message = str(arce)

    def stop_application(self):
        """
        Stops the thread and the application.
        """
        self.stop_app = True

    def run(self):
        """
        Infinite loop controlling the application (and controller) status.

        It can restart controller if the application can survive such operation. application['controller']['survive_controller']

        The application is stopped when:
          - The controller crashes and the application cannot survive that.
          - The controller crashes, the application can survive that, but the controller can not be started again (or it takes too long).
          - The controller node stops responding.
          - The application was stopped on some node.
          - The application crashed on some node.
          - Some node stopped responding.

        """
        controller_max_repeats = Distributor.CONTROLLER_START_TIMEOUT / float(self.REFRESH_TIME)
        controller_repeats = 0
        while not self.kill:
            if self.stop_app:
                self._stop_application('Stop requested')
                self.status = self.STOPPED
                return

            if self.controller is not None and self.controllername is not None:
                try:
                    status = self.controller.status(self.controllername)
                    if status is None or not status['running']: # problem
                        container.log.debug('Controller crashed')
                        if controller_repeats == 0: # first encounter
                            if self.survive_controller and self.controller_configuration is not None:
                                container.log.debug('Controller crashed, restarting...')
                                restart = self.controller.restart(self.controllername, self.controller_configuration)
                                if restart != True: # restart unsuccessful
                                    container.log.debug('Cannot restart controller, stopping application.')
                                    self._stop_application('Controller crashed, I tried to restart, but I was unsuccessful.')
                                    self.status = self.STOPPED
                                    return
                                else: # check later that it really started
                                    controller_repeats += 1
                            else: # no restarts allowed
                                container.log.error('Controller crashed, stopping application.')
                                self._stop_application('Controller has crashed. Cannot continue without him.')
                                self.status = self.STOPPED
                                return
                        else: # check if i have any more attempts
                            if controller_repeats >= controller_max_repeats:
                                container.log.debug('Cannot restart controller, stopping application.')
                                self._stop_application('Controller cannot be restarted. Something is wrong.')
                                self.status = self.STOPPED
                                return
                    else: # controller running, restart counting
                        controller_repeats = 0
                except environment.ControllerClientError as cce:
                    container.log.error(cce)
                    self._stop_application('Controller node error %s' % cce)
                    self.status = self.CRASHED
                    return

            try:
                status = self.apprunner.application_status(self.application['id'])
                stopped = []
                running = []
                crashes = []
                for stat in status:
                    if stat is False: # stopped
                        stopped.append(True)
                    elif stat is True: # running
                        running.append(True)
                    elif isinstance(stat, basestring): # crashed
                        crashes.append(stat)

                if len(running) != len(status):
                    if len(stopped) == len(status):
                        container.log.debug('Application is stopped on all machines.')
                        self.status = self.STOPPED
                        return
                    elif len(stopped) < len(status) and len(crashes) == 0:
                        container.log.debug('Application stopped on some machines, stopping it everywhere.')
                        self._stop_application('Stopped on some nodes, cleaning up.')
                        self.status = self.STOPPED
                        return
                    else:
                        container.log.debug('Application crashed somewhere, stopping it elsewhere.')
                        self._stop_application(crashes[0])
                        self.status = self.CRASHED
                        return

            except environment.AppRunnerClientError as arce:
                container.log.error('Status error:' + str(arce))
                self._stop_application(str(arce))
                self.status = self.CRASHED
                return

            time.sleep(self.REFRESH_TIME)

distributor = Distributor(EventBroadcaster())
"""
Global instance, no other instances should be created
"""