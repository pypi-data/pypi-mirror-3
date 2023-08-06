"""
An example implementation of a screensaver application.

Its only work is to register to a distribappcontrol.distributor
and then process all events in receive_event method.
"""

from claun.core import container
from claun.modules.distribappcontrol import distributor

__docformat__ = 'restructuredtext en'

__uri__ = 'screensaverpoc'
__version__ = '0.1'
__author__ = 'chadijir'
__dependencies__ = ['distribappcontrol']

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/', 'Root',
           )

__app__ = container.web.application(mapping, locals())


class Root:
    """
    Provides basic information.
    """
    def GET(self):
        return container.output(container.module_basic_information(__name__, __version__, {}))


class EventListener:
    def receive_event(self, event, *args, **kwargs):
        print(event, args, kwargs)

distributor.add_event_listener(EventListener())