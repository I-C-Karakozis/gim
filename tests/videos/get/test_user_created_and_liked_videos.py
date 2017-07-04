from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO
import os

class TestGetVideos(GimTestCase.GimFreshDBTestCase):
    def test_get_nonexistent_user_videos(self):
        with self.client:
            # Register two users
            auth1, u_id1 = users_api.register_user_quick(self.client,
                                                         email='gim@gim.com'
                                                         )
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email='gim2@gim.com'
                                                         )

            v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth2
                                                   )
            
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='created',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent'
                                                 )

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            
            assert response.status_code == http.OK
            assert len(videos) == 0  

    def test_get_user_videos_by_recency(self):
        with self.client:
            contents = ['a', 'b', 'c', 'd', 'e']
            auth1, u_id1 = users_api.register_user_quick(self.client)
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                    email='gim2@gim.com'
                                                    )

            video_ids = {}
            for content in contents:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth1
                                                   )
                video_ids[content] = v_id

            v_id = videos_api.post_video_quick(self.client,
                                                auth=auth2
                                                )
            
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='created',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent'
                                                 )
            data = json.loads(response.data.decode())

            intended_order = [video_ids[content] for content in reversed(contents)]
            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == 5
            assert returned_order == intended_order

            # check whether default option persists
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth2,
                                                 tags=[],
                                                 feedType='created',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='asdf'
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == 1
            assert v_id == data['data']['videos'][0]['video_id']

    def test_get_user_videos_by_popularity(self):
        with self.client:
            contents = ['a', 'b', 'c', 'd', 'e']
            net_votes = [0, -1, 1, 2, -2]
            auth1, u_id1 = users_api.register_user_quick(self.client,
                                                         email='gim@gim.com'
                                                         )
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email='gim2@gim.com'
                                                         )

            video_ids = []
            for content in contents:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth1
                                                   )
                video_ids.append(v_id)

            # upvote videos according to net_votes
            auths = (auth1, auth2)
            for net_vote, video_id in zip(net_votes, video_ids):
                upvotes = max(net_vote, 0)
                downvotes = abs(min(net_vote, 0))
                for i in range(upvotes):
                    videos_api.upvote_video(self.client,
                                            video_id,
                                            auth=auths[i]
                                            )
                for j in range(downvotes):
                    videos_api.downvote_video(self.client,
                                              video_id,
                                              auth=auths[-(j+1)]
                                              )
            
            intended_order = map(lambda x: x[1], 
                                 sorted(zip(net_votes, video_ids),
                                        cmp=lambda x, y: x[0] - y[0],
                                        reverse=True
                                        )
                                 ) 

            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='created',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='popular'
                                                 )
            data = json.loads(response.data.decode())

            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert returned_order == intended_order
            assert len(data['data']['videos']) == 5

    def test_get_liked_videos_no_votes(self):
        with self.client:
            # Register two users
            auth1, u_id1 = users_api.register_user_quick(self.client,
                                                         email='gim@gim.com'
                                                         )
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email='gim2@gim.com'
                                                         )

            v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth2
                                                   )
            
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='liked',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent'
                                                 )

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            
            assert response.status_code == http.OK
            assert len(videos) == 0 

            response = videos_api.get_all_videos(self.client,
                                                 auth=auth2,
                                                 tags=[],
                                                 feedType='liked',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent'
                                                 )

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            
            assert response.status_code == http.OK
            assert len(videos) == 0  

    def test_get_liked_videos_single_upvote(self):
        with self.client:
            # Register two users
            auth1, u_id1 = users_api.register_user_quick(self.client,
                                                         email='gim@gim.com'
                                                         )
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email='gim2@gim.com'
                                                         )

            v_id1 = videos_api.post_video_quick(self.client,
                                                   auth=auth2
                                                   )

            v_id2 = videos_api.post_video_quick(self.client,
                                                   auth=auth1
                                                   )

            videos_api.upvote_video(self.client,
                                   v_id1,
                                   auth=auth1
                                   )

            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='liked',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent'
                                                 )

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            
            assert response.status_code == http.OK
            assert len(videos) == 1  
            assert v_id1 == data['data']['videos'][0]['video_id']

    def test_get_liked_videos_mixed_votes_by_recency(self):
        with self.client:
            upvoted = ['a', 'b', 'c']
            downvoted = ['d', 'e']
            auth1, u_id1 = users_api.register_user_quick(self.client)
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                    email='gim2@gim.com'
                                                    )

            video_ids = list()
            for content in upvoted:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth2
                                                   )
                video_ids.append(v_id)

            # like videos in reverse order than the one posted
            for v_id in reversed(video_ids):
                videos_api.upvote_video(self.client,
                                   v_id,
                                   auth=auth1
                                   )


            for content in downvoted:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth2
                                                   )
                videos_api.downvote_video(self.client,
                                   v_id,
                                   auth=auth1
                                   )

            # check whether default option persists
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='liked',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='asdf'
                                                 )

            # ensure videos are in the order of the most recently liked to the least recently liked
            data = json.loads(response.data.decode())
            intended_order = [v_id for v_id in video_ids]
            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == 3
            assert returned_order == intended_order

            response = videos_api.get_all_videos(self.client,
                                                 auth=auth2,
                                                 tags=[],
                                                 feedType='liked',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent'
                                                 )

            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == 0

    def test_get_liked_videos_by_popularity(self):
        with self.client:
            contents = ['a', 'b', 'c', 'd', 'e']
            net_votes = [0, -1, 1, 2, -2]
            auth1, u_id1 = users_api.register_user_quick(self.client,
                                                         email='gim@gim.com'
                                                         )
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email='gim2@gim.com'
                                                         )

            video_ids = []
            for content in contents:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth1
                                                   )
                video_ids.append(v_id)

            # upvote videos according to net_votes
            auths = (auth1, auth2)
            for net_vote, video_id in zip(net_votes, video_ids):
                upvotes = max(net_vote, 0)
                downvotes = abs(min(net_vote, 0))
                for i in range(upvotes):
                    videos_api.upvote_video(self.client,
                                            video_id,
                                            auth=auths[i]
                                            )
                for j in range(downvotes):
                    videos_api.downvote_video(self.client,
                                              video_id,
                                              auth=auths[-(j+1)]
                                              )
            
            intended_order = [video_ids[3], video_ids[2]] 

            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='liked',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='popular'
                                                 )
            data = json.loads(response.data.decode())

            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert returned_order == intended_order
            assert len(data['data']['videos']) == 2
