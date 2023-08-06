"""
Configuration parser. Uses PyYAML library.

The configuration of the component is stored in the YAML file.

The basic sections are:
  - name - Name of the component
  - version - Version of the component
  - platform - Platform that the component is running on. (i. e. "gentoo", "windows-x86")
  - communication - Configuration of `core.communication` module, see the appropriate documentation for details.
  - logging - Configuration of `core.log` module, see the appropriate documentation for details.
  - modules - Modules configuration, see `core.moduleloader` for details.

"""
import yaml

__docformat__ = 'restructuredtext en'

class Configurator:
    def __init__(self, configfile):
        """
        Sets-up the path to the file.
        """
        self.file = configfile

    def parse(self):
        """
        Opens file for reading, parses it, closes the file and returns the dictionary with parsed configuration.

        May raise ConfigurationError when the file is malformed or does not exist.
        """
        try:
            reader = open(self.file, 'r')
            loaded = yaml.load(reader)
            reader.close()
            return loaded
        except IOError as e:
            raise ConfigurationError(e)
        except yaml.parser.ParserError as e:
            raise ConfigurationError(e)

class ConfigurationError(Exception): pass
