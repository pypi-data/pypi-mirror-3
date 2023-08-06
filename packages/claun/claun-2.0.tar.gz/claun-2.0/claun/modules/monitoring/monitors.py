# -*- coding: utf-8 -*-
"""
Particular monitors should be coded here or in a separate module.
"""
import subprocess

from claun.core import container
from claun.modules.monitoring.abstract_monitor import AbstractMonitor

class CpuLoadMonitor(AbstractMonitor):
    """
    Monitors CPU load as seen for example in 'top'.

    An average load for last 15 minutes is returned.
    """
    __monitorname__ = 'Average load'

    def __init__(self, interval=-1):
        AbstractMonitor.__init__(self, self.__monitorname__, interval)

    def _find_value(self):
        """
        uptime | tr -s ' ' | cut -f11 -d' '

        The implementation may differ on certain architectures, so test carefully.
        """
        try:
            load = subprocess.Popen("uptime | tr -s ' ' | cut -f11 -d' '", stdout=subprocess.PIPE, shell=True)
            out = load.communicate()[0]
            loadnum = out.split(',')[0] if ',' in out else out
            return loadnum.rstrip('\n')
        except Exception, e:
            container.log.error("CPU load error: '%s'" % e.__repr__())
            return 'N/A'

class MemoryLoadMonitor(AbstractMonitor):
    """
    Monitors RAM usage as seen in top.

    Returns the total amount of occupied memory (considering cache/buffer space as free) in percents.
    """
    __monitorname__ = 'Memory usage'

    def __init__(self, interval=-1):
        AbstractMonitor.__init__(self, self.__monitorname__, interval)

    def _find_value(self):
        """
        total memory: free -m | tr -s ' ' | grep Mem: | cut -d' ' -f2
        occupied memory: free -m | tr -s ' ' | grep '+' | cut -d' ' -f3

        Conversion to percents is done in python.
        """
        try:
            totalmemval = subprocess.Popen("free -m | tr -s ' ' | grep Mem: | cut -d' ' -f2", stdout=subprocess.PIPE, shell=True)
            usedmemval = subprocess.Popen("free -m | tr -s ' ' | grep '+' | cut -d' ' -f3", stdout=subprocess.PIPE, shell=True)

            total = totalmemval.communicate()[0]
            used = usedmemval.communicate()[0]

            return str(100 * float((float(used)) / float(total))).split('.')[0] + '%'
        except Exception, e:
            container.log.error("Memory load error: '%s'" % e.__repr__())
            return 'N/A'

class CpuTempMonitor(AbstractMonitor):
    """
    Monitors CPU temperature. Requires acpi.
    """
    __monitorname__ = 'CPU temperature'

    def __init__(self, interval=-1):
        AbstractMonitor.__init__(self, self.__monitorname__, interval)

    def _find_value(self):
        """
        acpi -t | cut -d" " -f4

        The resulting string has a degrees of centigrade sign added.
        """
        try:
            load = subprocess.Popen("acpi -t | cut -d' ' -f4", stdout=subprocess.PIPE, shell=True)
            out = load.communicate()[0]
            #out = out.split(',')[0] if ',' in out else out
            return out.rstrip('\n') + ' °C'
        except Exception, e:
            container.log.error("CPU temp error: '%s'" % e.__repr__())
            return 'N/A'
