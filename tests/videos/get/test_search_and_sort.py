from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO
import os

class TestGetVideos(GimTestCase.GimFreshDBTestCase):
    def test_get_nonexistent_by_popularity(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='popular'
                                                 )

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            
            assert response.status_code == http.OK
            assert videos == []

    def test_get_nonexistent_by_recent(self):
        with self.client:
            auth, u_id = users_api.register_user_quick(self.client)
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent'
                                                 )

            data = json.loads(response.data.decode())
            videos = data['data']['videos']
            
            assert response.status_code == http.OK
            assert videos == []   

    def test_get_all_by_popularity(self):
        with self.client:
            auth1, auth2, intended_order = videos_api.generate_sample_feed(self.client, sortBy='popularity')            

            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='popular'
                                                 )
            data = json.loads(response.data.decode())
            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert returned_order == intended_order

            # check whether default option persists
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='asdf'
                                                 )
            data = json.loads(response.data.decode())
            
            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert returned_order == intended_order

    def test_get_all_by_recent(self):
        with self.client:
            contents = ['a', 'b', 'c', 'd', 'e']
            auth1, u_id1 = users_api.register_user_quick(self.client)
            
            video_ids = {}
            for content in contents:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth1
                                                   )
                video_ids[content] = v_id
            
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent'
                                                 )

            data = json.loads(response.data.decode())

            intended_order = [video_ids[content] for content in reversed(contents)]
            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert returned_order == intended_order

    def test_get_with_lesser_limit(self):
        with self.client:
            contents = ['a', 'b', 'c', 'd', 'e']
            limit = 3
            auth1, u_id1 = users_api.register_user_quick(self.client)

            video_ids = {}
            for content in contents:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth1
                                                   )
                video_ids[content] = v_id
            
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent',
                                                 limit=limit
                                                 )

            data = json.loads(response.data.decode())

            intended_order = [video_ids[content] for content in reversed(contents)][0:limit]
            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert returned_order == intended_order

    def test_get_with_larger_limit(self):
        with self.client:
            contents = ['a', 'b', 'c', 'd', 'e']
            limit = 7
            auth1, u_id1 = users_api.register_user_quick(self.client)

            video_ids = {}
            for content in contents:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth1
                                                   )
                video_ids[content] = v_id
            
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent',
                                                 limit=limit
                                                 )

            data = json.loads(response.data.decode())

            intended_order = [video_ids[content] for content in reversed(contents)]
            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert returned_order == intended_order

    def test_get_with_offset(self):
        with self.client:
            contents = ['a', 'b', 'c', 'd', 'e']
            limit = 3
            offset = 1
            auth1, u_id1 = users_api.register_user_quick(self.client)

            video_ids = {}
            for content in contents:
                v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth1
                                                   )
                video_ids[content] = v_id
            
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='recent',
                                                 limit=limit,
                                                 offset=offset
                                                 )

            data = json.loads(response.data.decode())

            intended_order = [video_ids[content] for content in reversed(contents)][offset:offset+limit]
            returned_order = [x['video_id'] for x in data['data']['videos']]

            assert response.status_code == http.OK
            assert returned_order == intended_order

    def test_get_all_with_tags(self):
        with self.client:
            contents = ['one', 'day', 'we\'ll', 'old', 'hi']
            tags = [
                ['the'], 
                ['the', 'stories'], 
                ['the', 'stories', 'that', 'we'], 
                ['could', 'have', 'told', 'the'],
                []
                ]
            filter_tags = ['the', 'stories']

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            video_info = {}
            for content, ts in zip(contents, tags):
                response = videos_api.post_video(self.client,
                                                 auth=auth,
                                                 video=StringIO.StringIO(content),
                                                 tags=ts,
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
                
                data = json.loads(response.data.decode())
                video_info[data['data']['video_id']] = ts

            assert len(set(video_info.keys())) == len(contents)
            
            # GET on Videos endpoint with filter_tag
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=filter_tags,
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == len([i for i, ts in video_info.iteritems() if set(filter_tags).issubset(set(ts))])
            assert set(map(lambda x: x['video_id'], data['data']['videos'])) == set([k for k, ts in video_info.iteritems() if set(filter_tags).issubset(set(ts))]) 
            
            for v_info in data['data']['videos']:
                assert set(v_info['tags']) == set(video_info[v_info['video_id']])
                assert v_info['upvotes'] == 0
                assert v_info['downvotes'] == 0
                assert v_info['user_vote'] == 0

    def test_get_all_with_empty_tags(self):
        with self.client:
            contents = ['one', 'day', 'we\'ll', 'old', 'hi']
            tags = [
                ['the'], 
                ['the', 'stories'], 
                ['the', 'stories', 'that', 'we'], 
                ['could', 'have', 'told', 'the'],
                []
                ]
            filter_tags = list()

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            video_info = {}
            for content, ts in zip(contents, tags):
                response = videos_api.post_video(self.client,
                                                 auth=auth,
                                                 video=StringIO.StringIO(content),
                                                 tags=ts,
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
                
                data = json.loads(response.data.decode())
                video_info[data['data']['video_id']] = ts

            assert len(set(video_info.keys())) == len(contents)
            
            # GET on Videos endpoint with filter_tag
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=filter_tags,
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == len([i for i, ts in video_info.iteritems() if set(filter_tags).issubset(set(ts))])
            assert set(map(lambda x: x['video_id'], data['data']['videos'])) == set([k for k, ts in video_info.iteritems() if set(filter_tags).issubset(set(ts))]) 
            
            for v_info in data['data']['videos']:
                assert set(v_info['tags']) == set(video_info[v_info['video_id']])
                assert v_info['upvotes'] == 0
                assert v_info['downvotes'] == 0
                assert v_info['user_vote'] == 0

    def test_get_all_diff_geoloc(self):
        with self.client:
            contents = ['one', 'day', 'we\'ll', 'hi']
            latitudes = [60.0, 9.0, 71.0, 60.01]
            longitudes = [20.0, 4.0, 80.0, 20.01]
            tags = [
                ['think', 'about'], 
                ['the', 'stories'], 
                ['that', 'we'], 
                ['could', 'have', 'told', 'the']
                ]

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            video_info = {}
            for content, ts, lat, lon in zip(contents, tags, latitudes, longitudes):
                response = videos_api.post_video(self.client,
                                                 auth=auth,
                                                 video=StringIO.StringIO(content),
                                                 tags=ts,
                                                 lat=lat,                                                
                                                 lon=lon
                                                 )
               
                data = json.loads(response.data.decode())
                video_info[data['data']['video_id']] = ts

            assert len(set(video_info.keys())) == len(contents)
            
            # GET on Videos endpoint with specific geolocations
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 feedType='main',
                                                 lat=60.0,
                                                 lon=20.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == 2 # I can also reproduce the process of calculating lat_max and lat_min for more rigorous testing
                        
            for v_info in data['data']['videos']:
                assert set(v_info['tags']) == set(video_info[v_info['video_id']])
                assert v_info['upvotes'] == 0
                assert v_info['downvotes'] == 0
                assert v_info['user_vote'] == 0

    def test_get_geoloc_illegal_coordinates(self):
        with self.client:
            contents = ['one']
            latitudes = [60.0]
            longitudes = [20.0]

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            video_infolat = {}
            video_infolon = {}
            for content, lat, lon in zip(contents, latitudes, longitudes):
                response = videos_api.post_video(self.client,
                                                 auth=auth,
                                                 video=StringIO.StringIO(content),
                                                 lat=lat,
                                                 lon=lon
                                                 )
               
                data = json.loads(response.data.decode())
                video_infolat[data['data']['video_id']] = lat
                video_infolon[data['data']['video_id']] = lon

            assert len(set(video_infolat.keys())) == len(contents)
            assert len(set(video_infolon.keys())) == len(contents)
            
            # GET on Videos endpoint with bad latitude
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 feedType='main',
                                                 lat=91.0,
                                                 lon=20.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.BAD_REQ

            # GET on Videos endpoint with bad longitude
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 feedType='main',
                                                 lat=60.0,
                                                 lon=-181.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.BAD_REQ

    def test_get_not_flagged(self):
        with self.client:
            contents = ['one', 'day', 'we\'ll', 'old']
            tags = [
                ['think', 'about'], 
                ['the', 'stories'], 
                ['that', 'we'], 
                ['could', 'have', 'told', 'the']
                ]

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            video_info = {}
            for content, ts in zip(contents, tags):
                response = videos_api.post_video(self.client,
                                                 auth=auth,
                                                 video=StringIO.StringIO(content),
                                                 tags=ts,
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
                
                data = json.loads(response.data.decode())
                video_info[data['data']['video_id']] = ts

            assert len(set(video_info.keys())) == len(contents)

            # post and flag a video
            v_id = videos_api.post_video_quick(self.client,
                                                   auth=auth
                                                   )
            videos_api.flag_video(self.client, v_id, auth)
            
            # GET on Videos endpoint; ensure you return only unflagged videos
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == len(video_info.keys())
            assert set(map(lambda x: x['video_id'], data['data']['videos'])) == set(video_info.keys()) 
            
            for v_info in data['data']['videos']:
                assert set(v_info['tags']) == set(video_info[v_info['video_id']])
                assert v_info['upvotes'] == 0
                assert v_info['downvotes'] == 0
                assert v_info['user_vote'] == 0

    def test_get_flagged_vid_by_other_user(self):
        with self.client:
            contents = ['one', 'day', 'we\'ll', 'old']
            tags = [
                ['think', 'about'], 
                ['the', 'stories'], 
                ['that', 'we'], 
                ['could', 'have', 'told', 'the']
                ]

            # register two users
            auth, u_id = users_api.register_user_quick(self.client)
            auth2, u_id2 = users_api.register_user_quick(self.client,
                                                         email='gim2@gim.com'
                                                         )
            
            # POST to Videos endpoint
            video_info = {}
            for content, ts in zip(contents, tags):
                response = videos_api.post_video(self.client,
                                                 auth=auth,
                                                 video=StringIO.StringIO(content),
                                                 tags=ts,
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
                
                data = json.loads(response.data.decode())
                video_info[data['data']['video_id']] = ts

            assert len(set(video_info.keys())) == len(contents)

            # user 2 flags last video
            v_id = data['data']['video_id']
            videos_api.flag_video(self.client, v_id, auth2)
            
            # user1 GET on Videos endpoint; ensure all videos are properly returned
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
                                                 feedType='main',
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == len(video_info.keys())
            assert set(map(lambda x: x['video_id'], data['data']['videos'])) == set(video_info.keys()) 
            
            for v_info in data['data']['videos']:
                assert set(v_info['tags']) == set(video_info[v_info['video_id']])
                assert v_info['user_vote'] == 0

    