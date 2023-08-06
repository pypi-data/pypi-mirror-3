"""
Module defines an abstract class its successors can monitor some HW characteristics.

Current implementation provides storage space for only one value. It is possible to keep a queue
or some other data structure of measured values.
"""
import time
from abc import abstractmethod
from threading import Thread

from claun.core import container

__docformat__ = 'restructuredtext en'

class AbstractMonitor(Thread):
    """
    Abstract class that repeats one task that gathers some interesting value and stores it.

    This implementation can hold only one value at a time.

    Every subclass should override following methods:
      - __init__ - every monitor has to pass a unique name
      - _find_value - the 'magic' method that gets the monitored value (using some system call or whatever suits the needs)
    For example subclasses, see monitors module.

    Monitor provides methods how to pause and resume the monitoring of the characteristic.
    """

    def __init__(self, name, interval=-1):
        """
        Initializes name and interval and identifies the thread as a daemon.

        :param interval: when set to -1, no measuring is done, otherwise it sets the interval between checking the values (in seconds).
        """
        Thread.__init__(self)
        self.name = name
        self.interval = interval
        self.stop = False
        self.pause = False
        self.last_value = None
        self.daemon = True

    def set_interval(self, interval):
        """
        Updates the interval. Only integers greater than 0 are allowed.
        """
        if int(interval) < 0:
            return
        self.interval = int(interval)

    def get_interval(self):
        return self.interval

    def pause(self):
        """
        Pauses the monitor.

        The thread remains alive, but the measuring is not performed.
        """
        container.log.info("Monitoring '%s' paused" % (self.name))
        self.pause = True

    def resume(self):
        """
        Resumes the monitor.

        If not paused, nothing happens.
        """
        container.log.info("Monitoring '%s' paused" % (self.name))
        self.pause = False

    @abstractmethod
    def _find_value(self):
        """
        Here happens the magic. Has to be overriden by particular monitor.
        Return value is any sort of value that we found out.
        """
        return '-1'

    def get_value(self):
        """
        Returns the last gathered value.
        """
        return self.last_value

    def stop(self):
        """
        The thread is killed and can not be re-animated.
        """
        self.stop = True

    def run(self):
        """
        Thread is kept alive by an infinite loop (can be broken by invoking stop method).

        After self.interval seconds, a _find_value method is invoked anf returned value is stored.
        If any Exception occurs during obtaining the value, the monitor is stopped to save
        system resources.
        """
        while not self.stop:
            try:
                if self.interval != -1 or self.pause:
                    self.last_value = self._find_value()
                    time.sleep(self.interval)
            except Exception, e:
                container.log.error("Monitoring error in '%s': %s" % (self.name, e.__repr__()))
                container.log.info("Quitting monitor %s" % self.name)
                break
