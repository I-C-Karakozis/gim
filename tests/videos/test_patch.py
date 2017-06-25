from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO
import os

class TestPatchVideos(GimTestCase.GimFreshDBTestCase):
    def test_patch_upvote(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST a video
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
           
            data = json.loads(response.data.decode())
            assert data['data']['video_id'] == v_id
            assert data['data']['upvotes'] == 1
            assert data['data']['downvotes'] == 0

            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 1
            assert data['data']['downvotes'] == 0
            assert data['data']['user_vote'] == 1

    def test_patch_downvote(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST a video
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
           
            data = json.loads(response.data.decode())
            assert data['data']['video_id'] == v_id
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1

            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1
            assert data['data']['user_vote'] == -1


    def test_patch_not_owner(self): 
        with self.client:
            # Register two users
            auth1, u_id1 = users_api.register_user_quick(self.client,
                                                         email='gim@gim.com'
                                                         )
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email='gim2@gim.com'
                                                         )

            # POST a video with user 1
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth1
                                               )

            # vote video with user 2
            response = videos_api.patch_video(self.client,
                                       v_id,
                                       auth=auth2,
                                       upvote=False,
                                       flagged=False
                                       )

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1

            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth1
                                            )

            assert response.status_code == http.OK

            # check that a user who did not vote the video gets signal that he has not voted
            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1
            assert data['data']['user_vote'] == 0

    def test_patch_vote_non_existent_video(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)

            response = videos_api.patch_video(self.client,
                                       5,
                                       auth=auth,
                                       upvote=False,
                                       flagged=False
                                       )

            assert response.status_code == http.UNAUTH


    def test_patch_no_data(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)

            # POST a video with user
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth
                                               )

            response = videos_api.patch_video(self.client,
                                       v_id,
                                       auth=auth
                                       )

            assert response.status_code == http.UNAUTH

            response = videos_api.patch_video(self.client,
                                       v_id,
                                       auth=auth,
                                       flagged=True
                                       )

            assert response.status_code == http.UNAUTH

            response = videos_api.patch_video(self.client,
                                       v_id,
                                       auth=auth,
                                       upvote=True
                                       )

            assert response.status_code == http.UNAUTH

    def test_patch_double_upvote(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST a video
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
                                               upvote=True,
                                               flagged=False
                                               )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 0

            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )
            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 0
            assert data['data']['user_vote'] == 0

    def test_patch_double_downvote(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST a video
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
                                               flagged=False
                                               )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 0

            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.OK
                           
            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 0
            assert data['data']['user_vote'] == 0
           

    def test_patch_upvote_downvote(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST a video
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
                                               flagged=False
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

    def test_patch_downvote_upvote(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST a video
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
                                               upvote=True,
                                               flagged=False
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

    def test_patch_upvote_flag(self):
        with self.client:
            # Register a user
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
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1

            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['user_vote'] == -1

    def test_patch_flag_unexpected_json(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)

            # Check flagging with existing upvote
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth
                                               )

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=True,
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
