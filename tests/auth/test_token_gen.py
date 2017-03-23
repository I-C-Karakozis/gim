from tests import GimTestCase
from tests import http_helpers as http

import json

from app.mod_api import models

class TestAuth(GimTestCase.GimFreshDBTestCase):
    def test_encode_auth_token(self):
        user = models.User(
            email='fake@real.com',
            password='password'
            )
        self.db.session.add(user)
        self.db.session.commit()
        auth_token = user.encode_auth_token()
        assert isinstance(auth_token, bytes)

    def test_decode_auth_token(self):
        user = models.User(
            email='fake@real.com',
            password='password'
            )
        self.db.session.add(user)
        self.db.session.commit()
        auth_token = user.encode_auth_token()
        assert isinstance(auth_token, bytes)
        assert models.User.decode_auth_token(auth_token.decode('utf-8')) == user.u_id
