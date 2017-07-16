from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO
import os

DELETE_THRESHOLD = -4

class TestPatchBanVideos(GimTestCase.GimFreshDBTestCase):
    def test_downvote_ban(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth
                                                   )

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
            v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth
                                                   )

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
            v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth
                                                   )

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
            v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth
                                                   )

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