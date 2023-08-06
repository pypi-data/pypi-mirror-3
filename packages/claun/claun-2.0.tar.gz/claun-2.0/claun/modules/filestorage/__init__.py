"""
Claun module: File Storage
========================

Description
-----------
Simple facade for saving and reading files from one storage.

Endpoints
---------
No public endpoints.

Configuration
-------------
Example config section:
  filestorage:
      path: ./../storage

No dependencies.

Implementation details
----------------------
Files are stored under file names generated from their md5 hashes.
"""
import os

import hashlib
import re

from claun.core import container


__uri__ = 'filestorage'
__version__ = '0.1'
__author__ = 'chadijir'
__dependencies__ = []
mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/(.*)', 'Root'
           )

__app__ = container.web.application(mapping, locals())

class Root:
    """
    No public interface.
    """
    def GET(self, param):
        return container.output(container.module_basic_information(__name__, __version__, {}))

class StorageFacade:
    def __init__(self, directory):
        """
        Sets the directory path using the os.path.abspath routine that derives the path from `directory`.

        Please note, that no security checks are performed, so this might be a weak spot of your application.
        The correct security solution would be to run the component under a certain user that has access only
        to specified directories.
        """
        self.directory = os.path.abspath(directory)
        self.validator = re.compile(r"^[0-9a-f]{32}$")

    def write(self, contents):
        """
        Tries to write contents into a file.

        Filename is defined as a hex md5sum from the `contents`.
        Contents is written in 'wb' mode.
        :return: hash under which the file is stored, or None, if any IOError occurs.
        """
        try:
            hashname = hashlib.md5(contents).hexdigest()
            abspath = os.path.join(self.directory, hashname)
            handle = open(abspath, 'wb')
            handle.write(contents)
            handle.close()
            return hashname
        except IOError as ioe:
            container.log.error(ioe)
            return None

    def abspath(self, hash):
        """
        Returns absolute path for the filename `hash`.

        For security reasons, every hash is validated against a simple regexp: ^[0-9a-f]{32}$
        If the hash does not match, None is returned.
        """
        if self.validator.match(hash) is None:
            container.log.error('%s is not valid filename' % hash)
            return None
        return os.path.join(self.directory, hash)

    def read(self, hash):
        """
        Tries to read file with name hash (use hash provided when writing the file).

        For security reasons, every hash is validated against a simple regexp: ^[0-9a-f]{32}$
        """
        try:
            if self.validator.match(hash) is None:
                container.log.error('%s is not valid filename' % hash)
                return None
            abspath = os.path.join(self.directory, hash)
            handle = open(abspath, 'rb')
            contents = handle.read()
            handle.close()
            return contents
        except IOError as ioe:
            container.log.error(ioe)
            return None

storage = StorageFacade(container.configuration['modules']['filestorage']['path'])
