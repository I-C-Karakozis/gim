'''
These tests are heavily based on https://realpython.com/blog/python/token-based-authentication-with-flask
'''

from tests import GimTestCase
from tests import user_helpers as api
from tests import http_helpers as http

import time
import json

from app.mod_api import models

user = models.User(
    email='spongebob@squarepants.com',
    password='bikinibottom'
)

class TestAuth(GimTestCase.GimFreshDBTestCase):
    def test_registration(self):
        with self.client:
            response = api.register_user(self.client, 
                                         email='goofy@goober.com',
                                         password='password1!'
                                         )
            data = json.loads(response.data.decode())
            assert data['status'] == 'success'
            assert data['auth_token']
            assert response.content_type == 'application/json'
            assert response.status_code == http.CREATED 

    def test_register_with_already_registered_user(self):
        self.db.session.add(user)
        self.db.session.commit()
        
        with self.client:
            response = api.register_user(self.client,
                                         email=user.email,
                                         password='password1!'
                                         )
            data = json.loads(response.data.decode())
            assert data['status'] == 'failed'
            assert response.content_type == 'application/json'
            assert response.status_code == http.ACCEPTED

    def test_registered_user_login(self):
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

    def test_user_status(self):
        with self.client:
            response_register = api.register_user(self.client,
                                                  email='test@test.com',
                                                  password='password1!'
                                                  )
            auth_token = json.loads(response_register.data.decode())['auth_token']
            response_user = api.get_user_status(self.client,
                                         auth='Bearer ' + auth_token)
            data = json.loads(response_user.data.decode())
            assert data['status'] == 'success'
            assert data['data']['user_id'] > 0
            assert response_user.status_code == http.OK
            
    def test_valid_logout(self):
        with self.client:
            response_register = api.register_user(self.client,
                                                  email='test@test.com',
                                                  password='password1!'
                                                  )
            data_register = json.loads(response_register.data.decode())
            assert data_register['status'] == 'success'
            assert data_register['auth_token']
            assert response_register.content_type == 'application/json'
            assert response_register.status_code == http.CREATED
            response_login = api.login_user(self.client,
                                            email='test@test.com',
                                            password='password1!'
                                            )
            data_login = json.loads(response_login.data.decode())
            assert data_login['status'] == 'success'
            assert data_login['auth_token']
            assert response_login.content_type == 'application/json'
            assert response_login.status_code == http.OK

            auth_token = json.loads(response_login.data.decode())['auth_token']
            response = api.logout_user(self.client,
                                       auth='Bearer ' + auth_token)
            data = json.loads(response.data.decode())
            assert data['status'] == 'success'
            assert response.status_code == http.OK

# TODO: this test needs some love, coordinate time.sleep with token expiration

#    def test_invalid_logout(self):
#        response_register = api.register_user(self.client,
#                                              email='test@test.com',
#                                              password='password'
#                                              )
#        data_register = json.loads(response_register.data.decode())
#        assert data_register['status'] == 'success'
#        assert data_register['auth_token']
#        assert response_register.content_type == 'application/json'
#        assert response_register.status_code == http.CREATED
#        response_login = api.login_user(self.client,
#                                        email='test@test.com',
#                                        password='password'
#                                        )
#        data_login = json.loads(response_login.data.decode())
#        assert data_login['status'] == 'success'
#        assert data_login['auth_token']
#        assert response_login.content_type == 'application/json'
#        assert response_login.status_code == http.OK
        
#        time.sleep(5)
#        auth_token = json.loads(response_login.data.decode())['auth_token']
#        response = api.logout_user(self.client,
#                                   auth='Bearer ' + auth_token)
#        data = json.loads(response.data.decode())
#        assert data['status'] == 'failed'
#        assert response.status_code == http.UNAUTH

    def test_valid_blacklisted_token_user(self):
        with self.client:
            response_register = api.register_user(self.client,
                                                  email='test@test.com',
                                                  password='password1!'
                                                  )
            auth_token = json.loads(response_register.data.decode())['auth_token']
            blacklist_token = models.BlacklistToken(token=auth_token)
            self.db.session.add(blacklist_token)
            self.db.session.commit()
            response = api.get_user_status(self.client,
                                auth='Bearer ' + auth_token)
            data = json.loads(response.data.decode())
            assert data['status'] == 'failed'
            assert response.status_code == http.UNAUTH
            
