'''
These tests are heavily based on https://realpython.com/blog/python/token-based-authentication-with-flask
'''

from tests import GimTestCase
from tests import user_helpers as api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json

class TestAuth(GimTestCase.GimFreshDBTestCase):
    def test_auth_schema_bad_inputs(self):
        with self.client:
            response = api.post(self.client, '/api/Auth/Register',
                                         email='goofy@goober.com'
                                         )
            assert response.status_code == http.BAD_REQ

            response = api.post(self.client, '/api/Auth/Register',
                                         password='goofy@goober.com'
                                         )
            assert response.status_code == http.BAD_REQ

            response = api.post(self.client, '/api/Auth/Register',
                                         email='goofy@goober.com',
                                         password='password1!',
                                         wtf='wtf'
                                         )
            assert response.status_code == http.BAD_REQ

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
        with self.client:
            email = 'goofy@goober.com'
            response = api.register_user(self.client,
                                         email=email,
                                         password='password1!',
                                         confirm=False
                                         )
            response = api.register_user(self.client,
                                         email=email,
                                         password='password2!',
                                         confirm=False
                                         )
            data = json.loads(response.data.decode())
            assert data['status'] == 'failed'
            assert response.content_type == 'application/json'
            assert response.status_code == http.ACCEPTED      
            