from app import app
from app import video_client
from app.mod_api import models
from app.mod_api.delete_expired_videos import delete_expired_videos

from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import time
import datetime
import StringIO
import json

class TestDeleteExpiredVideos(GimTestCase.GimFreshDBTestCase):
    def test_delete_single_expired_video(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)

            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client,
                                                auth=auth
                                                )

            # compute time threshold            
            diff = datetime.timedelta(seconds = 1)
            time.sleep(3)
            now = datetime.datetime.now()
            threshold_datetime = now - diff

            delete_expired_videos(threshold_datetime)

            # GET on Videos endpoint, expect not found
            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

    def test_delete_multiple_expired_videos(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)

            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client,
                                                auth=auth
                                                )
            response = videos_api.post_video(self.client, auth, 
                                            video=StringIO.StringIO('yannis'),
                                            tags=['the', 'sitting', 'dead'],
                                            lat=0.0,
                                            lon=0.0
                                            )

            data = json.loads(response.data.decode())
            v_id2 = data['data']['video_id']
            
            # compute time threshold
            diff = datetime.timedelta(seconds = 1)
            time.sleep(3)
            now = datetime.datetime.now()
            threshold_datetime = now - diff

            delete_expired_videos(threshold_datetime)

            # GET on Videos endpoint, expect not found
            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            # print json.loads(response.data.decode())
            assert response.status_code == http.NOT_FOUND

            # GET on Videos endpoint, expect not found
            response = videos_api.get_video(self.client,
                                            v_id2,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

    def test_delete_not_non_expired_videos(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)

            response = videos_api.post_video(self.client, auth, 
                                            video=StringIO.StringIO('yannis'),
                                            tags=['the', 'sitting', 'dead'],
                                            lat=0.0,
                                            lon=0.0
                                            )

            data = json.loads(response.data.decode())
            v_id2 = data['data']['video_id']
            
            assert response.status_code == http.OK
            
            # compute time threshold
            diff = datetime.timedelta(seconds = 1)
            time.sleep(2)
            v_id = videos_api.post_video_quick(self.client,
                                                auth=auth
                                                )
            now = datetime.datetime.now()
            threshold_datetime = now - diff

            delete_expired_videos(threshold_datetime)

            # GET on Videos endpoint, expect found
            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.OK

            # GET on Videos endpoint, expect not found
            response = videos_api.get_video(self.client,
                                            v_id2,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

    def test_delete_expired_videos_check_votes(self):
        with self.client:
            # register two users
            auth, u_id = users_api.register_user_quick(self.client, email='gim@gim.com')
            auth2, u_id2 = users_api.register_user_quick(self.client, email='gim2@gim.com')

            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client,
                                                auth=auth
                                                )

            # vote the video twice
            response = videos_api.patch_video(self.client,
                                            v_id,
                                            auth=auth,
                                            upvote=True
                                            )
            assert response.status_code == http.OK

            response = videos_api.patch_video(self.client,
                                            v_id,
                                            auth=auth2,
                                            upvote=True
                                            )
            assert response.status_code == http.OK

            # compute time threshold
            diff = datetime.timedelta(seconds = 1)
            time.sleep(3)
            now = datetime.datetime.now()
            threshold_datetime = now - diff

            delete_expired_videos(threshold_datetime)           

            expired_votes = models.Vote.query.filter_by(v_id = v_id)

            assert len(expired_votes.all()) == 0

    def test_delete_expired_videos_check_tags(self):
        with self.client:
            pass # it should cascade from video.delete(); check manually on the mysql database


    def test_delete_expired_videos_check_file_system(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)

            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client,
                                                auth=auth
                                                )

            videos = models.Video.query.filter_by(v_id = v_id)

            # compute time threshold
            diff = datetime.timedelta(seconds = 1)
            time.sleep(3)
            now = datetime.datetime.now()
            threshold_datetime = now - diff

            delete_expired_videos(threshold_datetime)
            
            video = video_client.retrieve_videos([video.filepath for video in videos])
            assert len(video) == 0

