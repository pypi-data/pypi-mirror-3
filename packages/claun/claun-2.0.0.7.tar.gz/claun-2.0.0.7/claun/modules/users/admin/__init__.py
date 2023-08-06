"""
Submodule: Admin
================

Description
-----------

Admin module for users, provides Users and Groups CRUD methods.

Groups are stored in a CouchDB in a separate document with the following structure (see groups.json):
  - type - groups
  - groups - list of group names

For a user example, see user.json and for more detailed documentation the users.auth module documentation.

Configuration
-------------
  - db_name - Name of the database where users/groups are stored.

Endpoints
---------
All endpoints are restricted to admin group. Groups endpoints are in addition restricted to admin_groups.
Users endpoints are in addition restricted to admin_users.

  - /groups
    - GET: List all
    - POST: Crate new
  - /groups/{group-id}
    - GET: List one
    - PUT: Update
    - DELETE: Delete
  - /users
    - GET: List all
    - POST: Crate new
  - /users/{user-id}
    - GET: List one
    - PUT: Update
    - DELETE: Delete

Implementation details
----------------------
When a user is created/updated, his/hers groups are not checked against stored groups. Groups are currently here
only to provide data for easier user creation.

The tight relation between groups and users would result into a much more complex design with cascade deletes etc.
"""



from claun.core import container

from claun.modules.users.admin.help import __app__ as helpapp # plugin the help app
from claun.modules.users.admin import model
from claun.modules.users.auth import restrict

__uri__ = 'users/admin'
__author__ = 'chadijir'

uris = {}

mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/groups/(.*)', 'Group',
           '/groups', 'Groups',
           '/users/(.*)', 'User',
           '/users', 'Users',
           '/help', helpapp,
           '/', 'Root',
           )

__app__ = container.web.application(mapping, locals())

def _transform_users(users, notallowed=[]):
    """
    Removes fields from `notallowed` list from every user in `users`.

    :param users: List of CouchDB documents (value attribute is expected)
    """
    ret = []
    for u in users:
        for i in notallowed:
            if i in u.value: del u.value[i]
        ret.append(u.value)
    return ret

class Root:
    def GET(self):
        """
        Basic information.
        """
        return container.output({
                          'users': container.baseuri + __uri__ + '/users',
                          'groups': container.baseuri + __uri__ + '/groups'})

class Groups:
    @restrict(['admin', 'admin_groups'])
    def GET(self, user=None):
        """
        List all groups
        """
        return container.output([{'id': m.key} for m in model.all_groups()])

    @restrict(['admin', 'admin_groups'])
    def POST(self, user=None):
        """
        Create group.

        Mandatory field is name.

        If a request is malformed, a 400 Bad Request is returned.
        If mandatory fields are not present, a 400 Bad Request is returned.
        if a ModelError is encountered, a 500 Internal Server Error is returned.
        """
        try:
            contents = container.input(container.web.data())
            if 'name' not in contents:
                raise container.web.badrequest()

            result = model.create_group(contents['name'])
            if result is not None:
                return ''
            else:
                return result

        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()


class Group:
    @restrict(["admin", "admin_users"])
    def GET(self, name, user=None):
        """Get group.

        404 Not Found if no such group exists.
        """
        group = model.get_group(name)
        if group is None:
            return container.web.notfound()
        return container.output({'id': group.key})

    @restrict(["admin", "admin_users"])
    def PUT(self, name, user=None):
        """
        Update group with `name`.

        Mandatory field is name (which may differ from the `name` in URL).
        If the field is different, the `name` group is deleted and the new group passed in message body
        is created.

        If a request contains malformed data, a 400 Bad Request is returned.
        If mandatory fields are not present, a 400 Bad Request is returned.
        If no such group exist, a 404 Not Found is returned.
        if a ModelError is encountered, a 500 Internal Server Error is returned.
        """
        if name == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such group.'}))
        try:
            contents = container.input(container.web.data())
            if 'name' not in contents:
                raise container.web.badrequest()

            result = model.replace_group(name, contents['name'])
            if result is not None:
                return ''
            else:
                return result
        except model.ModelError as me:
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()


    @restrict(["admin", "admin_users"])
    def DELETE(self, name, user=None):
        """
        Delete group with `name`.

        404 Not Found if the group does not exist.
        500 Internal Server Error if there is a problem with the model.
        """
        if name == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such group.'}))
        try:
            result = model.delete_group(name)
            if result:
                return ''
            else:
                return result
        except model.ModelError as me:
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))

class Users:
    @restrict(["admin", "admin_users"])
    def GET(self, user=None):
        """
        List all users without _id, _rev and passwordhash.
        """
        return container.output(_transform_users(model.all_users(), ['_id', '_rev', 'passwordhash']))

    @restrict(["admin", "admin_users"])
    def POST(self, user=None):
        """
        Create user.

        Mandatory fields are name, passwordhash, allowed and permissions.
        Generated fields are id (container.webalize_string), type (user) and client_tokens (empty dictionary).

        If a request contains malformed data, a 400 Bad Request is returned.
        If mandatory fields are not present, a 400 Bad Request is returned.
        if a ModelError is encountered, a 500 Internal Server Error is returned.
        """
        try:
            contents = container.input(container.web.data())
            if 'name' not in contents or 'passwordhash' not in contents or 'allowed' not in contents or 'permissions' not in contents:
                raise container.web.badrequest()

            contents.update({'id': container.webalize_string(contents['name']), 'type': 'user', 'client_tokens': {}})

            result = model.create_user(contents)
            if result is not None:
                return container.output(contents)
            else:
                return container.web.internalerror('Cannot save user to database.')
        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(me)
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

class User:
    @restrict(["admin", "admin_users"])
    def GET(self, name, user=None):
        """Get user"""
        user = model.get_user(name)
        if user is None:
            return container.web.notfound()
        return container.output(_transform_users([user], ['_id', '_rev', 'passwordhash'])[0])

    @restrict(["admin", "admin_users"])
    def PUT(self, name, user=None):
        """
        Update user.

        Mandatory fields are name, allowed and permissions.
        'client_tokens' field is always copied from the database.
        If 'passwordhash' is present, this new value is saved.
        Generated fields are id (container.webalize_string) and type (user).
        ID is generated only when the user's name has changed.

        If a request contains malformed data, a 400 Bad Request is returned.
        If mandatory fields are not present, a 400 Bad Request is returned.
        If no such group exist, a 404 Not Found is returned.
        if a ModelError is encountered, a 500 Internal Server Error is returned.
        """
        if name == '': raise container.web.notfound()
        user = model.get_user(name) # default values
        if user is None:
            raise container.web.notfound()

        try:
            contents = container.input(container.web.data())
            if 'name' not in contents or 'allowed' not in contents or 'permissions' not in contents:
                raise container.web.badrequest()

            contents['client_tokens'] = user.value['client_tokens'] # always overwrite
            if 'passwordhash' not in contents:
                contents['passwordhash'] = user.value['passwordhash']

            if 'type' not in contents:
                contents['type'] = 'user'

            if contents['id'] != user['id']:
                contents['id'] = container.webalize_string(contents['name'])

            result = model.save_user(contents, user.id, user.value['_rev'])
            if result is not None:
                return ''
            else:
                raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save user.'}))
        except model.ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()

    @restrict(["admin", "admin_users"])
    def DELETE(self, id, user=None):
        """
        Delete user with `id`.

        404 Not Found if the group does not exist.
        500 Internal Server Error if there is a problem with the model.
        """
        if id == '': raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such user.'}))
        user = model.get_user(id)
        if user is None:
            raise container.web.notfound(container.output({'error': 'model_error', 'error_description': 'No such user.'}))
        try:
            result = model.delete_user(user.value)
            if result:
                return ''
            else:
                return result
        except model.ModelError as me:
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))
