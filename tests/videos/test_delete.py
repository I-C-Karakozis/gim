from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO
import os

class TestDeleteVideos(GimTestCase.GimFreshDBTestCase):
    def test_delete(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth
                                               )

            # DELETE video
            response = videos_api.delete_video(self.client,
                                               v_id,
                                               auth=auth
                                               )

            assert response.status_code == http.OK

            # GET on Videos endpoint, expect not found
            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

            # GET on VideoFiles endpoint, expect not found
            response = videos_api.get_video_file(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

                        # GET on Thumbnails endpoint
            response = videos_api.get_thumbnail(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

    def test_delete_not_owner(self):
        with self.client:
            # Register two users
            auth1, u_id1 = users_api.register_user_quick(self.client,
                                                         email='gim@gim.com'
                                                         )
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email='gim2@gim.com'
                                                         )
            # POST video as user 1
            v_id = videos_api.post_video_quick(self.client,
                                             auth=auth1
                                             )

            # DELETE video as user 2, expect unauthorized
            response = videos_api.delete_video(self.client,
                                               v_id,
                                               auth=auth2
                                               )
            
            assert response.status_code == http.UNAUTH
            
            # GET on Videos to make sure it is still there
            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth1
                                            )

            assert response.status_code == http.OK

            # GET on VideoFiles to make sure it is still there
            response = videos_api.get_video_file(self.client,
                                            v_id,
                                            auth=auth1
                                            )

            assert response.status_code == http.OK

            # GET on Thumbnails endpoint
            # response = videos_api.get_thumbnail(self.client,
            #                                 v_id,
            #                                 auth=auth1
            #                                 )

            # assert response.status_code == http.OK

    def test_delete_non_existent(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)

            # DELETE non-existent video, expect unauthorized
            response = videos_api.delete_video(self.client,
                                               v_id=9001,
                                               auth=auth
                                               )

            assert response.status_code == http.UNAUTH

    def test_double_delete(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST a video
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth
                                               )

            # DELETE video
            response = videos_api.delete_video(self.client,
                                               v_id,
                                               auth=auth
                                               )

            assert response.status_code == http.OK
            
            # DELETE video again, expect unauthorized
            response = videos_api.delete_video(self.client,
                                               v_id,
                                               auth=auth
                                               )

            assert response.status_code == http.UNAUTH