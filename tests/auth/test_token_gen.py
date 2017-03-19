from tests import GimTestCase
from tests import http_helpers as http

import json

from app.mod_api import models

user = models.User(
            email='fake@real.com',
            password='password'
            )

class TestAuth(GimTestCase.GimTestCase):
    def test_encode_auth_token(self):
        self.db.session.add(user)
        self.db.session.flush()
        auth_token = user.encode_auth_token()
        assert isinstance(auth_token, bytes)
        self.db.session.rollback()

    def test_decode_auth_token(self):
        self.db.session.add(user)
        self.db.session.flush()
        auth_token = user.encode_auth_token()
        assert isinstance(auth_token, bytes)
        assert models.User.decode_auth_token(auth_token.decode('utf-8')) == user.u_id
        self.db.session.rollback()
