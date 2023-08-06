from datetime import datetime

class AbstractFramework:
    """
    All Framework runners should inherit this class.
    """
    def __init__(self, filestorage):
        """
        Prepares fields and determines the self.urlname that should be used in the HTTP communication.

        self.urlname is derived from the name of the class and strips last 9 characters ('Framework') and all other characters puts in lowercase.
        For 'DummyFramework' the self.urlname is 'dummy'.

        self.applications is an important dictionary. You should save information about all running applications in it as it is
        used to serve statistics in the `applications_stats` method.

        :param filestorage: Reference to a filestorage.StorageFacade
        """
        self.configuration = None
        self.filestorage = filestorage
        self.urlname = self.__class__.__name__[:-9].lower()
        self.applications = {}

    def start(self, application, configuration, runtime, master):
        """
        Tries to start the application.

        :param application: Dictionary with information about the application. The abstract framework does not
        require any specific fields. It is framework dependent.
        :param configuration: Configuration of the framework. Typically it would be a string representation
        of the configuration file that might be later stored using the `self.filestorage`
        :param runtime: Runtime information about the application. Typically path to the binary program, it might contain
        information on how to stop the application etc.
        :param master: Boolean value determining if the machine is deemed to be the master node for
        this application. Some frameworks might behave differ for master and slave nodes. These differences
        should be resolved by the particular Framework.

        :rtype: boolean
        """
        pass

    def stop(self, appid):
        """
        Tries to stop application with given `appid`.

        It is a useful strategy to say the app was stopped even if it was never running.

        :rtype: boolean
        """
        pass

    def is_running(self, appid):
        """
        Is the `appid` currently running?
        """
        pass

    def applications_stats(self):
        """
        Returns information about applications that are/were/(even might be) run
        using this framework.

        Method uses self.applications and expects at least these fields for each application:
          - start_time - Time as a datetime instance when the application was launched. It is used to compute the
            uptime of the app.
          - crash_message - If the application is not in state 'running', currently only other state is
            recognized and that is 'crashed'. This means that if the application anyhow dies, you should
            pass some information into its crash_message field.

        The method returns another dictionary where for each application in self.applications are:
          - status - 'running'|'crashed'
          - info - uptime or crash_message

        Feel free to overwrite the method, however some other components might rely on this structure.
        """
        ret = {}
        for appname, data in self.applications.iteritems():
            uptime = (datetime.now() - data['start_time']).seconds
            ret[appname] = {}
            ret[appname]['status'] = 'running' if self.is_running(appname) else 'crashed'
            ret[appname]['info'] = uptime if ret[appname]['status'] == 'running' else data['crash_message']

        return ret



class FrameworkError(Exception): pass
