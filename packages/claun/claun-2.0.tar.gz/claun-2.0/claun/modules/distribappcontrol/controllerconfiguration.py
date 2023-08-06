"""
Interface for accessing all builders for controllers.

It can automatically import necessary classes and call their building process.
Generators for particular controllers are stored in the controllers module and their
name should be the same as is the `controller_name` attribute in the
claun.modules.distribappcontrol.model only with the first letter capitalized.
"""
from claun.core import container
from claun.modules.distribappcontrol import model

__all__ = ['ControllerConfigurationBuilderError', 'ControllerConfigurationBuilder']

class ControllerConfigurationBuilderError(Exception): pass

class ControllerConfigurationBuilder:
    """
    Director of the whole building process.
    """
    def __init__(self, controllertype, cconfigname, customization):
        """
        Sets attributes and tries to import the builder class using the set_builder method.

        :param controllertype: Name of the controller, it is used to lookup the appropriate class.
        :param cconfigname: Name of the controller's base configuration. It is retrieved later from the model
        :param customization: Dictionary containing attributes that should be overriden in the base configuration.
        """
        self.controllername = controllertype
        self.configname = cconfigname
        self.customization = customization
        self.builder = self.set_builder(self.controllername)

    def set_builder(self, controllertype):
        """
        Tries to import the appropriate builder class from the controllers module.

        If no such builder class exist, a ControllerConfigurationBuilderError is raised.
        Class is not instantiated, only a symbol is returned.
        :param controllertype: name of the controller, the class that the algorithm looks will **always** have the first letter capitalized
        """
        try:
            module = __import__('claun.modules.distribappcontrol.controllers', globals(), locals(), [controllertype.capitalize()])
            cls = getattr(module, controllertype.capitalize())
            return cls
        except AttributeError as ae:
            container.log.error(ae)
            raise ControllerConfigurationBuilderError('Cannot find the appropriate builder.')

    def get_config(self, controllername, configname):
        """
        Tries to get base configuration from the model module.

        If there is no such configuration, a ControllerConfigurationBuilderError is raised.
        Uses model.config_by_controller method.
        """
        result = model.config_by_controller(controllername, configname)
        if result is None:
            container.log.error('No controller config found in db for %s:%s' % (controllername, configname))
            raise ControllerConfigurationBuilderError('Cannot find the appropriate controller configuration.')
        return result

    def build(self):
        """
        Tries to build the real configuration from information provided.

        If **any** Exception is thrown during the building process, a ControllerConfigurationBuilderError is raised.
        """
        try:
            builder = self.builder(self.get_config(self.controllername, self.configname).value, self.customization)
            return builder.build()
        except Exception as e:
            container.log.error(e)
            raise ControllerConfigurationBuilderError('There was an error during building the configuration.')
