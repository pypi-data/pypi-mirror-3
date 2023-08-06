"""
Claun module: CouchDB
=====================

Description
-----------
CouchDB wrapper module using the couchdb-python (http://code.google.com/p/couchdb-python/) library.

The core of this module is the wrapper module, so for more documentation see that one.

Configuration
-------------
  couchdb:
    server: localhost # name of the server where couchdb runs
    port: 5984 # port where couchdb listens
    protocol: http # protocol, http or https
    username: admin # username (optional)
    password: admin # password for the user (optional)


No dependencies.

Implementation details
----------------------
The module was implemented on top of the couchdb-python library in the 0.8 version which is stable and works with Python 2.
This module was not tested against Python 3. According to http://code.google.com/p/couchdb-python/issues/detail?id=150 there
is currently no official version supporting the Python 3, however there is a patch
(see https://github.com/lilydjwg/couchdb-python3), so feel free to try it.

"""


from claun.core import container
from claun.modules.couchdb.wrapper import CouchWrapper
from claun.modules.couchdb.wrapper import CouchError

__uri__ = 'couchdb'
__version__ = '0.3'
__author__ = 'chadijir'
__dependencies__ = []

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/', 'Root'
           )

__docformat__ = 'restructuredtext en'
__app__ = container.web.application(mapping, locals())


username = None if 'username' not in container.configuration['modules']['couchdb'] else container.configuration['modules']['couchdb']['username']
password = None if 'password' not in container.configuration['modules']['couchdb'] else container.configuration['modules']['couchdb']['password']
client = CouchWrapper(container.configuration['modules']['couchdb']['server'], container.configuration['modules']['couchdb']['port'], container.configuration['modules']['couchdb']['protocol'], username, password)
"""client is a configured instance of the CouchWrapper."""

class Root:
    def GET(self):
        return container.output(container.module_basic_information(__name__, __version__, {}))
