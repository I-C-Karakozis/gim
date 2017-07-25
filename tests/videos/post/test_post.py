from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO
import os

class TestPostVideos(GimTestCase.GimFreshDBTestCase):
    def test_post(self):
        with self.client:
            contents = "akfdhlkjghkjghdsglj"
            tags = ['this', 'is', 'testing']

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=tags,
                                             lat=0.0,
                                             lon=0.0,
                                             )

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            v_id = data['data']['video_id']

            assert v_id > 0

    def test_post_correct_android_files(self):
        with self.client:
            contents = "akfdhlkjghkjghdsglj"
            tags = ['this', 'is', 'testing']

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=tags,
                                             lat=0.0,
                                             lon=0.0,
                                             filename='video.mov'
                                             )

            assert response.status_code == http.OK

            # POST to Videos endpoint
            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=tags,
                                             lat=0.0,
                                             lon=0.0,
                                             filename='video.mp4'
                                             )

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            v_id = data['data']['video_id']

            assert v_id > 0

            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=tags,
                                             lat=0.0,
                                             lon=0.0,
                                             filename='video.3gp'
                                             )

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            v_id = data['data']['video_id']

            assert v_id > 0

    def test_post_incorrect_android_files(self):
        with self.client:
            contents = "akfdhlkjghkjghdsglj"
            tags = ['this', 'is', 'testing']

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=tags,
                                             lat=0.0,
                                             lon=0.0,
                                             filename='video'
                                             )

            assert response.status_code == http.BAD_REQ

            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=tags,
                                             lat=0.0,
                                             lon=0.0,
                                             filename='video.asdf'
                                             )

            assert response.status_code == http.BAD_REQ

    def test_post_102MB_file(self):
        with self.client:
            # limit is currently 100MB
            length = 102 * 1024 * 1024

            file = open('102MB.mov', 'w')
            for i in range(length):
                file.write('a')
            file.close()

            file = open('102MB.mov', 'r')
            contents = file.read()
            file.close()
            os.system('rm 102MB.mov')

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=[],
                                             lat=0.0,
                                             lon=0.0
                                             )

            assert response.status_code == http.FILE_TOO_LARGE

    def test_post_banned_user(self):
        with self.client:
            # ban user
            auth, u_id = users_api.register_user_quick(self.client)
            users_api.ban_user(self.client, auth)

            # POST to Videos endpoint
            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO('abba'),
                                             tags=[],
                                             lat=0.0,
                                             lon=0.0
                                             )
            assert response.status_code == http.UNAUTH
            data = json.loads(response.data.decode())
            assert data['message'] == 'Posting Restricted.'
