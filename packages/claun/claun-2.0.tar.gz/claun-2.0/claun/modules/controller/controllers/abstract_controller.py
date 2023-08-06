import hashlib

class AbstractController:
    """
    Predecessor for all controller programs.

    self.urlname - short name that is to be used in URL, it is derived from the class name and takes the part
    before 'Controller' and puts it in lowercase (for class DummyController it is dummy)
    """
    def __init__(self, filestorage):
        """
        Only initializes fields.

        :param filestorage: Reference to a filestorage.StorageFacade
        """
        self.configuration = None
        self.filestorage = filestorage
        self.urlname = self.__class__.__name__[:-10].lower()

    def start(self, configuration):
        """
        Tries to start the controller's program.

        Controller specific, this abstract implementation only assigns the configuration.
        Start called with different configuration does not guarantee any effect.

        :rtype: boolean
        """
        pass

    def stop(self):
        """
        Tries to stop the controller's program.

        Controller-specific.

        :rtype: boolean
        """
        pass

    def restart(self, configuration):
        """
        Tries to restart the controller's program with a new passed configuration.

        Restart guarantees, that the controller will stop and start again.

        Controller-specific.

        :rtype: boolean
        """
        pass

    def is_running(self):
        """
        Is the controller's program running?

        :rtype: boolean
        """
        pass

    def configuration_hash(self):
        """
        Returns md5 hash of configuration that is being used, or None if the controller is not running, or the configuration is not set.
        """
        if self.is_running() and self.configuration is not None:
            return hashlib.md5(self.configuration).hexdigest()
        return None

class ControllerError(Exception): pass
