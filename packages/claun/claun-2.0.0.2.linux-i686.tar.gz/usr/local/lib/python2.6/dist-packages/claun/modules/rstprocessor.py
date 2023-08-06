import os
from docutils.core import publish_string

from claun.core import container

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


class MemoryCache:
    """
    Simple in-memory key-value store for processed help pages.
    """
    db = {}

    def set(self, key, value):
        self.db[key] = value

    def get(self, key):
        """
        Returns None if key is not stored.
        """
        self.db.get(key, None)

    def remove(self, key):
        if key in self.db:
            del self.db[key]

cache = MemoryCache()

def rst_to_html(abspath):
    """
    Converts rst file contents to html with distutils.core.publish_string.

    Raises 404 Not Found if file does not exist or IOError occurs.

    Uses MemoryCache to speed things up.
    """
    if not os.path.exists(abspath):
        cached.remove(abspath)
        raise container.web.notfound()

    cached = cache.get(abspath)
    if cached is not None:
        return cached

    try:
        contents = open(abspath, 'r').read()
        converted = publish_string(contents, writer_name='html')
        cache.set(abspath, converted)
        return converted
    except IOError:
        raise container.web.notfound()