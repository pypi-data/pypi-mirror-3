"""
Claun module: Users
===================

Description
-----------
This module provides support for multiple users (as in humans, not components) using the system.
It provides the administration module (CRUD functionality) and the auth module that contains
a subset of OAuth 2.0 implementation.

Endpoints
---------

  - /
  - /{user-id}
    - GET: Info about one user
    - PUT: Change a user's information
  - /auth - Auth submodule
  - /admin - Admin submodule

Configuration
-------------

Implementation details
----------------------
"""

from hashlib import sha256


from claun.core import container


from claun.modules.users.auth import __app__ as authapp
from claun.modules.users.admin import __app__ as adminapp

from claun.modules.users.auth import access_token_expired, OAuthBadRequest, Token, restrict, personalize
from claun.modules.users.admin.model import get_user
from claun.modules.users.admin.model import ModelError
from claun.modules.users.admin.model import save_user
from claun.modules.users.admin import _transform_users

__docformat__ = 'restructuredtext en'
__all__ = ['access_token_expired', 'Root', 'OAuthBadRequest', 'Token', 'restrict', 'personalize'] # from auth submodule

__uri__ = 'users'
__version__ = '0.2'
__author__ = 'chadijir'
__dependencies__ = ['couchdb']
mapping = (
           '', 'claun.core.communication.server.RedirToRoot',
           '/auth', authapp,
           '/admin', adminapp,
           '/(.*)', 'User',
           '/', 'Root'
           )

__app__ = container.web.application(mapping, locals())

class Root:
    def GET(self):
        return container.output(container.module_basic_information(__name__, __version__, {
                          'auth': container.baseuri + __uri__ + '/auth',
                          }))

class User:
    """
    This class handles the user that is logged in and should be used only to interact with his/hers identity.

    All endpoints should return 401 Unauthorized if a client requests information about
    a user that is not logged in (authorized by the @restrict decorator)
    """
    @restrict('all')
    def GET(self, id, user=None):
        """
        Displays info about one user without _id, _rev, passwordhash and client_tokens attributes.

        Raises 401 Unauthorized if a client requests different user than the one who's authorized in the request.
        Raises 404 Not Found if the user is not found in the database.
        """
        if id == '': raise container.web.badrequest()
        if id != user['id']:
            raise container.web.unauthorized()

        userdoc = get_user(id)
        if userdoc is None:
            raise container.web.notfound()
        return container.output(_transform_users([userdoc], ['_id', '_rev', 'passwordhash', 'client_tokens'])[0])

    @restrict('all')
    def PUT(self, id, user=None):
        """
        Update user, specifically change password. This method should not be used to change any other user preferences.

        Expects oldpassword and newpassword attributes in the message body.
        Oldpassword represents the user's current password and a newpassword is a newly created password.

        Raises 401 Unauthorized if a client requests different user than the one who's authorized in the request or if an oldpassword's hash does not match the
        current password's hash.
        Raises 404 Not Found if the user is not found in the database.
        Raises 400 Bad Request, if a request is malformed
        Raises 500 Internal Error if a ModelError is encoutnered.
        """
        if id == '': raise container.web.notfound()
        if id != user['id']:
            raise container.web.unauthorized()

        userdoc = get_user(id) # default values
        if userdoc is None:
            raise container.web.notfound()

        try:
            contents = container.input(container.web.data())

            if 'oldpassword' not in contents or 'newpassword' not in contents:
                raise container.web.badrequest()

            if sha256(contents['oldpassword']).hexdigest() != userdoc.value['passwordhash']:
                raise container.web.unauthorized(container.output({'error': 'bad_password', 'error_description': 'Bad old password!'}))

            userdoc.value['passwordhash'] = sha256(contents['newpassword']).hexdigest()

            result = save_user(userdoc.value)
            if result is not None:
                return ''
            else:
                raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': 'Cannot save user.'}))
        except ModelError as me:
            container.log.error(me)
            raise container.web.internalerror(container.output({'error': 'model_error', 'error_description': str(me)}))
        except container.errors.ClaunIOError as cioe:
            container.log.error('Cannot decode input: %s' % str(cioe))
            raise container.web.badrequest()
