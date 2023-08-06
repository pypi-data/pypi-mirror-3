"""
ModuleLoader is used during startup and tries to import all modules specified in the passed configuration with checking their dependencies.

The configuration is again a dictionary containing a key for every module that may contain another dictionary with the module's configuration.
The key (name of the module) has to be the same as the name of the python module that is present in the claun.modules package. A minimal module
might look like this (in a module named 'modulename'):

>>> from claun.core import container
>>> __uri__ = 'someuri' # mandatory
>>> __version__ = '0.1' # mandatory
>>> __author__ = 'chadijir' # mandatory
>>> __dependencies__ = ['othermodule'] # may be an empty list
>>>
>>> config = container.configuration['modules']['modulename'] # how to get the module's configuration
>>>
>>> mapping = (
>>>     '/(.*)', 'hello'
>>> ) # mandatory, see web.py documentation for subapplications
>>> __app__ = container.web.application(mapping, locals()) # mandatory, see web.py documentation for subapplications
>>>
>>> class hello:
>>>     def GET(self, params):
>>>             pass

In a configuration for every module, there might be the key 'public' present. It is optional and is used when using some form of client_authentication method on the server.
For more information, see the claun.core.communication.server module documentation.
"""
import sys


from claun.core import container

__docformat__ = 'restructuredtext en'
__all__ = ['basic_information', 'ModuleLoader', 'ModuleFatalError']

def basic_information(name, version, endpoints):
    """Creates a dictionary with basic information about a claun module.

    This may be used when requesting the root of a module.

    :param name: This is a __name__ variable of given module
    :param endpoints: A dictionary specifying URI endpoints that the module provides.
    """
    return {
            'module': name.split('.')[-1],
            'version': version,
            'endpoints': endpoints,
    }

container.module_basic_information = basic_information

class ModuleFatalError(Exception):
    """
    An error that may occur during module loading.
    """
    def __init__(self, module, exception):
        Exception.__init__(self, "%s: %s" %(module, exception))

class ModuleLoader:
    def __init__(self, configuration):
        """
        Tries to load modules and check their dependencies.

        self.imports field is used in the class to transport modules between methods.

        :param configuration: configuration dictionary, see the module documentation.
        """
        self.load_modules(configuration)
        self.check_dependencies()
        container.modules = self.imports

    def load_modules(self, list):
        """
        Tries to import modules in python runtime.

        ImportError is always caught and results into sys.exit.

        :param list: dictionary of modules, basically the same as the configuration
        """
        self.imports = {}
        if list is None:
            container.log.info("Loading 0 modules")
            return

        for module in list: # import all modules
            try:
                self.imports[module] = __import__('claun.modules.' + module, globals(), locals(), [module])
                container.log.info("Module '%s' successfully loaded" % module)
            except ModuleFatalError as e:
                container.log.fatal(e)
                sys.exit(1)
            except container.errors.FatalError as fe:
                container.log.fatal(fe)
                sys.exit(1)
            except ImportError as e:
                container.log.fatal(e)
                container.log.fatal("Error during loading module '%s', terminating" % module)
                sys.exit(1)

    def check_dependencies(self):
        """
        After loading all modules, their dependencies are checked.

        It is just looking into the dictionary of already imported modules if all dependencies
        are present. Currently, no version is checked.

        If an Unmet dependency is found, a sys.exit is invoked.
        """
        for module in self.imports.values(): # check dependencies
            container.log.debug("Checking '%s' dependencies" % module.__name__)
            for d in module.__dependencies__:
                try:
                    self.imports[d]
                except KeyError as e:
                    container.log.fatal("Unmet module dependencies: '%s' needs '%s', terminating" % (module.__name__, d))
                    sys.exit(1)
            container.log.info("Dependencies for '%s' OK" % module.__name__)
