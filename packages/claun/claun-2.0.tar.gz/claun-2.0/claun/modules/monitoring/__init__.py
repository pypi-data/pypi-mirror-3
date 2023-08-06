"""
Claun module: Monitoring
========================

Description
-----------
The module can provide HW monitoring capability for a component. In given intervals it obtains some interesting values
and provides them in this module's HTTP API.

Endpoints
---------
  - /
    - GET: list all monitors
  - /{monitor-id}
    - GET: latest values

Configuration
-------------
Example section in YAML config:

monitoring:
  available: [cpu_load, mem_load, cpu_temp]

Every key represents one type of monitor. If the value is off, monitor is never initialized.

No dependencies.

Implementation details
----------------------
After startup, the intervals can not be cahnged as well, it is however possible to implement a change of interval for
every monitor using the HTTP POST method on certain monitor.
"""


from abstract_monitor import AbstractMonitor
from claun.core import container

from monitors import CpuLoadMonitor
from monitors import CpuTempMonitor
from monitors import MemoryLoadMonitor

__uri__ = 'monitoring'
__version__ = '0.2'
__author__ = 'chadijir'
__dependencies__ = []
mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/(.*)', 'MonitoringRoot'
           )

__app__ = container.web.application(mapping, locals())


class Monitoring:
    """
    Monitoring initializer can load monitors from given configuration and then provides references when requested through HTTP.
    """

    DEFAULT_INTERVAL = 2
    """
    DEFAULT_INTERVAL is the default period between checking the value.
    """


    def __init__(self, available):
        """
        Every monitor specified in config is tried to be instantiated.

        If a monitor class is found, it's thread is started.
        If no such monitor exists, it is not created.
        """
        self.monitors = {}
        for monitor in available:
            cls = self._monitor_mapper(monitor)
            if cls is not None:
                self.monitors[monitor] = cls(self.DEFAULT_INTERVAL)
                self.monitors[monitor].start()

    def get_monitor(self, monitoruri):
        """
        Checks the dictionary for a monitor with such name.

        If it does not exist, None is returned. However it should never happen.
        """
        if monitoruri not in self.monitors:
            return None
        return self.monitors[monitoruri]

    def available_monitors(self):
        """
        Returns dictionary of {monitorname: full_uri} for all monitors.

        It is used when accessing the module main endpoint.
        """
        return dict([(m.__class__.__name__, container.baseuri + __uri__ + '/' + i) for i, m in self.monitors.iteritems()])

    def _monitor_mapper(self, key):
        """
        Maps keys from configuration to concrete classes.

        :return: callable or None. None if no sufficient monitor is found, otherwise it is the appropriate class.
        """
        try:
            module = __import__('claun.modules.monitoring.monitors', globals(), locals(), [key])
            cls = getattr(module, key)
            return cls
        except AttributeError as ae:
            container.log.error(ae)
            return None

# initialize
monitoring = Monitoring(container.configuration['modules']['monitoring']['available'])

class MonitoringRoot:
    """
    Main endpoint of the module.
    """
    def GET(self, name):
        """
        Handles all requests.

        If name is empty, the main endpoint is returned (uses container.module_basic_information) and lists all available monitors.
        If name is specified, it tries to find the monitor and return last value.
        If no such monitor exists, a 404 is raised.
        """
        if name == '':
            return container.output(container.module_basic_information(__name__, __version__, monitoring.available_monitors()))
        else:
            try:
                monitor = monitoring.get_monitor(name)
                return container.output({
                                  'value': monitor.get_value(),
                                  'name': name,
                                  'description': monitor.__monitorname__,
                                  'interval': monitor.get_interval(),
                                  })
            except KeyError:
                raise container.web.notfound()
