from tests import GimTestCase
from tests import user_helpers as api
from tests import http_helpers as http

import json

class TestUsers(GimTestCase.GimFreshDBTestCase):
    def test_get(self):
        with self.client:
            # register a user
            response = api.register_user(self.client, 
                                         email='goofy@goober.com',
                                         password='password'
                                         )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            auth = 'Bearer ' + auth_token
            u_id = data['data']['user_id']

            # GET on the Users endpoint with the user's id
            response = api.get_user(self.client,
                                    u_id=u_id,
                                    auth=auth
                               )
            assert response.status_code != http.UNAUTH and response.status_code != http.NOT_FOUND

    def test_patch(self):
        # register a user
        response = api.register_user(self.client, 
                                     email='goofy@goober.com',
                                     password='password'
                                     )
        data = json.loads(response.data.decode())
        auth_token = data['auth_token']
        auth = 'Bearer ' + auth_token
        u_id = data['data']['user_id']
        
        # PATCH on the Users endpoint with user's id
        response = api.patch_user(self.client,
                                  u_id=u_id,
                                  auth=auth
                                  )
        assert response.status_code != http.UNAUTH and response.status_code != http.NOT_FOUND

    def test_delete(self):
        # register a user
        response = api.register_user(self.client, 
                                     email='goofy@goober.com',
                                     password='password'
                                     )
        data = json.loads(response.data.decode())
        auth_token = data['auth_token']
        auth = 'Bearer ' + auth_token
        u_id = data['data']['user_id']

        # DELETE on the Users endpoint with the user's id
        response = api.delete_user(self.client,
                                   u_id=u_id,
                                   auth=auth
                                   )
        assert response.status_code != http.UNAUTH and response.status_code != http.NOT_FOUND
