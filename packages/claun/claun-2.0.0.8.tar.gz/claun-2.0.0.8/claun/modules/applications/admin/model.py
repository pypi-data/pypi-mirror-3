"""
Model layer for the Admin Applications module.

The model uses CouchDB as a storage.

During startup, a database may be created and filled with views.
If views in the database are out of date, they are updated.

As this is not the only module working with the applications in the database,
no unnecessary views are deleted.
"""

from claun.modules.couchdb import client as db
from claun.core import container
from claun.modules.couchdb import CouchError



__docformat__ = 'restructuredtext en'

DB_NAME = container.configuration['modules']['applications']['db_name']
"""Default db name. Database should be created if it does not exist."""

class ModelError(Exception): pass

####

def applications_by_id_map(doc):
    """
    All applications by id, gets rid of no attributes.

    Resulting pairs: [id: {values}]
    """
    if doc['type'] == 'application':
        notallowed = ()
        filtered = dict((k, doc[k]) for k in doc if k not in notallowed)
        yield(filtered['id'], filtered)


# sync DB
try:
    db.touch_database(DB_NAME)
    views = [
            db.define_view('applications', 'by_id', applications_by_id_map),
            ]
    db.sync_views(DB_NAME, views, False) # multiple packages do this, dont't remove missing
except CouchError as ce:
    raise container.errors.FatalError(ce)

# public API
def all_applications():
    """
    All applications. Uses applications/by_id view.

    :return: ViewResults or []
    """
    try:
        return db.view(DB_NAME, 'applications/by_id')
    except CouchError as ce:
        container.log.error(ce)
        return []

def get_application(appid):
    """
    Application with id `appid`. Uses application/by_id view.

    If no such application exists, None is returned.
    """
    try:
        result = db.view(DB_NAME, 'applications/by_id', key=appid)
        if len(result) > 0:
            return result.__iter__().next()
    except Exception as e:
        container.log.debug("Application retrieval error: %s" % e)
        return None

def create_application(application):
    """Creates application as a new document.

    Application dictionary has to contain an `id` key.
    If application with `id` already exists, a ModelError is raised.

    :param application: Dictionary with application, has to contain `id` key
    :return: (id, rev) tuple of the newly saved document or None if some problem occurs
    """
    if 'id' not in application:
        raise ModelError('Missing ID')
    if get_application(application['id']) is not None:
        raise ModelError('Application already exists')
    try:
        return db.save_document(DB_NAME, application)
    except CouchError as ce:
        container.log.error(ce)
        return None

def update_application(application, docid=None, revid=None):
    """Updates application.

    You can specify `_id` and `_rev` either directly in the dictionary
    or as separate arguments. If `_id` or `_rev` are not present in either form,
    a ModelError is raised.

    :param application: Dictionary with application
    :param docid: `_id` attribute, if `application` contains `_id` field, may be None
    :param revid: `_rev` attribute, if `application` contains `_rev` field, may be None
    :return: (id, rev) tuple of the newly saved document, or None
    """
    if '_id' not in application:
        if docid is None:
            raise ModelError('No ID specified!')
        application['_id'] = docid

    if '_rev' not in application:
        if revid is None:
            raise ModelError('No revision specified!')
        application['_rev'] = revid
    try:
        return db.save_document(DB_NAME, application)
    except CouchError as ce:
        container.log.error(ce)
        return None

def delete_application(application):
    """
    Deletes application.

    May raise ModelError.
    :param application: The application dictionary or document containing the key _id.
    :return: boolean
    """
    if '_id' not in application:
        raise ModelError('Missing _ID')
    try:
        return db.delete_document(DB_NAME, application) is None
    except CouchError as ce:
        container.log.error(ce)
        return False


def delete_attachment(doc, filename):
    """Deletes attachment `filename` from document `doc`

    :param doc: Document/dictionary where to delete the attachment.
    :param filename: Name of the attachment to delete.
    :return: boolean
    """
    try:
        return db.delete_attachment(DB_NAME, doc, filename) is None
    except CouchError as ce:
        container.log.error(ce)
        return False

def put_attachment(doc, contents, filename): # omit content_type
    """
    Adds/overwrites attachment with name `filename` to `doc`.

    :param doc: Document/dictionary where to attach the attachment.
    :param contents: Attachment's contents.
    :param filename: Name under which the attachment will be stored. Older version may be overwritten.
    """
    try:
        return db.put_attachment(DB_NAME, doc, contents, filename)
    except CouchError as ce:
        container.log.error(ce)
        return None
