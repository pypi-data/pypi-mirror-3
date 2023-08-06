"""
Interface for accessing all builders for frameworks.

It can automatically import necessary classes and call their building process.
Generators for particular frameworks are stored in the frameworks module and their
name should be the same as is the `framework_name` attribute in the
claun.modules.distribappcontrol.model only with the first letter capitalized (for example Cavelib for cavelib).
"""
from claun.core import container
from claun.modules.distribappcontrol import model

__all__ = ['FrameworkConfigurationBuilderError', 'FrameworkConfigurationBuilder']


class FrameworkConfigurationBuilderError(Exception): pass

class FrameworkConfigurationBuilder:
    """
    Director of the whole building process.
    """
    def __init__(self, frameworkname, fconfigname, computers, master, environment, customization):
        """
        Sets attributes and tries to import the builder using the set_builder method.

        :param frameworkname: Name of the framework name from which the builder class is derived.
        :param fconfigname: Name of the particular base configuration. It should be retrieved from the application model
        :param computers: Dictionary containing information about computers. Preferrably from the claun.modules.environment model
        :param master: Master node, one full record from `computers`
        :param environment: Dictionary containing the environment settings. Preferrably from the claun.modules.environment model.
        :param customization: Simple key:value dictionary that holds adjustments to the settings from other source (like user)
        """
        self.frameworkname = frameworkname
        self.fconfigname = fconfigname
        self.customization = customization
        self.computers = computers
        self.master = master
        self.environment = environment
        self.builder = self.set_builder(self.frameworkname)

    def set_builder(self, frameworktype):
        """
        Tries to import the appropriate builder class from the frameworks module.

        If no such builder class exist, a FrameworkConfigurationBuilderError is raised.
        Class is not instantiated, only a symbol is returned.
        :param frameworkname: name of the controller, the class that the algorithm looks will **always** have the first letter capitalized
        """
        try:
            module = __import__('claun.modules.distribappcontrol.frameworks', globals(), locals(), [frameworktype.capitalize()])
            cls = getattr(module, frameworktype.capitalize())
            return cls
        except AttributeError as ae:
            container.log.error(ae)
            raise FrameworkConfigurationBuilderError('Cannot find the appropriate builder.')

    def get_config(self, frameworkname, configname):
        """
        Tries to get base configuration from the model module.

        If there is no such configuration, a ControllerConfigurationBuilderError is raised.
        Uses model.config_by_controller method.
        """
        result = model.config_by_framework(frameworkname, configname)
        if result is None:
            container.log.error('No framework config found in db for %s:%s' % (frameworkname, configname))
            raise FrameworkConfigurationBuilderError('Cannot find the appropriate framework configuration.')
        return result

    def build(self):
        """
        Tries to build the real configuration from information provided.

        If **any** Exception is thrown during the building process, a FrameworkConfigurationBuilderError is raised.
        """
        try:
            builder = self.builder(self.environment, self.computers, self.master, self.get_config(self.frameworkname, self.fconfigname).value, self.customization)
            return builder.build()
        except Exception as e:
            container.log.error(e)
            raise FrameworkConfigurationBuilderError('There was an error during building the framework configuration.')
