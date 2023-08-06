"""
"""
import os

from claun.core import container
from claun.modules.rstprocessor import rst_to_html

__uri__ = 'applications/admin/help'
__author__ = 'chadijir'

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/(.*)', 'Root'
           )

__app__ = container.web.application(mapping, locals())


class Root:
    def GET(self, path):
        """
        Basic information.
        """
        if path.startswith('..'):
            raise container.web.badrequest()
        abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), (os.sep).join(path.split('/')) )
        container.web.header('Content-Type', 'text/html')
        return rst_to_html(abspath)

