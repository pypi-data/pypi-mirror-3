import sys
import time
from claun import core
from claun import modules
from claun.vendor import web
from core.configurator import ConfigurationError
from core.log import LoggingError
from core.communication.io import ClaunIOError

__all__ = ['core', 'modules']
__docformat__ = 'restructuredtext en'
__version__ = '2.0'
__author__ = 'Jiri Chadima'

class Claun:
    """
    Main class of the whole project that during startup initializes all structures and starts all services.

    >>> Claun("/path/to/config")
    """
    def __init__(self, configuration_path):
        """
        Startup method.

        Configuration is parsed, logging is set up and then other services are started.
        Firstly, it is the HttpClient, then the modules are loaded.
        The last one to start is the HttpServer. It is first configured and then the thread is started.
        After successfully starting the server daemon, an infinite loop is created that
        awaits KeyboardInterrupt exception that allows us to easily terminate the whole system.

        :param configuration_path: path to configuration file
        """
        # linking libraries
        core.container.web = web
        core.container.claun_version = __version__

        # configuration
        try:
            configurator = core.Configurator(configuration_path)
            core.container.configuration = configurator.parse()
        except ConfigurationError as ce:
            print('%s' % ce)
            sys.exit(1)

        # logging
        try:
            core.log.setup(core.container.configuration['logging'])
            core.log.info("Configuration file '%s' parsed OK" % configuration_path)
            core.container.log = core.log
        except LoggingError as le:
            print('%s' % le)
            sys.exit(1)

        # communication
        try:
            core.container.input = core.InputHandler(core.container.configuration['communication']['input'] if 'input' in core.container.configuration['communication'] else {})
            core.container.output = core.OutputHandler(core.container.configuration['communication']['output'] if 'output' in core.container.configuration['communication'] else {})
        except ClaunIOError as cioe:
            core.log.fatal(cioe)
            sys.exit(1)

        # HTTP client
        core.container.client = core.HttpClient(core.container.configuration['communication']['client'])

        # modules
        core.ModuleLoader(core.container.configuration['modules'])

        # start server
        server = core.HttpServer(core.container.configuration['communication']['server'])
        server.start()

        time.sleep(0.5) # let the server start
        if not server.is_alive():
            core.log.fatal("Server not running!")
            sys.exit(1)

        core.log.info("'%s' is up and running on %s:%i (%s)!" % (core.container.configuration['name'], core.container.configuration['communication']['server']['ip'], core.container.configuration['communication']['server']['port'], core.container.configuration['communication']['server']['fqdn']))

        while True: # keep daemon http server running
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                core.log.info("Got ^C, terminating")
                core.log.flush()
                print('')
                sys.exit(0)

