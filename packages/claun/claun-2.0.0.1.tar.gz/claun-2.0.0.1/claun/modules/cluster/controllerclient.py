from claun.core import container

__all__ = ['ControllerClient', 'ControllerClientError']

class ControllerClientError(Exception): pass

class ControllerClient:
    """
    This class communicates with the claun.modules.controller module that can be installed on some cluster nodes.

    It is always assigned to one certain node.
    """
    def __init__(self, computer, httpclient):
        """
        Initializing of data structures.

        :param computer: Node that this instance will take care of.
        :param httpclient: claun.core.communication.client.HttpClient instance.
        """
        self.computer = computer
        self.client = httpclient

    def _available(self):
        """
        Checks instant availability/reachability of self.computer via its 'reachable' attribute.

        If computer is not reachable or does not provide controller module,
        a ControllerClientError is raised.
        """
        if not self.computer['reachable']:
            raise ControllerClientError('Unreachable node.')
        if 'controller' not in self.computer['root']['available_modules']:
            raise ControllerClientError('Missing controller module.')

    def _endpoint(self, name):
        """
        Contacts the node and tries to get an enpoints related to controller `name`.

        If the controller is not supported on the target machine, a ControllerClientError is raised.
        Otherwise link to `name` detail is returned.

        Uses `_available` method.
        """
        self._available()
        all = self.client.request(address=self.computer['root']['available_modules']['controller'])[1]['endpoints']
        if name not in all:
            raise ControllerClientError('Unsupported controller type')
        return all[name]


    def status(self, name):
        """
        Contact the `name`'s endpoint contents.

        Uses _status method.

        If the node's unreachable, None is returned.
        """
        try:
            return self._status(name)['contents']
        except container.errors.ClientException as ce:
            container.log.error("Cannot reach client %s:%i - %s" % (self.computer['data']['fqdn'], self.computer['data']['port'], ce))
            return None

    def _status(self, name):
        """
        Returns {'endpoint': url, 'contents': contents} of the `name` endpoint.

        To get `name` endpoint's address, uses self._endpoint method.
        Does not catch ClientException.
        """
        endpoint = self._endpoint(name)
        return {'endpoint': endpoint, 'contents': self.client.request(address=endpoint)[1]}

    def _process(self, name, action, configuration=''):
        """
        Sends request to `name` to do `action`.

        Returns True or parsed contents of the error response body.

        :param name: Name of the controller
        :param action: Action to perform. Supported are currently stop, start, restart. However when calling their value obtained
        from the endpoint contents is used.
        :param configuration: It should be serializable and is transported in the HTTP body under the configuration key. Only mandatory for start and restart actions.
        """
        if action not in ['start', 'stop', 'restart']:
            raise ControllerClientError('Unsupported action')

        try:
            address, status = self._status(name).values()
            if action == 'stop':
                body = container.output({'action': status['actions']['stop']}, header=container.output.default)
            else:
                body = container.output({'configuration': configuration, 'action': status['actions'][action]}, header=container.output.default)
            self.client.request(address=address, body=body, method=container.http_methods.PUT) # 202 is deemed successful
            return True
        except container.errors.ClientException as ce: # other codes than 200
            if ce.response is not None and ce.response[0]['status'] == '202':
                return True
            container.log.error("Cannot reach client %s:%i - %s" % (self.computer['data']['fqdn'], self.computer['data']['port'], ce))
            if ce.response is not None:
                return ce.response[1]
            else:
                return str(ce)



    def start(self, name, configuration):
        """
        Tries to start the `name` controller with `configuration`.

        It is not guaranteed, that the call will affect anything, as there already might be a running instance.

        Uses self._process method.
        """
        return self._process(name, 'start', configuration)


    def restart(self, name, configuration):
        """
        Tries to restart the `name` controller with `configuration`.

        In contrast to start method, when using the restart, it is guaranteed, that the target node will stop and start
        the controller program again.

        Uses self._process method.
        """
        return self._process(name, 'restart', configuration)

    def stop(self, name):
        """
        Tries to stop the `name` controller.

        Uses self._process method.
        """
        return self._process(name, 'stop')
