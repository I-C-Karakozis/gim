from tests import GimTestCase
from tests import user_helpers as api
from tests import video_helpers as video_api
from tests import http_helpers as http

import json
from datetime import datetime

class TestUsers_ApiCalls(GimTestCase.GimFreshDBTestCase):
    # test user data return as expected
    def test_get_valid(self):
        with self.client:
            # register a user
            auth, u_id = api.register_user_quick(self.client)
            
            
            response = api.get_user(self.client,
                                    u_id = u_id,
                                    auth = auth
                               )            
            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['email'] == 'goofy@goober.com'
            assert data['data']['score'] == 0
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
            auth, u_id = api.register_user_quick(self.client)
            
            response = api.get_user(self.client,
                                    u_id = 100,
                                    auth = auth
                                )

            data = json.loads(response.data.decode())
            assert response.status_code == http.UNAUTH

    def test_get_invalid_auth(self):
        with self.client:
            # register a user
            auth, u_id = api.register_user_quick(self.client)
            auth2, u_id2 = api.register_user_quick(self.client,
                                                   email='goof@goober.com'
                                                   )
            
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

    def test_get_score(self):
        with self.client:
            auth1, u_id1 = api.register_user_quick(self.client,
                                                   email="gim@gim.com"
                                                   )
            auth2, u_id2 = api.register_user_quick(self.client,
                                                   email="gim2@gim.com"
                                                   )

            # user 1 posts video
            v_id = video_api.post_video_quick(self.client,
                                              auth=auth1
                                              )

            # user 2 upvotes
            video_api.upvote_video(self.client,
                                   v_id,
                                   auth=auth2
                                   )

            response = api.get_user(self.client,
                                    u_id1,
                                    auth=auth1
                                    )

            # score should be 1 (1 upvote, 0 votes)
            data = json.loads(response.data.decode())
            assert response.status_code == http.OK
            assert data['data']['score'] == 1

            # user 1 upvotes
            video_api.upvote_video(self.client,
                                   v_id,
                                   auth=auth1
                                   )
            
            response = api.get_user(self.client,
                                    u_id1,
                                    auth=auth1
                                    )
            
            data = json.loads(response.data.decode())

            # score should be 3 (2 upvotes, 1 vote)
            assert response.status_code == http.OK
            assert data['data']['score'] == 3

            # user 2 downvotes
            video_api.downvote_video(self.client,
                                     v_id,
                                     auth=auth2
                                     )

            response = api.get_user(self.client,
                                    u_id1,
                                    auth=auth1
                                    )

            data = json.loads(response.data.decode())

            # score should be 1 (1 upvote, 1 downvote, 1 vote)
            assert response.status_code == http.OK
            assert data['data']['score'] == 1

    def test_delete_valid(self):
        with self.client:
            # register a user
            auth, u_id = api.register_user_quick(self.client)
            
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!'
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
            auth, u_id = api.register_user_quick(self.client)
            
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
            auth, u_id = api.register_user_quick(self.client)
            
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
            auth, u_id = api.register_user_quick(self.client)
            
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
            auth, u_id = api.register_user_quick(self.client)
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!',
                                       new_password = 'new_password1!'
                                    )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'new_password1!',
                                       new_password = 'password1!'
                                    )
            assert response.status_code == http.OK

    def test_patch_valid_testInvalidOldPassword(self):
        with self.client:
            # register a user
            response = api.register_user(self.client, 
                                         email='goofy@goober.com',
                                         password='password1!'
                                         )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            auth = 'Bearer ' + auth_token
            u_id = data['data']['user_id']
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!',
                                       new_password = 'new_password1!'
                                    )

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            # attempt to delete user with old password
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!'
                                    )
            assert response.status_code == http.UNAUTH

    def test_patch_invalid_password(self):
        with self.client:
            # register a user
            auth, u_id = api.register_user_quick(self.client)
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'passwordd',
                                       new_password = 'hihello1!'
                                    )

            assert response.status_code == http.UNAUTH

            # test old password still provides accessibility
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!'
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
                                         password='password1!'
                                         )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            auth = 'Bearer ' + auth_token
            u_id = data['data']['user_id']
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       new_password = 'new_password1!'
                                    )
            assert response.status_code == http.BAD_REQ

            # test old password still provides accessibility
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!'
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
            auth, u_id = api.register_user_quick(self.client) 
            
            response = api.patch_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!'
                                    )
            assert response.status_code == http.BAD_REQ

            # test old password still provides accessibility
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!'
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
            auth, u_id = api.register_user_quick(self.client)
            
            response = api.patch_user(self.client,
                                       u_id = 5,
                                       auth = auth,
                                       password = 'password1!',
                                       new_password = 'new_password1!'
                                       )
            assert response.status_code == http.UNAUTH

            # test old password still provides accessibility
            response = api.delete_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                       password = 'password1!'
                                    )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_id'] == u_id

            response = api.get_user(self.client,
                                       u_id = u_id,
                                       auth = auth,
                                    )
            assert response.status_code == http.NOT_FOUND

