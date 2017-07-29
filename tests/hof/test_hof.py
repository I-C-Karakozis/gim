from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import hof_helpers as hof_api
from tests import cron_helpers as cron
from tests import http_helpers as http

from app import app

import json
import StringIO

class TestHallOfFame(GimTestCase.GimFreshDBTestCase):    
    def test_get_hof_video(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)            
            contents = "akfdhlkjghkjghdsglj"
           
            # POST to Videos endpoint
            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=[],
                                             lat=0.0,
                                             lon=0.0,
                                             )

            data = json.loads(response.data.decode())
            v_id = data['data']['video_id']

            cron.delete_expired()

            response = hof_api.get_all_hof_videos(self.client, auth)

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            hof_id = videos[0]['video_id']
            
            assert len(videos) == 1
            assert videos[0]['score'] == 0

            # test video file has been deleted
            response = videos_api.get_video_file(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

            # test video data have been deleted
            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

            # test hof video file is available
            response = hof_api.get_video_file(self.client,
                                            hof_id,
                                            auth=auth
                                            )

            assert response.status_code == http.OK
            assert response.data == contents

            # test thumbnail has not been deleted
            response = hof_api.get_thumbnail(self.client,
                                            hof_id,
                                            auth=auth
                                            )

            assert response.status_code == http.OK  

    def test_get_empty_hof(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            response = hof_api.get_all_hof_videos(self.client, auth)

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            videos = data['data']['videos']            
            assert len(videos) == 0

    def test_get_hof_video_not_owner(self):
        with self.client:
            # register users
            auth1, u_id1 = users_api.register_user_quick(self.client, email='gim@gim.com')
            auth2, u_id2 = users_api.register_user_quick(self.client, email='gim2@gim2.com')

            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client, auth=auth1)

            cron.delete_expired()

            response = hof_api.get_all_hof_videos(self.client, auth2)

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            videos = data['data']['videos']            
            assert len(videos) == 1
            assert videos[0]['score'] == 0

    def test_get_hof_video_score_calculations_multiple_upvotes(self):
        with self.client:
            # register users
            auth1, u_id1 = users_api.register_user_quick(self.client, email='gim@gim.com')
            auth2, u_id2 = users_api.register_user_quick(self.client, email='gim2@gim2.com')
            
            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client, auth=auth1)

            videos_api.upvote_video(self.client, v_id, auth1)
            videos_api.upvote_video(self.client, v_id, auth2)

            cron.delete_expired()

            response = hof_api.get_all_hof_videos(self.client, auth1)

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            assert len(videos) == 1
            assert videos[0]['score'] == 2

    def test_get_hof_video_score_calculations_multiple_downvotes(self):
        with self.client:
            # register users
            auth1, u_id1 = users_api.register_user_quick(self.client, email='gim@gim.com')
            auth2, u_id2 = users_api.register_user_quick(self.client, email='gim2@gim2.com')

            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client, auth=auth1)

            videos_api.downvote_video(self.client, v_id, auth1)
            videos_api.downvote_video(self.client, v_id, auth2)

            cron.delete_expired()

            response = hof_api.get_all_hof_videos(self.client, auth1)

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            assert len(videos) == 1
            assert videos[0]['score'] == -2

    def test_get_hof_video_score_calculations_mixed_vote(self):
        with self.client:
            # register users
            auth1, u_id1 = users_api.register_user_quick(self.client, email='gim@gim.com')
            auth2, u_id2 = users_api.register_user_quick(self.client, email='gim2@gim2.com')

            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client, auth=auth1)

            videos_api.upvote_video(self.client, v_id, auth1)
            videos_api.downvote_video(self.client, v_id, auth2)

            cron.delete_expired()

            response = hof_api.get_all_hof_videos(self.client, auth1)

            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            assert len(videos) == 1
            assert videos[0]['score'] == 0


    def test_get_sorted_multiple_hof_videos(self):
        with self.client:
            desc_scores, auths = cron.simulate_hof(self.client, app.config.get('HALL_OF_FAME_LIMIT'))
            desc_scores.sort(reverse=True)
            cron.delete_expired()

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)

            response = hof_api.get_all_hof_videos(self.client, auth)

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            
            assert len(videos) == len(desc_scores)

            # check scores and sorted order
            for vid, score in zip(videos, desc_scores):
                assert vid['score'] == score

    def test_updating_hof(self):
        with self.client:
            desc_scores, auths = cron.simulate_hof(self.client, app.config.get('HALL_OF_FAME_LIMIT'))
            desc_scores.sort(reverse=True)
            cron.delete_expired()

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)

            response = hof_api.get_all_hof_videos(self.client, auth)

            assert response.status_code == http.OK
            
            # create 11th top video w/ 11 upvotes
            v_id = videos_api.post_video_quick(self.client, auth=auth)            
            videos_api.upvote_video(self.client, v_id, auth)
            for user in auths:
                videos_api.upvote_video(self.client, v_id, user)

            cron.delete_expired()

            response = hof_api.get_all_hof_videos(self.client, auth)

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            hof_id = videos[0]['video_id']

            assert len(videos) == app.config.get('HALL_OF_FAME_LIMIT')
            assert videos[0]['score'] == app.config.get('HALL_OF_FAME_LIMIT') + 1

            # check scores and sorted order
            del desc_scores[len(desc_scores) - 1]
            desc_scores.append(app.config.get('HALL_OF_FAME_LIMIT') + 1)
            desc_scores.sort(reverse=True)
            for vid, score in zip(videos, desc_scores):
                assert vid['score'] == score

            # test video is removed
            response = videos_api.get_video_file(self.client,
                                            v_id,
                                            auth=auth
                                            )
            assert response.status_code == http.NOT_FOUND

            # test thumbnail has not been deleted
            response = hof_api.get_thumbnail(self.client,
                                            hof_id,
                                            auth=auth
                                            )
            assert response.status_code == http.OK

            # test hof video has been uploaded
            response = hof_api.get_video_file(self.client,
                                            hof_id,
                                            auth=auth
                                            )
            assert response.status_code == http.OK

    def test_score_carryover(self):
        with self.client:
            # register a user
            auth1, u_id1 = users_api.register_user_quick(self.client,
                                                         email="gim@gim.com"
                                                         )
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email="gim2@gim.com"
                                                         )

            # post a video by user
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth1
                                               )

            # upvote video
            videos_api.upvote_video(self.client,
                                    v_id,
                                    auth=auth1
                                    )
            videos_api.upvote_video(self.client,
                                    v_id,
                                    auth=auth2
                                    )

            # delete the video into the hall of fame
            cron.delete_expired()

            # check that user's score
            response = users_api.get_user(self.client,
                                          u_id1,
                                          auth=auth1
                                          )

            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert data['data']['score'] == 5

            response = users_api.get_user(self.client,
                                          u_id2,
                                          auth=auth2
                                          )

            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert data['data']['score'] == 1

    def test_score_not_in_hof(self):
        pass # TODO

