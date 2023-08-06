"""
Claun module: HW Control (Unix/Linux)
=====================================

Description
-----------
This module enables HW operations with the given computer.

Endpoints
---------
  - reboot
  - shutdown
  - restart-x

Configuration
-------------
No configuration options.

No dependencies.

Implementation details
----------------------
The commands are unix specific and require the su privileges. It is possible to run the component under a user
who can perform the needed commands.

Implementation for other OSs might be tricky.
"""


import subprocess

from claun.core import container


__uri__ = 'hwcontrol'
__version__ = '0.1'
__author__ = 'chadijir'
__dependencies__ = []

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/reboot', 'Reboot',
           '/shutdown', 'Shutdown',
           '/restart-x', 'RestartX',
           '/(.*)', 'HWControlRoot'
           )

__app__ = container.web.application(mapping, locals())
__docformat__ = 'restructuredtext en'
__all__ = ['HWControlRoot', 'Reboot', 'Shutdown', 'RestartX']


class HWControlRoot:
    """
    Lists all possible actions.
    """
    def GET(self, name):
        return container.output(container.module_basic_information(__name__, __version__, {
                          "reboot": container.baseuri + __uri__ + '/reboot',
                          "shutdown": container.baseuri + __uri__ + '/shutdown',
                          "restart-x": container.baseuri + __uri__ + '/restart-x',
                          }))

class Reboot:
    """
    Reboots the computer using the /sbin/reboot command.
    """
    def GET(self):
        container.log.info("The system is going for reboot now!")
        #subprocess.Popen('sudo /sbin/reboot'.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        return container.output([])

class Shutdown:
    """
    Shuts down the computer using the /shutdown -h 0 command.
    """
    def GET(self):
        container.log.info("The system is going for shutdown now!")
        #subprocess.Popen('sudo shutdown -h 0'.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        import sys
        sys.exit(0)
        return container.output([])

class RestartX:
    """
    Restarts the X-server by invoking /etc/init.d/xdm restart.
    """
    def GET(self):
        container.log.info("The system is restarting X-Server now!")
        #subprocess.Popen('sudo /etc/init.d/xdm restart'.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        return container.output([])
