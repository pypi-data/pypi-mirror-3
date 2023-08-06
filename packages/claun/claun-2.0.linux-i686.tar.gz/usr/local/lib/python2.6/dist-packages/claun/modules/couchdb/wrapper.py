# -*- coding: utf-8 -*-
"""
Wrapper for accessing CouchDB using couchdb-python.
"""

from claun.core import container

import couchdb.client
import couchdb.design

from couchdb.http import ResourceNotFound
from couchdb.http import Unauthorized


from httplib import CannotSendRequest
from httplib import ResponseNotReady
from uuid import uuid4
import socket

class CouchError(Exception): pass

__docformat__ = 'restructuredtext en'
__all__ = ['CouchWrapper', 'CouchError']

class CouchWrapper:
    r"""Wrapper class for accessing CouchDB.

    Instance of this should be used as a proxy for CouchDB database.
    It can work with databases, documents and provides methods for
    syncing views placed anywhere in the code.

    Every method may raise CouchError

    >>> wrapper = CouchWrapper('localhost', '5984', 'http')

    Wrapper can work on both HTTP and HTTPS.
    """

    def __init__(self, host, port=5984, protocol = 'https', username=None, password=None):
        """Sets up couchdb.client.Server.

        If a connection to the server can not be made, a socket.error is raised.

        :param host: hostname where couchdb is running
        :param port: port where couchdb is listening (optional, default 5984)
        :param protocol: protocol that the couchdb understands, http|https (optional, default https)
        :param username: CouchDB username, optional
        :param password: CouchDB password, optional
        """
        self.host = host
        self.protocol = protocol
        self.port = port
        uriparts = [self.protocol, '://']
        if username is not None and password is not None:
            uriparts += [username, ':', password, '@']
        uriparts += [self.host, ':', str(self.port)]
        fulluri = ''.join(uriparts)
        self.server = couchdb.client.Server(url = fulluri)
        container.log.debug('Connecting to couch on: %s' % fulluri)

    # Database operations

    def create_database(self, database_name):
        """Creates database.

        :param database_name: Name of the database
        :return: created database
        :rtype: `couchdb.client.Database`
        """
        try:
            return self.server.create(database_name)
        except socket.error as e:
            raise CouchError(e)

    def delete_database(self, database_name):
        """Deletes database.

        :param database_name: Name of the database
        :return: None
        :rtype: None
        """
        try:
            return self.server.delete(database_name)
        except socket.error as e:
            raise CouchError(e)

    def list_databases(self):
        """Gets all databases.

        Uses couchdb.client.Server capabilities to iterate over
        databases.

        :return: iterator over databases
        """
        try:
            return self.server
        except socket.error as e:
            raise CouchError(e)

    def database_info(self, database_name):
        """Gets info document about database

        :param database_name: Database name
        :rtype: dict
        """
        try:
            return self.server[database_name].info()
        except socket.error as e:
            raise CouchError(e)

    def get_database(self, database_name):
        """Gets database.

        :param database_name: Database name
        :rtype: `couchdb.client.Database`
        """
        try:
            return self.server[database_name]
        except socket.error as e:
            raise CouchError(e)

    def touch_database(self, database_name):
        """
        Checks if database exists and if it does not, tries to create it.

        May raise CouchError when a database cannot be created.

        :param database_name: Database name
        :rtype: boolean
        """
        try:
            self.get_database(database_name)
            return True
        except ResourceNotFound:
            container.log.error('Missing database %s' % database_name)
            try:
                self.create_database(database_name)
                container.log.info('Created database...')
                return True
            except Unauthorized:
                raise CouchError('Cannot create database %s' % database_name)
        except Unauthorized:
            raise CouchError('Cannot retrieve database %s' % database_name)
        return False


    # Document operations

    def list_documents(self, database_name):
        """Lists all documents in a database.

        :param database_name: Database name
        :rtype: `couchdb.client.ViewResults`
        """
        try:
            return self.server[database_name].view('_all_docs')
        except socket.error as e:
            raise CouchError(e)

    def get_document(self, database_name, document_id):
        """Gets document with given doc_id.

        :param database_name: Database name
        :param document_id: Document id
        :return: Document or None
        :rtype: `couchdb.client.Document`
        """
        try:
            return self.server[database_name].get(document_id)
        except socket.error as e:
            raise CouchError(e)

    def save_document(self, database_name, document):
        """Saves document.

        If given document does not have it's id, it is generated
        as suggested in http://packages.python.org/CouchDB/client.html#couchdb.client.Database.save

        :param database_name: Database name
        :param document: dict with document
        :return: (id, rev)
        :rtype: tuple
        """
        try:
            if '_id' not in document:
                document['_id'] = uuid4().hex
            return self.server[database_name].save(document)
        except socket.error as e:
            raise CouchError(e)

    def save_documents(self, database_name, documents):
        """Shorthand for saving multiple documents.

        This method does not inject the uuid into any documents.

        :param database_name: Database name
        :param documents: list of documents
        :return: iterable over the resulting documents
        :rtype: list
        """
        try:
            return self.server[database_name].update(documents)
        except socket.error as e:
            raise CouchError(e)

    def delete_document(self, database_name, document):
        """Deletes a document

        :param database_name: Database name
        :param document: Document to be deleted
        """
        try:
            return self.server[database_name].delete(document)
        except ResourceNotFound as rnf:
            container.log.error(rnf)
            return None
        except socket.error as e:
            raise CouchError(e)

    def view(self, database_name, view_name, wrapper=None, **options):
        """Performs view on database.

        If a view is not found, FatalError is raised.

        :param database_name: Database name where to perform
        :param view_name: view name with design document name, for example 'blog/articles'
        :param wrapper: optional callable that wraps around the result rows
        :param options: optional query string parameters
        :return: the view results
        :rtype: `couchdb.client.ViewResults`
        """
        successful = False
        try:
            while not successful:
                try:
                    ret = self.server[database_name].view(view_name, wrapper, **options)
                    ret.total_rows # fetch and raise ResourceNotFound eventually
                    successful = True
                    return ret
                except CannotSendRequest as csr:
                    container.log.error('Cannot Send Request: %s' % csr)
                except ResponseNotReady as rnr:
                    container.log.error(rnr)
        except socket.error as e:
            raise CouchError(e)
        except ResourceNotFound:
            raise container.errors.FatalError('View %s was not found in %s!' % (view_name, database_name))

    def query(self, database_name, map_function, reduce_function=None, language='python', wrapper=None, **options):
        """Performs an ad-hoc query (temporary view) on database.

        This might be slow.

        :param database_name: Database name where to perform
        :param map_function: code of map function, if language is python, the reference is enough
        :param reduce_function: code of reduce function, if language is python, the reference is enough (optional)
        :param language: programming language of the functions (optional)
        :param wrapper: optional callable that wraps around the result rows (optional)
        :param options: optional query string parameters (optional)
        :return: the view results
        :rtype: `couchdb.client.ViewResults`
        """
        try:
            return self.server[database_name].query(map_function, reduce_function, language, wrapper, **options)
        except socket.error as e:
            raise CouchError(e)

    # Attachments
    def get_attachment(self, database_name, id_or_doc, filename, default=None):
        """Returns attachment from a document.

        :param database_name: Database name where to perform
        :param id_or_doc: either a document ID or a dictionary or Document object representing the document that the attachment belongs to
        :param filename: name of the attachment
        :param default: default value to return when the document or attachment is not found (optional, default None)
        :return: a file-like object with read and close methods, or the value of the default argument if the attachment is not found
        """
        try:
            successful = False
            while not successful:
                try:
                    ret = self.server[database_name].get_attachment(id_or_doc, filename, default)
                    successful = True
                    return ret
                except CannotSendRequest as csr:
                    container.log.error(csr)
                except ResponseNotReady as rnr:
                    container.log.error(rnr)
        except socket.error as e:
            raise CouchError(e)

    def put_attachment(self, database_name, doc, contents, filename, content_type=None):
        """Creates/Updates attachment of a document.

        The implementation tries to put attachment in a loop that can deal with
        CannotSendRequest and ResponseNotReady exceptions. If the database does not
        respond, you may get stuck here.

        If a socket.error occurs, the CouchError is raised.

        :param database_name: Database name where to perform
        :param doc: Document to which the attachment should be attached (should contain both _id and _rev)
        :param contents: Raw contents of the attachment (file like object or string)
        :param filename: name of the attachment
        :param content_type: Content type of the attachment. If None, CouchDB makes a guess based on attachment's extension. (Default is None)
        :return: None
        """

        try:
            successful = False
            while not successful:
                try:
                    ret = self.server[database_name].put_attachment(doc, contents, filename, content_type)
                    successful = True
                    return ret
                except CannotSendRequest as csr:
                    container.log.error(csr)
                except ResponseNotReady as rnr:
                    container.log.error(rnr)
        except socket.error as e:
            raise CouchError(e)

    def delete_attachment(self, database_name, doc, filename):
        """Removes attachment `filename` of the document `doc`.

        The implementation tries to delete attachment in a loop that can deal with
        CannotSendRequest and ResponseNotReady exceptions. If the database does not
        respond, you may get stuck here.

        If a socket.error occurs, the CouchError is raised.

        :param database_name: Name of the database where to perform
        :param doc: Dictionary or Document with `_id` and `_rev` specified.
        :param filename: Name of the attachment to delete.
        """
        try:
            successful = False
            while not successful:
                try:
                    ret = self.server[database_name].delete_attachment(doc, filename)
                    successful = True
                    return ret
                except CannotSendRequest as csr:
                    container.log.error(csr)
                except ResponseNotReady as rnr:
                    container.log.error(rnr)
        except socket.error as e:
            raise CouchError(e)


    # Permanent views

    def define_view(self, design_name, view_name, map_function, reduce_function=None, language='python', wrapper=None, **options):
        """Prepares custom view to be stored into database.

        >>> wrapper = CouchWrapper('localhost', '5984')
        >>> def map(doc): yield None, doc
        >>> articles = wrapper.define_view('blog', 'articles', map)

        However the view is not stored, it is just prepared. To store
        views, use sync_views method that can accept multiple views.

        >>> wrapper.sync_views('db', [articles])

        :param design_name: Name of design document
        :param view_name: Name of the view
        :param map_function: code of map function, if language is python, the reference is enough
        :param reduce_function: code of reduce function, if language is python, the reference is enough (optional)
        :param language: programming language of the functions (optional)
        :param wrapper: optional callable that wraps around the result rows (optional)
        :param options: optional query string parameters (optional)
        :return: the view definition
        :rtype: `couchdb.design.ViewDefinition`
        """
        try:
            return couchdb.design.ViewDefinition(design_name, view_name, map_function, reduce_function, language, wrapper, **options)
        except socket.error as e:
            raise CouchError(e)

    def sync_views(self, database_name, views, remove_missing=False, callback=None):
        """Synchronizes views with database. See `define_view` method

        :param database_name: where to store the views
        :params views: list of `couchdb.design.ViewDefintion` instances
        :param remove_missing: if the engine deletes views that are not specified in the views parameter (optional, default False)
        :param callback: a function that is called on a document after getting it from database and before it gets updated, gets doc as the only argument
        """
        try:
            couchdb.design.ViewDefinition.sync_many(self.server[database_name], views, remove_missing, self._sync_views_callback(callback))
        except socket.error as e:
            raise CouchError(e)

    def _sync_views_callback(self, outer_callback=None):
        """
        Wrapper callback function for sync_views method.

        Currently does nothing.
        """
        if outer_callback is not None:
            outer_callback()
