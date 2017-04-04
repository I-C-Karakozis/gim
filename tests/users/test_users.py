from tests import GimTestCase
from tests import user_helpers as api
from tests import http_helpers as http

import json
from datetime import datetime

class TestUsers_ApiCalls(GimTestCase.GimFreshDBTestCase):
    # test user data return as expected
    def test_get_valid(self):
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
            
            
            response = api.get_user(self.client,
                                    u_id = u_id,
                                    auth = auth
                               )            
            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['email'] =='goofy@goober.com'

            registered_on = datetime.strptime(data['data']['registered_on'], '%a, %d %b %Y %H:%M:%S %Z')
            response = api.get_user(self.client,
                                    u_id = u_id,
                                    auth = auth
                               )           
            registered_on2 = datetime.strptime(data['data']['registered_on'], '%a, %d %b %Y %H:%M:%S %Z')
            diff = registered_on2 - registered_on
            assert diff.total_seconds() == 0 

    def test_get_invalid_uid(self):
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
            
            response = api.get_user(self.client,
                                    u_id = 100,
                                    auth = auth
                                )

            data = json.loads(response.data.decode())
            assert response.status_code == http.UNAUTH

    def test_get_invalid_ayth(self):
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

            response = api.register_user(self.client, 
                                         email='goof@goober.com',
                                         password='password'
                                         )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            auth2 = 'Bearer ' + auth_token
            u_id2 = data['data']['user_id']
            
            response = api.get_user(self.client,
                                    u_id = u_id,
                                    auth = auth2
                                )

            data = json.loads(response.data.decode())
            assert response.status_code == http.UNAUTH

            response = api.get_user(self.client,
                                    u_id = u_id2,
                                    auth = auth
                                )

            data = json.loads(response.data.decode())
            assert response.status_code == http.UNAUTH

    def test_delete_valid(self):
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
            
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password'
                                    )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.NOT_FOUND

    def test_delete_invalid_password(self):
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
            
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'passwordd'
                                    )
            assert response.status_code == http.UNAUTH

            # test user still exists
            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.OK


    def test_delete_invalid_noPassword(self):
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
            
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth
                                    )
            assert response.status_code == http.BAD_REQ

            # test user still exists
            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.OK

    def test_delete_invalid_uid(self):
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
            
            response = api.delete_user(self.client,
                                       u_id = 5,
                                       auth = auth,
                                       password = 'password'
                                    )
            assert response.status_code == http.UNAUTH

            # test user still exists
            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.OK

    def test_patch_valid_testNewPassword(self):
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
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password',
                                       new_password = 'new_password'
                                    )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'new_password',
                                       new_password = 'password'
                                    )
            assert response.status_code == http.OK

    def test_patch_valid_testInvalidOldPassword(self):
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
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password',
                                       new_password = 'new_password'
                                    )

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            # attempt to delete user with old password
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password'
                                    )
            assert response.status_code == http.UNAUTH

    def test_patch_invalid_password(self):
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
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'passwordd',
                                       new_password = 'hi'
                                    )
            assert response.status_code == http.UNAUTH

            # test old password still provides accessibility
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password'
                                    )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.NOT_FOUND


    def test_patch_invalid_noPassword(self):
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
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       new_password = 'new_password'
                                    )
            assert response.status_code == http.BAD_REQ

            # test old password still provides accessibility
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password'
                                    )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.NOT_FOUND

    def test_patch_invalid_noNewPassword(self):
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
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password'
                                    )
            assert response.status_code == http.BAD_REQ

            # test old password still provides accessibility
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password'
                                    )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.NOT_FOUND


    def test_patch_invalid_uid(self):
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
            
            response = api.patch_user(self.client,
                                       u_id = 5,
                                       auth = auth,
                                       password = 'password',
                                       new_password = 'new_password'
                                       )
            assert response.status_code == http.UNAUTH

            # test old password still provides accessibility
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password'
                                    )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.NOT_FOUND






   

    
