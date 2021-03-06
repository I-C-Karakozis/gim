'''
These tests are heavily based on https://realpython.com/blog/python/token-based-authentication-with-flask
'''

from tests import GimTestCase
from tests import user_helpers as api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json

from app.mod_api import models

class TestAuth(GimTestCase.GimFreshDBTestCase):
    def test_user_status(self):
        with self.client:
            response_register = api.register_user(self.client,
                                                  email='test@test.com',
                                                  password='password1!'
                                                  )
            auth_token = json.loads(response_register.data.decode())['auth_token']

            response_user = api.get_user_status(self.client,
                                         auth='Bearer ' + auth_token)
            assert response_user.status_code == http.OK
            data = json.loads(response_user.data.decode())
            assert data['status'] == 'success'
            assert data['data']['user_id'] > 0
            assert len(data['data']['warning_ids']) == 0
            assert data['data']['vote_restricted'] == False
            assert data['data']['post_restricted'] == False

    def test_bad_token_status(self):
        with self.client:
            response_user = api.get_user_status(self.client,
                                         auth='Bearer ' + 'asdfghjkl')            
            assert response_user.status_code == http.UNAUTH
            data = json.loads(response_user.data.decode())
            assert data['status'] == 'failed'

    def test_status_banned_video_warning(self):
        with self.client:
            # ban video of user
            auth, u_id = api.register_user_quick(self.client)
            v_id = videos_api.post_video_quick(self.client, auth=auth)
            videos_api.ban_videos(self.client, [v_id])

            # check if warning id is returned
            response_user = api.get_user_status(self.client, auth=auth)
            data = json.loads(response_user.data.decode())
            assert response_user.status_code == http.OK
            assert data['data']['vote_restricted'] == False
            assert data['data']['post_restricted'] == False
            assert len(data['data']['warning_ids']) == 1

            # check that warning is not issued twice
            response_user = api.get_user_status(self.client, auth=auth)
            data = json.loads(response_user.data.decode())
            assert response_user.status_code == http.OK
            assert data['data']['vote_restricted'] == False
            assert data['data']['post_restricted'] == False
            assert len(data['data']['warning_ids']) == 0

    def test_status_multiple_banned_video_warning(self):
        with self.client:
            # ban two videos of user
            auth, u_id = api.register_user_quick(self.client)
            v_id1 = videos_api.post_video_quick(self.client, auth=auth)
            v_id2 = videos_api.post_video_quick(self.client, auth=auth, content='fu')
            videos_api.ban_videos(self.client, [v_id1, v_id2])

            # check if warning id is returned
            response_user = api.get_user_status(self.client, auth=auth)
            assert response_user.status_code == http.OK
            data = json.loads(response_user.data.decode())
            assert len(data['data']['warning_ids']) == 2
            id1 = data['data']['warning_ids'][0]
            id2 = data['data']['warning_ids'][1]
            assert id1 >= 0            
            assert id2 >= 0
            assert id1 != id2

            response_user = api.get_user_status(self.client, auth=auth)            
            assert response_user.status_code == http.OK
            data = json.loads(response_user.data.decode())
            assert len(data['data']['warning_ids']) == 0
            
    def test_status_banned_user(self):
        with self.client:
            # ban video of user
            auth, u_id = api.register_user_quick(self.client)
            api.ban_user(self.client, auth)

            response_user = api.get_user_status(self.client, auth=auth)
            data = json.loads(response_user.data.decode())
            assert response_user.status_code == http.OK
            assert len(data['data']['warning_ids']) == 3
            assert data['data']['vote_restricted'] == True
            assert data['data']['post_restricted'] == True
            
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
            
