from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

from datetime import datetime, timedelta
import json
import StringIO
import os

DELETE_THRESHOLD = -4

class TestPatchBanVideos(GimTestCase.GimFreshDBTestCase):
    def test_downvote_ban(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            v_id = videos_api.post_video_quick(self.client, auth=auth)

            # keep downvoting the video until the video has a score below threshold
            for i in range(abs(DELETE_THRESHOLD - 1)):
                response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
                assert response.status_code == http.OK

                email='goofy' + str(i) + '@goober.com'
                auth, u_id = users_api.register_user_quick(self.client, email=email)
                videos_api.downvote_video(self.client, v_id, auth)

            
            # test video is not found
            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.NOT_FOUND

    def test_flag_ban(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            v_id = videos_api.post_video_quick(self.client, auth=auth)

            # keep flagging the video until the video has a score below threshold
            for i in range(abs(DELETE_THRESHOLD) / 2 + 1):
                response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
                assert response.status_code == http.OK

                email='goofy' + str(i) + '@goober.com'
                auth, u_id = users_api.register_user_quick(self.client, email=email)
                videos_api.flag_video(self.client, v_id, auth)
            
            # test video is not found
            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.NOT_FOUND

    def test_downvote_flag_ban(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            v_id = videos_api.post_video_quick(self.client, auth=auth)

            # keep downvoting the video until the video has a score below threshold
            for i in range(abs(DELETE_THRESHOLD) / 3 + 1):
                response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
                assert response.status_code == http.OK

                email='goofy' + str(i) + '@goober.com'
                auth, u_id = users_api.register_user_quick(self.client, email=email)
                videos_api.downvote_video(self.client, v_id, auth)
                videos_api.flag_video(self.client, v_id, auth)

            
            # test video is not found
            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.NOT_FOUND

    def test_upvote_ban(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            v_id = videos_api.post_video_quick(self.client, auth=auth)

            # keep downvoting the video until the video has a score below threshold
            for i in range(abs(DELETE_THRESHOLD - 1)):
                response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
                assert response.status_code == http.OK

                email='goofy' + str(i) + '@goober.com'
                auth, u_id = users_api.register_user_quick(self.client, email=email)
                videos_api.upvote_video(self.client, v_id, auth)

            
            # test video is not found
            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.OK

    def test_ban_file_retrieval(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            v_id = videos_api.post_video_quick(self.client, auth=auth)
            videos_api.ban_videos(self.client, [v_id])

            # check that banned video is no longer stored in the videos ftp directory
            response = videos_api.get_video(self.client, v_id, auth=auth)
            assert response.status_code == http.NOT_FOUND
            response = videos_api.get_video_file(self.client, v_id, auth=auth)
            assert response.status_code == http.NOT_FOUND
            
            # check that banned video is located in the banned ftp directory
            response_user = users_api.get_user_status(self.client, auth=auth)
            data = json.loads(response_user.data.decode())
            bv_id = data['data']['warning_id']
            response = videos_api.get_banned_video(self.client, bv_id, auth=auth)
            assert response.status_code == http.OK
            response = videos_api.get_banned_video_file(self.client, bv_id, auth=auth)
            assert response.status_code == http.OK

    def test_ban_file_data(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            contents = "akfdhlkjghkjghdsglj"
            tags = ['this', 'is', 'testing']
           
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

            # delete file
            videos_api.ban_videos(self.client, [v_id])
            response_user = users_api.get_user_status(self.client, auth=auth)  
            data = json.loads(response_user.data.decode())          
            bv_id = data['data']['warning_id']

            # check banned video metadata
            response = videos_api.get_banned_video(self.client, bv_id, auth=auth)
            data = json.loads(response.data.decode())
            assert response.status_code == http.OK
            assert data['data']['user_id'] == u_id
            assert data['data']['lat'] == 0.0
            assert data['data']['lon'] == 0.0
            assert datetime.strptime(data['data']['uploaded_on'], '%a, %d %b %Y %H:%M:%S %Z') < datetime.now()
            assert set(data['data']['tags']) == set(tags)
            assert data['data']['user_warned'] == True

            # GET banned video file
            response = videos_api.get_banned_video_file(self.client, bv_id, auth=auth)
            assert response.status_code == http.OK
            assert response.data == contents

    def test_ban_bad_get(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            v_id = videos_api.post_video_quick(self.client, auth=auth)

            # check no video is fetched for get banned video request
            response = videos_api.get_banned_video(self.client, 1, auth=auth)
            assert response.status_code == http.NOT_FOUND
            response = videos_api.get_banned_video_file(self.client, 1, auth=auth)
            assert response.status_code == http.NOT_FOUND

