"""
Claun module: Environment
=========================

Description
-----------
The Environment module holds information about the computers in the cluster and the parameters of the environment.

It provides two main endpoints:
  1. cluster
     Provides information about computers forming the cluster.
  2. configuration
     Provides information about parameters for the overall configuration of CAVE. Parameters are editable.

As the module uses the users module, the configuration can be (and is) personalized. This means that if a user
customizes the configuration, the parameters are stored in-memory and are available until the restart of this component.

Information about the cluster is stored in the couchdb that is accessed through environment.model module.
However not all information should be stored in the database, so environment module uses cluster module to
enhance the information about computers by accessing those directly via HTTP.

Example couchdb documents can be found in the configuration.json and computer.json files attached to this module.

Please, pay attention to the type attribute of both documents, it is important.

Every parameter written in the **configuration** document, can have these fields:
  - name - name of the parameter for the application, it can be used later when creating some configuration files.
  - human_name - Name for the user, like 'Distance from user' or 'Stereo?'
  - type - dropdown|boolean|slider - or other, this field should tell clients how to render the field when the user can edit it
    - values - specific for dropdown, this is a list of values from which can the user select (mandatory)
    - min - specific for slider, minimal selectable value (mandatory)
    - max - specific for slider, maximal selectable value (mandatory)
  - default - default value for this parameter, it is pre-selected when presenting to the user
  - help - some helpful text that can explain what the parameter does
  - user_editable - whether a user can edit the parameter; you may want some parameters to be fixed to some value
  - group - special property, like "projection"; it is useful when you want to render some parameters differently,
    you may use this attribute to group them together

In current implementation, every computer has its own document in the couchdb and can have these properties:
  - hostname - short name of the host
  - id - Unique identification that is used in URI.
  - connected - if the computer is currently connected to the cluster. This might be useful when you are changing the infrastructure.
  - ip - IP address
  - port - port where the claun component is listening
  - platforms - List of all platforms available on this node. The actual platform should be specified in the appropriate configuration file.
  - masterpriority - For some processes, the computers have to have one master machine, this sets the order in which the computers
    will be chosen as the master machine. (If the computer with masterpriority 1 is offline, the computer with masterpriority 2 becomes the master)
  - fqdn - Fully Qualified Domain Name is used when contacting the computers through HTTP
  - projections - Very CAVE specific property telling us which projections does this computer handle.
    It is a hash where the key is the name of the projection (it is handy to have the same name as in the configuration document) and the
    value is another hash usually with these possible parameters:
    - xmax - maximum position on the X-axis
    - xmin - minimum position on the X-axis
    - ymin - minimum position on the Y-axis
    - ymax - maximum position on the Y-axis
    - xscreen - Particular X screen where the projection is presented.

Of course it is possible to add many more attributes to every part of these documents. Attributes listed here are used in the
current implementation for CAVE and without them, it is highly probable that the system will break down.

If you will be implementing the system for other platform (e. g. Windows), it is probable that you will have to provide different
set of attributes for projections and/or parameters.

When you update the appropriate map function, you can brake the configuration parameters into separate documents, or merge
computers into one document. For particular implementation notes, see the model module.

Endpoints
---------
All endpoints are restricted to group all.

  - /cluster
    - GET: List all nodes in a cluster with details
    - PUT: Do some action, supports only reload at the time
  - /cluster/{node-id}/
    - GET: List info about node-id
  - /cluster/{node-id}/{action}
    - GET: Perform action on the node-id (It would be nice to re-implement it in a more RESTful way)
  - /configuration
    - GET: List all parameters
  - /configuration/{parameter-id}
    - GET: List parameter
    - PUT: Set parameter's value

Configuration
-------------
db_name: somename - name of the database in couchdb where the information is stored

Depends on couchdb, users and cluster modules.

Implementation details
----------------------
This is CAVE-specific implementation.

Adding computers to the database during the runtime of the component  is not immediately reflected. You have to explicitly call
the reload action.

On the other hand, parameters are handled dynamically, so feel free to update/add them on the fly, the changes will be reflected
during the next request.

"""
from claun.core import container

from claun.modules.environment.admin import __app__ as adminapp
from claun.modules.environment import model

from claun.modules.cluster import clusterclient
from claun.modules.cluster import ClusterClientError
from claun.modules.cluster.apprunnerclient import AppRunnerClientError
from claun.modules.cluster.controllerclient import ControllerClientError

from claun.modules.users import personalize
from claun.modules.users import restrict

__uri__ = 'environment'
__version__ = '0.1'
__author__ = 'chadijir'
__dependencies__ = ['couchdb', 'users', 'cluster']

uris = {}
uris['cluster'] = '/cluster'
uris['config'] = '/configuration'

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/admin', adminapp,
           uris['cluster'], 'ClusterInfo',
           uris['cluster'] + '/(.*)/(.*)', 'ClusterDetail',
           uris['cluster'] + '/(.*)', 'ClusterDetail',
           uris['config'], 'Configuration',
           uris['config'] + '/(.*)', 'Parameter',
           '/', 'Root'
           )

__app__ = container.web.application(mapping, locals())

class Root:
    """
    Provides basic information.
    """
    def GET(self):
        return container.output(container.module_basic_information(__name__, __version__, {
                          'cluster': container.baseuri + __uri__ + uris['cluster'],
                          'configuration': container.baseuri + __uri__ + uris['config'],
                          }))

clusterclient.set_computers(dict([(comp.key, comp.value) for comp in model.all_computers()]))
"""
Cluster client instance. Retrieves data from database only during startup, not dynamically.
"""

def _transform(name, value, notallowed=[]):
    """
    Transforms computer of `name`'s `value` to contain a key 'actions' and provides links to available actions from key 'hwcontrol'.

    If the key 'online' is False, a 'boot' action is added into the attribute 'actions'
    """
    value['actions'] = {}
    if 'hwcontrol' in value:
        for m in value['hwcontrol']:
            value['actions'][m] = container.baseuri + __uri__ + uris['cluster'] + '/' + name + '/' + m
        del value['hwcontrol']
    if not value['online']:
        value['actions']['boot'] = container.baseuri + __uri__ + uris['cluster'] + '/' + name + '/boot'

    for n in notallowed:
        if n in value: del value[n]

    return value



class ClusterInfo:
    """
    Displays information about cluster using the 'clusterclient' instance.
    """
    def GET(self):
        """
        Main endpoint.

        List of computers is obtained from clusterclient instance and
        then URIs for hwcontrol actions are generated. If the computer is not deemed
        online, an URI for boot is generated.

        Generated URIs lead again to this module, particularly to the ClusterDetail class.
        >>> http://server.example.com:3400/environment/cluster/computer-id/action-name
        """
        computers = clusterclient.enhance()
        for k, v in computers.iteritems():
            computers[k] = _transform(k, v, ['_id', '_rev'])

        return container.output(computers.values())

    def PUT(self):
        """
        Do something with the computer list, currently supports only reload.

        If an incoming request contains key action with value reload, a
        `clusterclient` is re-initialized with fresh
        data from database. The new list is immediately checked via network,
        so processing this request might take longer time.
        """
        try:
            contents = container.input(container.web.data())
            if 'action' in contents and contents['action'] == 'reload':
                clusterclient.set_computers(dict([(comp.key, comp.value) for comp in model.all_computers()]), True)
                return container.output({'status': 'ok'})
            else:
                return container.web.badrequest()
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()



class ClusterDetail:
    """
    Handles information about one node in the cluster. Restricted endpoint (group 'all').
    """
    @restrict('all')
    def GET(self, computername, action=None, user=None):
        """
        Provides information about a node in the cluster or delegates given action.

        As this method may be potentially dangerous, it is user-protected.

        If no action is specified, only information about the node with computername is displayed.
        The output is the same as in the ClusterInfo class.

        If a computer with such name does not exist, 404 is returned.
        If a remote action is successfully invoked, a 200 is returned, Bad request otherwise.
        If a problem with requesting the node occurs, a 500 Internal Error is returned.
        """
        computer = model.computer_by_id(computername)
        if computer is None: # non existing computer
            raise container.web.notfound()

        if action is None: # no action, return detail
            computer = clusterclient.get_one(computername)
            return container.output(_transform(computername, computer, ['_id', '_rev']))

        try: # delegation
            if clusterclient.hwcontrol(computername, action):
                return container.output({'status': 'In progress...'})
            else:
                raise container.web.badrequest()
        except ClusterClientError as cce:
            raise container.web.internalerror('There was a problem with your request: %s' % cce)

class Configuration:
    """
    Public, but personalized environment configuration.
    """
    @personalize
    def GET(self, user=None):
        """See model.configuration method for details."""
        return container.output(model.configuration(user))

class Parameter:
    """
    Parameter detail. Restricted endpoint (group 'all').
    """
    @restrict('all')
    def GET(self, name, user=None):
        """
        Provides detail about parameter with given name.

        Delegated to model.parameter. If no such parameter exists, 404 is returned.
        """
        parameter = model.parameter(user, name)
        if parameter is None:
            raise container.web.notfound()

        return container.output(parameter.value)

    @restrict('all')
    def PUT(self, name, user=None):
        """
        Updates given parameter.

        Delegated to model.save_parameter. If call is successful, 200, 404 otherwise.
        """
        if model.save_parameter(user, container.input(container.web.data())):
            return container.output({'status': 'OK'})
        else:
            raise container.web.notfound()
