from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO
import os

class TestPatchFlagVideos(GimTestCase.GimFreshDBTestCase):
    def test_patch_flag(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # Check flagging without existing vote
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth
                                               )

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=False,
                                               flagged=True
                                               )
            assert response.status_code == http.OK

            # test no effect on vote
            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 0

            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_vote'] == 0

    def test_patch_upvote_flag(self):
        with self.client:
            # Register users
            auth, u_id = users_api.register_user_quick(self.client)

            # Check flagging with existing upvote
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth
                                               )

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=True,
                                               flagged=False
                                               )
            assert response.status_code == http.OK

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=False,
                                               flagged=True
                                               )
            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 1
            assert data['data']['downvotes'] == 0

            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_vote'] == 1

    def test_patch_downvote_flag(self):
        with self.client:
            # Register users
            auth, u_id = users_api.register_user_quick(self.client)

            # Check flagging with existing upvote
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth
                                               )

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=False,
                                               flagged=False
                                               )
            assert response.status_code == http.OK

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=False,
                                               flagged=True
                                               )
            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1

            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_vote'] == -1
