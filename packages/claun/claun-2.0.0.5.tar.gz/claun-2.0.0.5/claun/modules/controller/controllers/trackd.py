import time
import fcntl
import os
import subprocess
from threading import Thread

from claun.core import container
from claun.modules.controller.controllers.abstract_controller import AbstractController
from claun.modules.controller.controllers.abstract_controller import ControllerError

class TrackdController(AbstractController):
    """
    Controller for trackd program (*NIX platform).

    http://www.mechdyne.com/trackd.aspx

    Uses the TrackdProcess thread to control the program.
    """
    def __init__(self, filestorage):
        """
        Instantiates the TrackdProcess and kills all running instances of trackd programs if any are running.

        See TrackdProcess.running_grep and TrackdProcess.killall
        """
        AbstractController.__init__(self, filestorage)
        self.process = TrackdProcess()
        if self.process.running_grep(): # kill all during startup
            self.process.killall()

        container.log.add_handler('trackd')

    def start(self, configuration):
        """
        Starts trackd.

        If another instance is already running with the same configuration, nothing is done and True is returned.
        If the running instance has different configuration, or no trackd is running,
        the configuration is saved using the filestorage module and then
        the TrackdProcess thread is started.

        May raise ControllerError.

        :param configuration: Configuration string for trackd.
        """
        if self.is_running():
            if self.configuration == configuration:
                container.log.info('TRACKD Requesting start of running trackd with same configuration, not doing anything.', 'trackd')
                return True
            else:
                container.log.info('TRACKD Restarting with new configuration', 'trackd')
                return self.restart(configuration)

        self.configuration = configuration
        hash = self.filestorage.write(self.configuration)
        if hash is None:
            raise ControllerError("TRACKD Cannot save configuration")
        abspath = self.filestorage.abspath(hash)
        self.process.set_configpath(abspath)
        started = False
        while not started:
            try:
                self.process.start()
                started = True
            except RuntimeError as re: # we cannot run the same thread instance twice
                container.log.error(re, 'trackd')
                self.process = TrackdProcess()
                self.process.set_configpath(abspath)
        return True

    def stop(self):
        """
        Tries to stop the trackd process.

        If no trackd is running, it returns True.
        """
        if self.process.stopped():
            return True
        container.log.info('TRACKD Stopping', 'trackd')
        self.configuration = None
        self.process.stop()
        return True

    def restart(self, configuration):
        """
        Stops the process, waits for its real death and then starts it again with passed configuration.
        """
        self.stop()
        while self.is_running():
            time.sleep(0.1)
        return self.start(configuration)

    def is_running(self):
        """
        Checks if the trackd process is running.
        """
        return self.process.running()



class TrackdProcess(Thread):
    """
    Real Trackd watchdog.

    It can be in one of four states: INIT, STARTUP, RUNNING and STOPPED.

    As the trackd program can take a little longer to initialize, the STARTUP phase might be long.
    """

    #WORKING_DIRECTORY = '/usr/local/CAVE/trackd/bin'
    # Testing only, change for production
    WORKING_DIRECTORY = '/home/jirka/Projects/Diplomka/resources/trackd'
    INIT = 0
    STARTUP = 1
    RUNNING = 2
    STOPPED = 3

    def __init__(self):
        """
        Sets thread to daemon and state to INIT.
        """
        Thread.__init__(self)
        self.daemon = True
        self.state = self.INIT
        self.kill = False

    def set_configpath(self, configpath):
        """
        Set path to the configuration file.
        """
        self.configpath = configpath

    def _stop(self):
        """
        Real stopping procedure.

        Tries to terminate and then kill the real trackd process. Sets state to STOPPED.
        """
        if self.proc:
            self.proc.terminate()
            container.log.info('TRACKD <- terminate', 'trackd')
            if self.proc.poll() is None:
                self.proc.kill()
                container.log.info('TRACKD <- kill', 'trackd')
            self.state = self.STOPPED

    def stop(self):
        """
        Stops the infinite loop.
        """
        self.kill = True

    def killall(self):
        """
        Performs 'killall trackd'. Returns True if killall was successful.
        """
        cmd = subprocess.Popen(['killall', 'trackd'], shell=False)
        (out, err) = cmd.communicate()
        container.log.debug('killall trackd: %s' % out, 'trackd')
        return err == ''

    def running_grep(self):
        """
        Performs 'ps -e | grep trackd'. If no instances are found, returns False, True otherwise.
        """
        command = subprocess.Popen(['ps', '-e'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = command.communicate()
        grep = subprocess.Popen(['grep', 'trackd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (gout, err) = grep.communicate(out)
        return not gout == ''

    def running(self):
        """
        Is the process running?
        """
        return self.state == self.RUNNING

    def stopped(self):
        """
        Has the process already stopped or has not been started yet?
        """
        return self.state == self.STOPPED or self.state == self.INIT

    def run(self):
        """
        Starts the trackd process.

        Before starting, adds '/usr/lib32/libstdc++-v3' to the LD_LIBRARY_PATH.
        After starting the command, the instance gets into a STARTUP stage.

        Then an infinite loop is created that checks if the trackd is alive and
        logs the program output.
        When the '-----------------------\n' output is encountered, the trackd is
        considered ready for service and the state goes to RUNNING.

        When any Exception is encountered during the trackd execution or the process
        dies, the state is set to STOPPED and the infinite loop is broken.

        Uses non-blocking stdout read.
        """
        conf = os.environ.copy()
        conf.update({"LD_LIBRARY_PATH":"`pwd`:${LD_LIBRARY_PATH}:/usr/lib32/libstdc++-v3;"})

        try:
            cmd = subprocess.Popen(['./trackd', '-file', self.configpath], shell=False,
                        cwd=self.WORKING_DIRECTORY, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=conf)
        except Exception as e:
            container.log.error('Cannot start Trackd: %s' % e, 'trackd')

        # startup error check
        if cmd.poll() is not None:
            err = cmd.stderr.readline()
            if err != '':
                container.log.error(err, 'trackd')
            container.log.error('=' * 10 + 'TRACKD cannot start' + '=' * 10, 'trackd')
            self.state = self.STOPPED
            return
        self.state = self.STARTUP

        # running
        self.proc = cmd
        container.log.info('=' * 10 + 'TRACKD process launched with pid ' + str(self.proc.pid) + ' ' + '=' * 10, 'trackd')

        fd = self.proc.stdout.fileno() # set stdout to nonblocking read
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        while True:
            if self.kill:
                self._stop()
                return
            try:
                out = self.proc.stdout.read(1024)
                if out == '':
                    container.log.error('TRACKD runtime exception: empty out, trackd was probably killed, terminating', 'trackd')
                    self.state = self.STOPPED
                    return
                else:
                    # detect some specific output to see if its ready
                    if not out.find('-----------------------\n') == -1:
                        self.state = self.RUNNING
                        container.log.info('=' * 10 + 'TRACKD ready' + '=' * 10, 'trackd')

                container.log.info('TRACKD output: %s' % out, 'trackd')
            except IOError, e:
                time.sleep(.5)
            except Exception, e:
                container.log.error('TRACKD runtime exception:' + str(e), 'trackd')
                self.state = self.STOPPED
                return

            if self.proc.poll() is not None:
                (out, err) = self.proc.communicate()
                container.log.error('TRACKD unexpectedly ended: ERR: ' + err + '; OUT: ' + out, 'trackd')
                self.state = self.STOPPED
                return
