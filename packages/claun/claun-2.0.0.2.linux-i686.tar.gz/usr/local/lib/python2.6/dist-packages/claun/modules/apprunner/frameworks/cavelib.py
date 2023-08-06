import fcntl
import time
import hashlib
import os
import subprocess
from subprocess import Popen
from threading import Thread
from datetime import datetime

from claun.core import container
from claun.modules.apprunner.frameworks.abstract_framework import AbstractFramework
from claun.modules.apprunner.frameworks.abstract_framework import FrameworkError

class CaveLibFramework(AbstractFramework):
    """
    Application control for applications based on CAVELib framework (*NIX runtime).

    http://www.mechdyne.com/cavelib.aspx
    """
    def start(self, application, configuration, runtime, master):
        """
        Tries to start the application.

        This framework runner should in no way check the controller module if necessary. It should be handled by higher layers
        in the architecture.

        Might raise FrameworkError.

        If any application with the same name, configuration and parameters is tried to be run, nothing will happen (However, success will be reported).
        If the application has different configuration or parameters, old instance is stopped and a new one is launched.
        Then the configuration file is written on disk (might raise FrameworkError).
        For every application, a record is created in `self.applications` that contains:
          - crash_message - See AbstractFramework.applications_stats
          - start_time - Datetime instance containing now time.
          - configuration - same as `configuration`, it is later used when comparing other applications that are being tried to run
          - params - application['parameters'] - same as configuration
          - process - CavelibProcess instance that handles the runtime itself.

        Uses a separate log called 'cavelib'.

        :param application: CAVELib runner expects following parameters
          - id - ID of the application, it will be identified by it everywhere
          - parameters - List of parameters. Each of them is a dictionary with at least following keys:
            - default - Default value of the parameter, it is used when 'value' is not present
            - name - Name of the parameter. (If you have to pass parameters as '-p', include the dash in the name)
            - value - Current value of the parameter. Optional and if not present, the default is used.
            - processing_type - cmd|envvar|cmdnoname|cmdnospace - this tells the framework how to pass the parameters
              to the program.
              - cmd - "binary -param 12" for name='-param' and 'value'=12
              - envvar - "param=12" for name='param' and 'value'=12 (Typical environment variable)
              - cmdnoname - "binary 12" for name='-param' and 'value'=12
              - cmdnospace - "binary -param12" for name='-param' and 'value'=12
        :param configuration: String with contents of the cave.config file. It is stored using the `filestorage` and later passed only as a filename
        :param runtime: Runtime information about the application. It is a dictionary that should contain following keys:
          - binary - Absolute path to the binary file that represents the application
          - directory - Working directory for the application
          - md5sum - MD5 checksum of the binary. Optional. If present, a md5sum of the actual binary is compared to this and if it doesn't match, the application is not launched.
          - In the future, information on how to terminate/kill the application might be included.
        :param master: boolean value if this is master or not. Currently not used.
        """

        container.log.add_handler('cavelib')

        if self.is_running(application['id']):
            if self.applications[application['id']]['configuration'] == configuration and self.applications[application['id']]['params'] == application['parameters']:
                container.log.info('CAVELIB Already running %s with the same configuration and parameters' % application['id'], 'cavelib')
                return True
            else:
                container.log.info('CAVELIB Already running %s with different configuration or parameters, stopping...' % application['id'], 'cavelib')
                self.applications[application['id']]['process'].stop()
                while application['id'] in self.applications and not self.applications[application['id']]['process'].stopped():
                    time.sleep(0.5)

        hash = self.filestorage.write(configuration)
        if hash is None:
            raise FrameworkError("CAVELIB Cannot save configuration")
        configpath = self.filestorage.abspath(hash)

        self.applications[application['id']] = {
                'crash_message': None,
                'start_time': datetime.now(),
                'configuration': configuration,
                'params': application['parameters'],
                'process': CavelibProcess(self, application['id'], master, configpath, runtime, application['parameters'])
        }
        self.applications[application['id']]['process'].start()
        return True

    def stop(self, appid):
        """
        Tries to stop `appid`.

        You should call it after crash of the application to clear your self.applications if you have seen that the application has crashed.

        If appid is not present in self.applications or has already stopped, True is returned as stopping was in fact successful.
        If appid is running, a stop method of its process is called and True is returned.
        """
        if appid not in self.applications:
            return True
        app = self.applications[appid]
        if app['process'].stopped():
            self.app_stopped(appid)
            return True
        container.log.info('CAVELIB %s stopping' % appid, 'cavelib')
        app['process'].stop()
        return True

    def app_crashed(self, appid, message):
        """
        Sets the crash_message of appid to message.
        """
        if appid in self.applications:
            self.applications[appid]['crash_message'] = message

    def app_stopped(self, appid):
        """
        Removes appid from self.applications.
        """
        if appid in self.applications:
            del self.applications[appid]

    def is_running(self, appid):
        """
        Is the application running?

        Uses CavelibProcess.running()
        """
        if appid in self.applications:
            return self.applications[appid]['process'].running()
        return False

class CavelibProcess(Thread):
    """
    The thread that actually takes care of the running application.

    It can be in four states, INIT, STARTUP, RUNNING or STOPPED.
      - INIT - Instance was created, but the thread was not started.
      - STARTUP - The moment between thread start and application start.
      - RUNNING - Application is running.
      - STOPPED - Application either crashed or was stopped.
    """

    INIT = 0
    STARTUP = 1
    RUNNING = 2
    STOPPED = 3

    def __init__(self, originator, appid, master, configpath, runtime, parameters):
        """
        Sets attributes, state to INIT and might check the md5 sum of the binary.

        If the md5sum key is present in the runtime dictionary, it is checked against
        the actual binary's checksum. If it does not match, a FrameworkError is raised.

        :param originator: typically CaveLibFramework class. It is used to report app_crashed and app_stopped.
        :param appid: Application identifier
        :param master: Is this machine deemed master? Boolean.
        :param configpath: Absolute path to the configuration file.
        :param runtime: Runtime dictionary containing keys: binary, directory and optionally md5sum (see `CaveLibFramework` for details)
        :param parameters: Application parameters, see `CaveLibFramework` and its application parameter.
        """
        Thread.__init__(self)
        self.state = self.INIT
        self.daemon = True
        self.kill = False
        self.appid = appid
        self.master = master
        self.configpath = configpath
        self.runtime = runtime
        self.parameters = parameters
        self.originator = originator

        if 'md5sum' in runtime:
            if self.md5_checksum(self.runtime['binary']) != self.runtime['md5sum']:
                container.log.error('Binary md5sum mismatch for %s' % self.appid, 'cavelib')
                raise FrameworkError('Binary hash mismatch! Maybe you are running a wrong version.')

    def stop(self):
        """
        Stops the infinite loop.
        """
        self.kill = True

    def running(self):
        """
        If the instance is in state RUNNNING, it is considered as running.
        """
        return self.state == self.RUNNING

    def stopped(self):
        """
        Instance is considered stopped if it is either in state INIT or STOPPED.
        """
        return self.state == self.INIT or self.state == self.STOPPED

    def run(self):
        """
        Startup procedure.

        It assigns all parameters to binary, appends configpath as a -caveconfig argument.
        Sets DISPLAY=:0 environment variable and starts the command with working directory taken from runtime.
        After successful startup an infinite loop is created that checks if the process is still alive
        and logs its output.

        If the process stops by itself or any Exception is raised, app_crashed method is called and
        application is set to be STOPPED.

        Uses non-blocking stdout reads.
        """
        command = [self.runtime['binary']]
        conf = os.environ.copy()

        container.log.debug('CAVELIB Setting %s\'s arguments' % self.appid, 'cavelib')

        for param in self.parameters:
            value = param['value'] if 'value' in param else param['default']
            if param['processing_type'] == 'cmd':
                command.append(param['name'])
                command.append(value)
            elif param['processing_type'] == 'envvar':
                conf.update({param['name']:value})
            elif param['processing_type'] == 'cmdnoname':
                command.append(value)
            elif param['processing_type'] == 'cmdnospace':
                command.append(param['name'] + value)

        conf.update({"DISPLAY":":0"})

        command.append("-caveconfig")
        command.append(self.configpath)

        wd = self.runtime['directory']
        cmd = Popen(command, shell=False, cwd=wd,
                    env=conf, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # running
        self.proc = cmd
        self.state = self.RUNNING

        container.log.info('=' * 10 + ('CAVELIB started %s with pid %i' % (self.appid, self.proc.pid)) + '=' * 10, 'cavelib')

        fd = cmd.stdout.fileno() # stdout to nonblocking mode
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        while True:
            if self.kill:
                self._stop()
                return

            try:
                out = self.proc.stdout.read(1024)
                container.log.info('CAVELIB output: %s' % out, 'cavelib')
            except IOError as e:
                time.sleep(.5)
            except Exception as e:
                container.log.error('CAVELIB runtime exception: ' + str(e), 'cavelib')
                self.state = self.STOPPED
                self.originator.app_crashed(self.appid, 'Runtime error:' + str(e))
                return

            if self.proc.poll() is not None:
                (xout, err) = self.proc.communicate()
                container.log.error('CAVELIB Application ' + self.appid + ' unexpectedly ended: ERR: ' + err + '; OUT: ' + xout, 'cavelib')
                self.state = self.STOPPED
                self.originator.app_crashed(self.appid, 'Unexpected error, last output:' + xout.strip().split('\n')[-1])
                return

    def _stop(self):
        """
        Real stopping procedure called from the inner loop.

        Firstly tries to send terminate to the process.
        If it is not successful, sends kill.
        After stopping the application, shared memory is cleaned, state is set to STOPPED and app_stopped is called in the originator.
        """
        if self.proc:
            self.proc.terminate()
            container.log.info('CAVELIB %s <- terminate' % self.appid, 'cavelib')
            if self.proc.poll() is None:
                self.proc.kill()
                container.log.info('CAVELIB %s <- kill' % self.appid, 'cavelib')
            container.log.info('CAVELIB Cleaning shared memory', 'cavelib')
            #Popen(["""for i in `ipcs | cut -f 2 -d \ `; do ipcrm -s $i; done"""], shell=True, stdout=subprocess.PIPE) # TODO
            container.log.info('CAVELIB Application %s stopped' % self.appid, 'cavelib')
            self.state = self.STOPPED
            self.originator.app_stopped(self.appid)

    def md5_checksum(self, path):
        """
        Generates md5 checksum of the file on `path`.
        """
        fh = open(path, 'rb')
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data: break
            m.update(data)
        fh.close()
        return m.hexdigest()
