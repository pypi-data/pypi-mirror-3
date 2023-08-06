"""
Global container that contains stuff that is useful for the whole system, such as a configuration.

It is filled with fields during startup.
Fields accessible after successful startup:
  - core.container.web - links to the claun.vendor.web package containing the web.py library
  - core.container.configuration - dictionary with parsed YAML configuration file
  - core.container.errors - contains links to all errors that can be propagated from the core
    - FatalError - Fatal Error, program should end when such error is encountered
    - ClaunIOError - IO Error, bad serialization/deserialization of data
    - ClientError - HTTP Client error (Unreachable host, bad response)
  - core.container.log - links to core.log module
  - core.container.input - Callable claun.core.communication.InputHandler
  - core.container.output - Callable claun.core.communication.OutputHandler
  - core.container.client - isntance of claun.core.communication.HttpClient
  - core.container.module_basic_information - link to core.moduleloader.basic_information method
  - core.container.baseuri - http(s)://example.com:81/ aka full uri of the component
  - core.container.client_authentication - authentication method that can be called to authenticate incoming requests
  - core.container.modules - dictionary of all modules loaded during startup
"""

import unicodedata

class ObjectContainer:
    """
    Empty class providing object-like access to properties.
    """
    pass

    def __getattr__(self, attribute):
        try:
            log.error('Cannot find %s attribute' % attribute)
        except NameError:
            pass


__docformat__ = 'restructuredtext en'
## intentionally empty
errors = ObjectContainer()

def webalize_string(string):
    """
    Uses unicodedata to remove international characters, puts all characters
    to lowercase and replaces spaces with dashes.
    """
    return unicodedata.normalize('NFKD', string.lower().replace(' ', '-') ).encode('ascii', 'ignore')
