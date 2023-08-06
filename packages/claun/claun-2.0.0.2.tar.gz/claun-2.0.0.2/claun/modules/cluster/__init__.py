"""
Claun module: Cluster
=====================

Description
-----------

Client for another components running the Claun system. Typical usage is on the central server where we want to control other components.
It does not offer any endpoints and should be used by other modules to access the computers in the cluster.

The module itself in no way discovers any computers, the list of them must be given to this module during initialization.

After getting the list of computers, a polling thread is started that checks in a given interval all nodes if they are alive.
In addition, every node gets a ControllerClient instance.

TODO create hwcontrol and monitoring as separate clients (as is for example apprunner)

Configuration
-------------
No configuration options.

No dependencies.

Endpoints
---------
No public endpoints.

Implementation details
----------------------
Listing of available information in ClusterClient.enhance_one method is hard-coded and should be probably changed in the future.
However the boundaries are so tight here, that it might be better to edit the code than introduce some configuration
variables etc.

List of computers provided from the client class is a must to keep this module as independent as possible.

"""

import time
from threading import Thread

from claun.core import container

from claun.modules.cluster.controllerclient import ControllerClient
from claun.modules.cluster.controllerclient import ControllerClientError
from claun.modules.cluster.apprunnerclient import AppRunnerClient
from claun.modules.cluster.apprunnerclient import AppRunnerClientError

__uri__ = 'cluster'
__version__ = '0.2'
__author__ = 'chadijir'
__dependencies__ = []

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/(.*)', 'ClusterRoot'
           )

__app__ = container.web.application(mapping, locals())
__docformat__ = 'restructuredtext en'
__all__ = ['ClusterRoot', 'ClusterClient', 'ClusterClientError', 'ControllerClient', 'ControllerClientError', 'AppRunnerClient', 'AppRunnerClientError']


### Endpoints

class ClusterRoot:
    """
    Root endpoint that offers nothing more than a basic functionality.

    All requests will fall back here.
    """
    def GET(self, name):
        return container.output(container.module_basic_information(__name__, __version__, {}))

### Classes

class PollNodes(Thread):

    REFRESH_TIME = 5
    """
    Simple thread checking nodes in a cluster in a certain interval.
    """
    def __init__(self, originator):
        """
        Init thread and set it as a daemon

        :param originator: Parent object holding the reference to the computers collection.
        """
        Thread.__init__(self)
        self.originator = originator
        self.daemon = True

    def run(self):
        """
        Infinite loop that checks root endpoints of all nodes in originator.computers.

        Uses refresh method.
        """
        while(True):
            self.refresh()
            time.sleep(self.REFRESH_TIME)

    def refresh(self):
        """
        Check all computers.

        The goal of this is to keep fresh information about node's available modules.
        The method fills reachable and root fields in the original dictionary.
        """
        for name, computer in self.originator.computers.iteritems():
            try:
                try:
                    self.originator.computers[name]['root'] = container.client.request(computer['data']['fqdn'], computer['data']['port'], '/')[1]
                    self.originator.computers[name]['reachable'] = True
                except container.errors.ClientException as ce:
                    container.log.debug("Cannot reach client %s:%i - %s" % (computer['data']['fqdn'], computer['data']['port'], ce))
                    self.originator.computers[name]['reachable'] = False
                    self.originator.computers[name]['root'] = {}
                except AttributeError: # socket missed
                    pass
            except KeyError: # concurrent modification
                pass


class ClusterClientError(Exception): pass


class ClusterClient:
    """
    Besides providing information about all computers (see __init__ and enhance methods),
    this class provides an instance of AppRunnerClient that can be used to start/stop applications in
    the cluster. It is accessible through `apprunner` field.
    """

    def __init__(self):
        """
        Starts the polling thread.

        :param computers: dictionary with this required values {'computername': {'fqdn': '..', 'port': '..'}}
        """
        self.computers = {}
        self.polling = PollNodes(self)
        self.polling.start()

    def set_computers(self, computers, instant_refresh=False):
        """
        Stores passed computers in a class field.

        AppRunner instance is created as well.

        Every computer is then represented as a dictionary, where the originally passed
        data is stored under 'data' key. Other keys are:
          - root - Contents of the root endpoint. It is refreshed periodically by PollNodes isntance
          - reachable - If the node is currently alive.
          - controller - Instance of ControllerClient for this computer

        :param computers: dictionary with this required values {'computername': {'fqdn': '..', 'port': '..'}}
        :param instant_refresh: If True, the polling thread's refresh method is called immediately (And it may take long time). Optional, default False.
        """
        self.computers = {}
        for name, value in computers.iteritems():
            self.computers[name] = {}
            self.computers[name]['data'] = value
            self.computers[name]['root'] = {}
            self.computers[name]['reachable'] = False
            self.computers[name]['controller'] = ControllerClient(self.computers[name], container.client)
        self.apprunner = AppRunnerClient(self.computers, container.client)
        if instant_refresh:
            self.polling.refresh()


    def enhance(self):
        """
        Add information available only remotely to self.computers dictionary.

        Calls enhance_one for all computers in self.computers.

        Returns dictionary in a format similar passed to the __init__ method.
        """
        for cname, computer in self.computers.iteritems():
            self.computers[cname] = self._enhance_one(computer)
        return dict([(cname, c['data']) for cname, c in self.computers.iteritems()])

    def _enhance_one(self, computer):
        """
        Adds information available only on the remote node.

        Currently only Monitoring and HWControl modules are contacted. For Monitoring, all monitors' current
        values are listed and for HWControl all possible actions are listed.

        If available, a 'platform' key is added.

        To sum it up, for each computer are added these fields to the original dictionary:
          - online - true|false if the given computer is reachable
          - hwcontrol - list of possible HWControl commands. Explicit URIs are not listed to make sure that the command will be delegated through the server
          - monitors - dictionary where there is a record for every available monitor on the destination computer

        :param computer: dictionary containing information about the computer
        """
        computer['data']['online'] = False
        computer['data']['monitors'] = {}
        if 'platform' in computer['data']: del computer['data']['platform']
        if computer['reachable'] is True:
            try:
                computer['data']['online'] = True
                if 'monitoring' in computer['root']['available_modules']:
                    monitors = container.client.request(address=computer['root']['available_modules']['monitoring'])[1]['endpoints']
                    for name, address in monitors.iteritems():
                        monitor = container.client.request(address=address)[1]
                        computer['data']['monitors'][name] = {'value': monitor['value'], 'description': monitor['description']}
                if 'hwcontrol' in computer['root']['available_modules']:
                    computer['data']['hwcontrol'] = container.client.request(address=computer['root']['available_modules']['hwcontrol'])[1]['endpoints'].keys()
                if 'platform' in computer['root']:
                    computer['data']['platform'] = computer['root']['platform']

            except container.errors.ClientException as ce:
                container.log.debug("Cannot reach client %s:%i - %s" % (computer['data']['fqdn'], computer['data']['port'], ce))
        return computer


    def get_one(self, name):
        """
        Returns one computer with given name or None.

        Method invokes enhance_one method.
        """
        if name in self.computers:
            self.computers[name] = self._enhance_one(self.computers[name])
            return self.computers[name]['data']
        return None

    def controller(self, name):
        return self.computers[name]['controller'] if name in self.computers else None

    def hwcontrol(self, name, action): # rename
        """
        Delegates certain HW action to a remote computer with given name.

        TODO create as a separate client (like apprunnerclient)

        ClusterClientError may be raised if there's no such computer or the computer is unreachable.

        Currently the 'boot' action is hardcoded here (and does nothing) as its implementation is **very** specific.
        Other actions are delegated to the appropriate computer. If the action is allowed there,
        it is performed. ClusterClientError will be raised if the computer is unreachable, or the action is invalid.
        The success of 'shutdown' and 'reboot' action is determined by a very simple condition presuming that
        the HTTP request will not get any response. However if the request is not successful, we are not able to check
        the real state of the destination computer.

        :param name: computer name (as given as a key in the initial computers dictionary)
        :param action: action name
        """
        if name not in self.computers:
            raise ClusterClientError("No such computer")

        if action == 'boot': # no HTTP method, delegate to ipmi, wol or something else TODO
            return True

        computer = self.computers[name]

        if computer['reachable'] is False:
            raise ClusterClientError("Computer is currently unreachable")

        try: # list actions
            actions = container.client.request(address=computer['root']['available_modules']['hwcontrol'])[1]['endpoints']
        except ClientException as ce:
            container.log.error("Cannot access computer: %s" % ce)
            raise ClusterClientError("Cannot access computer: %s" % ce)

        if action not in actions.keys(): # invalid action
            container.log.error("Invalid action %s" % action)
            raise ClusterClientError("Invalid action")
        else:
            try: # try to send action
                container.client.request(address=actions[action])
            except ClientException as ce: # what happens? no response? depends on the action
                container.log.error("Error during action request: %s" % ce)
                if action == 'shutdown' or action == 'reboot':
                    return True
                else:
                    return False
        return True


clusterclient = ClusterClient()