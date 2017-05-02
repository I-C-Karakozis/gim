from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import hof_helpers as hof_api
from tests import cron_helpers as cron
from tests import http_helpers as http

import json
import StringIO

CAP = 10

class TestHallOfFame(GimTestCase.GimFreshDBTestCase):    
    def test_get_hof_video(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client, auth=auth)

            cron.delete_expired()

            response = hof_api.get_all_hof_videos(self.client, auth)

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            
            assert len(videos) == 1
            assert videos[0]['score'] == 0

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
            # CAP is the current cap
            desc_scores, auths = cron.simulate_hof(self.client, CAP)
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
            # CAP is the current cap
            desc_scores, auths = cron.simulate_hof(self.client, CAP)
            desc_scores.sort(reverse=True)
            cron.delete_expired()

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)

            response = hof_api.get_all_hof_videos(self.client, auth)

            assert response.status_code == http.OK

            # get old
           
            # POST to Videos endpoint
            v_id = videos_api.post_video_quick(self.client, auth=auth)

            # create 11th top video w/ 11 upvotes
            videos_api.upvote_video(self.client, v_id, auth)
            for user in auths:
                videos_api.upvote_video(self.client, v_id, user)

            cron.delete_expired()

            response = hof_api.get_all_hof_videos(self.client, auth)

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            print len(videos)
            assert len(videos) == CAP
            assert videos[0]['score'] == CAP + 1

            # check scores and sorted order
            del desc_scores[len(desc_scores) - 1]
            descscores.append(CAP + 1)
            desc_scores = desc_scores.sort(reverse=True)
            for vid, score in zip(videos, desc_scores):
                assert vid['score'] == score