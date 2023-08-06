import os
from hashlib import sha256
from docutils.core import publish_string

from claun.core import container

__docformat__ = 'restructuredtext en'

__uri__ = 'rstprocessor'
__version__ = '0.1'
__author__ = 'chadijir'
__dependencies__ = []

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


class MemoryCacheUnit:
    def __init__(self, key, originalhash, value):
        self.key = key
        self.originalhash = originalhash
        self.value = value


class MemoryCache:
    """
    Simple in-memory key-value store for processed help pages.
    """
    db = {}

    def set(self, key, hash, value):
        self.db[key] = MemoryCacheUnit(key, hash, value)

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
        cache.remove(abspath)
        raise container.web.notfound()

    try:
        contents = open(abspath, 'r').read()
        hash = sha256(contents).hexdigest()
    except IOError:
        raise container.web.notfound()

    cached = cache.get(abspath)
    if cached is not None and cached.hash == hash:
        return cached

    converted = publish_string(contents, writer_name='html')
    cache.set(abspath, hash, converted)
    return converted

def raw_to_html(abspath):
    if not os.path.exists(abspath):
        cache.remove(abspath)
        raise container.web.notfound()

    try:
        contents = open(abspath, 'r').read()
        hash = sha256(contents).hexdigest()
    except IOError:
        raise container.web.notfound()

    cached = cache.get(abspath)
    if cached is not None and cached.hash == hash:
        return cached

    converted = publish_string('::\n    \n    %s' % "\n    ".join(contents.split('\n')), writer_name='html')
    cache.set(abspath, hash, converted)
    return converted

