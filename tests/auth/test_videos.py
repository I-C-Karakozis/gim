from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json

class TestVideos(GimTestCase.GimFreshDBTestCase):
    def test_get_all(self):
        with self.client:
            # register a user
            response = users_api.register_user(self.client, 
                                         email='goofy@goober.com',
                                         password='password'
                                         )
            data = json.loads(response.data.decode())
            auth_token = data['auth_token']
            auth = 'Bearer ' + auth_token
            u_id = data['data']['user_id']
            
            # GET on Videos endpoint
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth
                                                 )
            assert response.status_code != http.UNAUTH 
            assert response.status_code != http.NOT_FOUND

    def test_post(self):
        # register a user
        response = users_api.register_user(self.client, 
                                           email='goofy@goober.com',
                                           password='password'
                                           )
        data = json.loads(response.data.decode())
        auth_token = data['auth_token']
        auth = 'Bearer ' + auth_token
        u_id = data['data']['user_id']
        
        # POST on Videos endpoint
        response = videos_api.post_video(self.client,
                                         auth=auth
                                         )
        assert response.status_code != http.UNAUTH
        assert response.status_code != http.NOT_FOUND
