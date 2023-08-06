"""
I/O handler for incoming/outgoing requests.

Module consists of two handlers, one for input and one for output. It is useful
to unify the output of textual/structured/serializable data. Do not use this
module to transport binary data.

Configuration
-------------
Configuration options are the same for both processors:
  - available - List of supported media types (Optional)
  - default - Mime type used as a default fallback (Optional)

>>> input = core.InputHandler({'default'; 'application/json', 'available': ['application/json;q=0.9', 'application/xml']})

By default, module operates with application/json media type on both ends and
the behaviour is considered standard. If you are implementing custom media type
handler, the input method should produce the same output as the json method (which is
some form of dictionary).

Both input and output are implemented as separate methods for each media type.
For an example implementation, see ``input`` or ``output`` module.

media type handlers are loaded dynamically during startup, all letters are lowercased and
the './+-' characters are all replaced with '_'. Module then looks either in ``input`` or ``output``
for the appropriately named method (for 'application/json' it looks for
application_json method).

When the handler is not found, it can not be used.

Runtime
-------
When the input/output handler is called to do some work (either parse data or serialize it),
the appropriate HTTP headers are checked to provide the client what it originally wanted.
If the request can not be satisfied, a 406 Not Acceptable is returned.
If the request contains data in an unsupported media type, a 415 Unsupported Media Type is returned.

The library `mimeparse` is used for the "best media type fit" detection.

>>> a = input('{"document": ["val1", "val2"]}') # a = {'document': ['val1', 'val2']}
>>> a = input('<xml>sadf</xml>') # a = {'xml': 'sadf'} if XML input handler is defined, 415 otherwise

"""

import re

from claun.core import container
from claun.core import log

import mimeparse

__docformat__ = 'restructuredtext en'

INPUT_PACKAGE = 'claun.core.communication.io.input'
OUTPUT_PACKAGE = 'claun.core.communication.io.output'
DEFAULT_AVAILABLE_INPUT = ['application/json', 'application/x-www-form-urlencoded', 'text/plain']
DEFAULT_AVAILABLE_OUTPUT = ['application/json', 'application/x-www-form-urlencoded', 'text/plain']
DEFAULT_INPUT = 'application/json'
DEFAULT_OUTPUT = 'application/json'

class DynamicHandlerLoader:
    """
    Base class for input and output handlers.
    """
    def __init__(self, configuration, package, default_available, default_default):
        """
        Tries to load all available handlers and determines the default media type.

        :param configuration: Dictionary containing keys available and default, available is
        a list of all desired media type handlers and default is the default one. Both keys are optional.
        :param package: Where to look for handlers declared in configuration['available'] field
        :param default_available: Fallback value for available handlers
        :param default_default: Fallback value for default handler
        """
        self.available = configuration.get('available', default_available)
        self.default = configuration.get('default', default_default)
        self.name = self.__class__.__name__[0:-7].lower()
        self.package = package
        self.handlers = {}
        self.params = {}
        self.load()
        self.default = self.default if self.default in self.handlers else self.handlers.keys()[0]
        self.available = self.handlers.keys()
        container.log.debug('Setting "%s" as default %s handler' % (self.default, self.name))

    def all_available(self):
        list = []
        default = ''
        for h in self.handlers.keys():
            string = '%s;%s' % (h, self.params[h]) if h in self.params else h
            if h == self.default:
                default = string
            else:
                list.append(string)
        list.append(default)
        return list

    def load(self):
        """
        Tries to load all handlers declared in self.available.

        They can contain the quality information, it is stripped here.

        If no handlers are loaded, a ClaunIOError is raised.
        """
        for handler in self.available:
            splitter = handler.split(';')
            handlername = splitter[0]
            if len(splitter) > 1:
                self.params[handlername] = splitter[1]
            f = self._map_handler(handlername)
            if f is not None:
                self.handlers[handlername] = f
                container.log.debug('Loaded "%s" %s handler' % (handlername, self.name))

        if not self.handlers:
            raise ClaunIOError('No %s handlers loaded' % self.name)

    def _map_handler(self, orig_name):
        """
        Tries to import one handler for media type ``orig_name``.

        Orig_name is transformed into a method name: './+-' characters are
        all replaced with '_' (application/vnd.ms-excel => application_vnd_ms_excel).
        If such method is not found, an error is logged and None is returned.
        If a method is found, a callable is returned.
        """
        name = re.sub('\+|\/|\.|-', '_', orig_name.lower())
        try:
            module = __import__(self.package, globals(), locals(), [name])
            return getattr(module, name)
        except AttributeError:
            container.log.error('Cannot import "%s" %s handler' % (orig_name, self.name))
            return None

class OutputHandler(DynamicHandlerLoader):
    """
    This class handles all output, it is callable.
    """
    def __init__(self, configuration):
        """
        Initializes underlying instance of DynamicHandlerLoader with
        OUTPUT_PACKAGE, DEFAULT_AVAILABLE_OUTPUT, DEFAULT_OUTPUT.
        """
        DynamicHandlerLoader.__init__(self, configuration, OUTPUT_PACKAGE, DEFAULT_AVAILABLE_OUTPUT, DEFAULT_OUTPUT)

    def __call__(self, data, **kwargs):
        """
        Converts ``data`` to appropriate media format.

        You can specify the output media type by passing 'header' argument.
        If it is not present, request's HTTP Accept header's content is checked.
        If no specific media type is passed, a `default` media type is used,
        mimeparse's best match is used otherwise.

        If no appropriate match is found, a 406 Not Acceptable is returned.
        """
        if 'header' not in kwargs:
             header = container.web.ctx.environ.get('HTTP_ACCEPT', None)
        else:
            header = kwargs['header']
            del kwargs['header']
        if header is None or header == '*/*':
            name = self.default
        else:
            name = mimeparse.best_match([self.default] + self.available, header)
        if name == '':
            raise container.web.notacceptable()
        return self.handlers[name](data, **kwargs)


class InputHandler(DynamicHandlerLoader):
    def __init__(self, configuration):
        """
        Initializes underlying instance of DynamicHandlerLoader with
        INPUT_PACKAGE, DEFAULT_AVAILABLE_INPUT, DEFAULT_INPUT.
        """
        DynamicHandlerLoader.__init__(self, configuration, INPUT_PACKAGE, DEFAULT_AVAILABLE_INPUT, DEFAULT_INPUT)

    def __call__(self, data, **kwargs):
        """
        Tries to convert ``data`` from media format to python data structure.

        You can specify the input media type by passing 'header' argument.
        If it is not present, request's HTTP Content-Type header's content is checked.
        If no specific media type is passed, a `default` media type is used,
        mimeparse's best match is used otherwise.

        If no appropriate match is found, a 415 Unsupported Media Type is returned.
        """
        if 'header' not in kwargs:
            header = container.web.ctx.environ.get('CONTENT_TYPE', None)
        else:
            header = kwargs['header']
            del kwargs['header']

        if header is None:
            name = self.default
        else:
            name = mimeparse.best_match([self.default] + self.available, header)

        if name == '':
            raise container.web.unsupportedmediatype()

        return self.handlers[name](data, **kwargs)


class ClaunIOError(Exception): pass

container.errors.ClaunIOError = ClaunIOError
