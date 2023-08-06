
from claun.core import container

__all__ = ['AppRunnerClient', 'AppRunnerClientError']

class AppRunnerClientError(Exception): pass

class AppRunnerClient:
    """
    Client for the apprunner module that is used to run applications on multiple nodes.

    It is not designated to one computer, but handles the whole cluster.
    """
    def __init__(self, computers, httpclient):
        """
        Assigns fields and prepares internal structures.

        self.running keeps track of what application runs on what machines, for example {'app': {node1: StatusURI1, node2: StatusURI2...}}

        :param computers: ClusterClient.computers.
        :param httpclient: claun.core.communication.client.HttpClient instance.
        """
        self.computers = computers
        self.client = httpclient
        self.running = {} # what runs where

    def start(self, mastername, computerconfigs, application, runtime):
        """
        Tries to start application on all nodes for which is available a configuration.

        A request to start the application on all nodes is performed, only status codes 200 or 202 are
        considered successful. If a startup fails on some node, a rollback is performed in
        which the application is stopped on nodes that succeeded in starting it in the first place.
        To stop applications, uses the _stop method.

        If some framework needs to be run only on a master machine, the apprunner module on the
        destination nodes should take care of it.

        May raise AppRunnerClientError if the rollback is not successful.

        :param mastername: hostname of the master node
        :param computerconfigs: Dictionary where each key is a node and its value is its configuration string
        :param application: Application, that is to be run. See the documentation of the applications module as it is recommended to use the same structure here.
        :param runtime: Runtime attributes for given application and used platform.
        """
        started = {}

        endpoints = self._check_and_get_framework(computerconfigs.keys(), application['framework']['name'])

        for node, config in computerconfigs.iteritems():
            try:
                data = container.output({'configuration': config,
                                  'master': mastername == node,
                                  'runtime': runtime,
                                  'application': application,
                                  'action': endpoints[node]['contents']['actions']['start']},
                                  header=container.output.default)
                self.client.request(address=endpoints[node]['endpoint'], body=data, method=container.http_methods.PUT)
                started[node] = True
            except container.errors.ClientException as ce:
                if ce.response is not None and ce.response[0]['status'] == '202':
                    started[node] = True
                else:
                    container.log.debug(ce.response[1])
                    started[node] = False

        if all(started.values()): # all was ok, application is starting/running on all nodes
            self.running[application['id']] = dict([(node, endpoints[node]['endpoint']) for node in computerconfigs.keys()])
            container.log.debug('Application startup OK')
            return True
        else: # turn off app where it has started
            container.log.debug('Application startup messed up')
            for node, stat in started.iteritems():
                try:
                    if stat: self._stop(application, node)
                except AppRunnerClientError:
                    raise AppRunnerClientError('Startup messed up, some nodes were not successfully launched and some are not turned off. Inconsistency.')
            if application['id'] in self.running:
                del self.running[application['id']]
            raise AppRunnerClientError('Application was not started on some nodes. Cluster was cleaned, but the application is not running.')

    def _stop(self, application, node):
        """
        Tries to stop `application` on `node`.

        Only 200 or 202 are considered a success.
        If the stopping fails, AppRunnerClientError is raised.

        :param application: Whole application dictionary as is passed for example to the start method.
        :param node: Hostname of the node.
        """
        try:
            container.log.debug('Stopping %s on %s' % (application['id'], node))
            status = self._check_and_get_framework([node], application['framework']['name'])[node]
            endpoint = status['endpoint']
            contents = status['contents']
            data = container.output({'action': contents['actions']['stop'], 'application_id': application['id']}, header=container.output.default)
            self.client.request(address=endpoint, body=data, method=container.http_methods.PUT)
            return True
        except container.errors.ClientException as ce:
            if ce.response is not None and ce.response[0]['status'] == '202':
                return True
            container.log.error('Cannot stop %s on %s: %s' % (application['id'], node, ce))
            raise AppRunnerClientError('Cannot stop %s on %s: %s' % (application['id'], node, str(ce)))

    def stop(self, application):
        """
        Tries to stop `application` on all nodes using the _stop method for all involved nodes.

        If the application was not launched by the instance where you are calling the stop method, stop won't be successful and AppRunnerClientError will be raised.
        If stopping is successful, returns True.
        """
        status = {}
        if application['id'] not in self.running:
            raise AppRunnerClientError('"%s" was not launched through this server, cannot stop from here.' % application['id'])
        for node in self.running[application['id']]:
            try:
                self._stop(application, node)
                status[node] = True
            except AppRunnerClientError:
                status[node] = False
        if all(status.values()):
            if application['id'] in self.running:
                del self.running[application['id']]
            return True
        else:
            raise AppRunnerClientError('Cannot stop "%s" on all nodes, problem with "%s"' % (application['id'], ', '.join([n for n, v in status.iteritems() if not v])))

    def _available(self, nodename):
        """
        Checks if the `nodename` is reachable by network and contains the `apprunner` module.
        """
        if nodename not in self.computers:
            raise AppRunnerClientError('Unknown node "%s".' % nodename)
        if not self.computers[nodename]['reachable']:
            raise AppRunnerClientError('Unreachable node "%s".' % nodename)
        if 'apprunner' not in self.computers[nodename]['root']['available_modules']:
            raise AppRunnerClientError('Missing apprunner module on "%s".' % nodename)

    def _frameworks(self, nodename):
        """
        Returns names and endpoints for all frameworks supported by the `nodename`.

        Uses _available.
        """
        self._available(nodename)
        all = self.client.request(address=self.computers[nodename]['root']['available_modules']['apprunner'])[1]['endpoints']
        return all

    def application_status(self, appid):
        """
        Returns status of the supposedly running `appid`.

        For every node an appropriate endpoint is contacted and if the application is in
        the content of the endpoint and its status is 'running', it is considered running.
        If an application is running on all nodes, True is returned.

        If the application is not in self.running, an AppRunnerClientError is raised.
        If the application is not running on even one node, an AppRunnerClientError is raised.
        If some node is unreachable, an AppRunnerClientError is raised.
        """
        if appid not in self.running:
            raise AppRunnerClientError("No such application.")
        try:
            ret = {}
            for node, endpoint in self.running[appid].iteritems():
                status = self.client.request(address=endpoint)[1]['applications']
                if appid in status:
                    if status[appid]['status'] == 'running':
                        ret[node] = True
                    elif status[appid]['status'] == 'crashed':
                        ret[node] = status[appid]['info']
                else:
                    ret[node] = False
            return ret.values()
        except container.errors.ClientException as ce:
            container.log.error(ce)
            raise AppRunnerClientError('Problem encountered: %s' % ce.response)

    def _endpoint_contents(self, endpoint):
        """
        Returns {endpoint: address, contents: contentsoftheendpoints}.
        """
        return {'endpoint': endpoint, 'contents': self.client.request(address=endpoint)[1]}

    def _check_and_get_framework(self, nodes, frameworkname):
        """
        Returns contents of endpoints for a given `frameworkname` on all nodes.

        If some node does not support the framework, an AppRunnerClientError is raised.
        :return: Dictionary where each node gets the return value of _endpoint_contents.
        """
        frameworks = {}
        for nodename in nodes:
            result = self._frameworks(nodename)
            if frameworkname not in result.keys():
                raise AppRunnerClientError('Node "%s" does not support framework %s' % (nodename, frameworkname))
            else:
                frameworks[nodename] = self._endpoint_contents(result[frameworkname])
        return frameworks
