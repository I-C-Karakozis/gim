'''
These tests are heavily based on https://realpython.com/blog/python/token-based-authentication-with-flask
'''

from tests import GimTestCase
from tests import user_helpers as api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json

class TestAuth(GimTestCase.GimFreshDBTestCase):
    def test_confirmed_user_login(self):
        with self.client:
            response_register = api.register_user(self.client,
                                                  email='goofy@goober.com',
                                                  password='password1!'
                                                  )
            data_register = json.loads(response_register.data.decode())
            assert data_register['status'] == 'success'
            assert data_register['auth_token']
            assert response_register.content_type == 'application/json'
            assert response_register.status_code == http.CREATED
            response_login = api.login_user(self.client,
                                            email='goofy@goober.com',
                                            password='password1!'
                                            )
            data_login = json.loads(response_login.data.decode())
            assert data_login['status'] == 'success'
            assert data_login['auth_token']
            assert response_login.content_type == 'application/json'
            assert response_login.status_code == http.OK

    def test_unconfirmed_user_login(self):
        with self.client:
            response_register = api.register_user(self.client,
                                                  email='goofy@goober.com',
                                                  password='password1!',
                                                  confirm=False
                                                  )
            data_register = json.loads(response_register.data.decode())
            assert response_register.status_code == http.CREATED

            response_login = api.login_user(self.client,
                                            email='goofy@goober.com',
                                            password='password1!'
                                            )
            assert response_login.status_code == http.UNAUTH

    def test_non_registered_user_login(self):
        with self.client:
            response = api.login_user(self.client,
                                      email='test@test.com',
                                      password='password1!'
                                      )
            data = json.loads(response.data.decode())
            assert data['status'] == 'failed'
            assert response.content_type == 'application/json'
            assert response.status_code == http.NOT_FOUND

    def test_bad_confirm_token(self):
        with self.client:
            response = api.get(self.client, '/api/Auth/Confirm/asdfghjkl')
            assert response.status_code == http.UNAUTH
            
