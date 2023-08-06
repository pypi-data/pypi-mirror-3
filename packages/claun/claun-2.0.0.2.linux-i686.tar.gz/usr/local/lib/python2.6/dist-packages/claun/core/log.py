"""
Python's default Logger decorator. Sets up the message format and destination logfile.

>>> log.setup({
>>>     'location': './logs',
>>>     'logname': 'something',
>>>     'max_size': '5',
>>>     'backups': '5',
>>>     'level': 'warning',
>>>     })

>>> log.error('message') # appends 'message' to './logs/something.log'

>>> log.add_handler('another', 'error') # creates ./logs/another.log
>>> log.warning('message', 'another') # does nothing
>>> log.warning('message') # appends 'message' to './logs/something.log'
>>> log.error('message', 'another') # appends 'message' to './logs/another.log'
"""

import logging
import inspect
from logging import handlers

FORMAT = '%(levelname)s:%(asctime)-15s:%(message)s'
DEFAULT_MAX_SIZE_MB = 20
DEFAULT_BACKUPS = 5
DEFAULT_LEVEL = 'INFO'

levels = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET
}

loggers = {}
settings = {}

class LoggingError(Exception): pass

def setup(configuration):
    """
    Checks configuration and creates a default logging handler.

    Configuration is a dictionary with only one mandatory parameter and that
    is `location`.

    Other possible parameters are logname, max_size, backups and level.
      - max_size and backups are attributes of RotatingFileHandler.
      - level is a minimal level that will be logged
      - if logname is not specified, 'log' is used
    """
    global loggers, levels
    if 'location' not in configuration:
        raise LoggingError('Missing log location!')
    if configuration['location'].startswith('..') or configuration['location'].startswith('/'):
        raise LoggingError('Unsecure location! It can not start with ".." or "/"')

    settings['location'] = configuration['location']
    settings['logname'] = configuration.get('logname', 'log')
    settings['max_size'] = configuration.get('max_size_mb', DEFAULT_MAX_SIZE_MB) * 1024 * 1024 # MBs to Bs
    settings['backups'] = configuration.get('backups', DEFAULT_BACKUPS)
    settings['level'] = configuration.get('level', DEFAULT_LEVEL).upper()

    add_handler(settings['logname'], settings['level'])

def add_handler(logname, level=DEFAULT_LEVEL):
    """
    Creates new handler named `logname`.

    Requires that a setup method is run before.
    """
    global loggers, settings, levels
    if len(settings) < 1:
        raise LoggingError('Logging was not yet set up.')

    if logname in loggers:
        return

    try:
        h = handlers.RotatingFileHandler('%s/%s.log' % (settings['location'], logname), maxBytes=settings['max_size'], backupCount=settings['backups'])
    except IOError:
        raise LoggingError('No such file or directory %s' % (settings['location']))
    h.setFormatter(logging.Formatter(FORMAT))
    loggers[logname] = logging.getLogger(logname)
    loggers[logname].setLevel(levels.get(level.upper(), levels[DEFAULT_LEVEL]))
    loggers[logname].addHandler(h)

def critical(message, logname=None):
    """
    :param message: Message to log
    :param logname: If not specified, message is written to a default log.
    """
    global loggers
    caller = inspect.stack()[1]
    message = '%s:%s:%s: %s' % (caller[1], caller[3], caller[2], message)
    if logname is None or logname not in loggers:
        loggers[settings['logname']].critical(message)
    else:
        loggers[logname].critical(message)

fatal = critical

def error(message, logname=None):
    """
    :param message: Message to log
    :param logname: If not specified, message is written to a default log.
    """
    global loggers
    caller = inspect.stack()[1]
    message = '%s:%s:%s: %s' % (caller[1], caller[3], caller[2], message)
    if logname is None or logname not in loggers:
        loggers[settings['logname']].error(message)
    else:
        loggers[logname].error(message)

def info(message, logname=None):
    """
    :param message: Message to log
    :param logname: If not specified, message is written to a default log.
    """
    global loggers
    caller = inspect.stack()[1]
    message = '%s:%s:%s: %s' % (caller[1], caller[3], caller[2], message)
    if logname is None or logname not in loggers:
        loggers[settings['logname']].info(message)
    else:
        loggers[logname].info(message)

def debug(message, logname=None):
    """
    :param message: Message to log
    :param logname: If not specified, message is written to a default log.
    """
    global loggers
    caller = inspect.stack()[1]
    message = '%s:%s:%s: %s' % (caller[1], caller[3], caller[2], message)
    if logname is None or logname not in loggers:
        loggers[settings['logname']].debug(message)
    else:
        loggers[logname].debug(message)

def flush():
    """
    Call ``flush`` on all loggers.
    """
    global loggers
    for l in loggers.itervalues():
        for h in l.handlers:
            h.flush()
