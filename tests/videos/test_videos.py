from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO

class TestVideos(GimTestCase.GimFreshDBTestCase):
    def test_post(self):
        with self.client:
            contents = "akfdhlkjghkjghdsglj"
            tags = ['this', 'is', 'testing']

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
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

            assert v_id > 0

    def test_get(self):
        with self.client:
            contents = "akfdhlkjghkjghdsglj"
            tags = ['this', 'is', 'testing']

            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # POST to Videos endpoint
            response = videos_api.post_video(self.client,
                                             auth=auth,
                                             video=StringIO.StringIO(contents),
                                             tags=tags,
                                             lat=0.0,
                                             lon=0.0,
                                             )

            data = json.loads(response.data.decode())
            v_id = data['data']['video_id']

            # GET on VideoFiles endpoint
            response = videos_api.get_video_file(self.client,
                                            v_id,
                                            auth=auth
                                            )

            assert response.status_code == http.OK
            assert response.data == contents

            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 0
            assert set(data['data']['tags']) == set(tags)

    def test_get_nonexistent(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # GET on Videos (non-existent id)
            response = videos_api.get_video(self.client,
                                            v_id=9001,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

    def test_get_all(self):
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
            
            # GET on Videos endpoint
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
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

    def test_get_all_by_popularity(self):
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
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth1,
                                                 tags=[],
                                                 lat=0.0,
                                                 lon=0.0,
                                                 sortBy='popular'
                                                 )
            data = json.loads(response.data.decode())
            
            intended_order = map(lambda x: x[1], 
                                 sorted(zip(net_votes, video_ids),
                                        cmp=lambda x, y: x[0] - y[0],
                                        reverse=True
                                        )
                                 ) 
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
            contents = ['one', 'day', 'we\'ll', 'old']
            tags = [
                ['think', 'about'], 
                ['the', 'stories'], 
                ['that', 'we'], 
                ['could', 'have', 'told', 'the']
                ]
            filter_tag = 'the'

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
                                                 tags=[filter_tag],
                                                 lat=0.0,
                                                 lon=0.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert len(data['data']['videos']) == len([ts for ts in video_info.values() if filter_tag in ts])
            assert set(map(lambda x: x['video_id'], data['data']['videos'])) == set([k for k, ts in video_info.iteritems() if filter_tag in ts]) 
            
            for v_info in data['data']['videos']:
                assert set(v_info['tags']) == set(video_info[v_info['video_id']])
                assert v_info['upvotes'] == 0
                assert v_info['downvotes'] == 0

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
                                                 lat=91.0,
                                                 lon=20.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.BAD_REQ

            # GET on Videos endpoint with bad longitude
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 lat=60.0,
                                                 lon=-181.0
                                                 )
            data = json.loads(response.data.decode())

            assert response.status_code == http.BAD_REQ


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
                                               upvote=True
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
            assert data['data']['upvotes'] == 1
            assert data['data']['downvotes'] == 0

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
                                               upvote=False
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
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1


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
                                       upvote=False
                                       )

            assert response.status_code == http.OK
            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1

    def test_patch_vote_non_existent_video(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)

            response = videos_api.patch_video(self.client,
                                       5,
                                       auth=auth,
                                       upvote=False
                                       )

            assert response.status_code == http.UNAUTH


    def test_patch_no_data(self):
        with self.client:
            # Register a user
            auth, u_id = users_api.register_user_quick(self.client)

            # POST a video with user 1
            v_id = videos_api.post_video_quick(self.client,
                                               auth=auth
                                               )

            response = videos_api.patch_video(self.client,
                                       v_id,
                                       auth=auth
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
                                               upvote=True
                                               )
            assert response.status_code == http.OK

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=True
                                               )
            assert response.status_code == http.NOT_MOD

            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )
            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 1
            assert data['data']['downvotes'] == 0

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
                                               upvote=False
                                               )
            assert response.status_code == http.OK

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=False
                                               )
            assert response.status_code == http.NOT_MOD

            response = videos_api.get_video(self.client,
                                                v_id,
                                                auth=auth
                                                )
            assert response.status_code == http.OK
                           
            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1
           

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
                                               upvote=True
                                               )
            assert response.status_code == http.OK

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=False
                                               )
            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 1

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
                                               upvote=False
                                               )
            assert response.status_code == http.OK

            response = videos_api.patch_video(self.client,
                                               v_id,
                                               auth=auth,
                                               upvote=True
                                               )
            assert response.status_code == http.OK

            data = json.loads(response.data.decode())
            assert data['data']['upvotes'] == 1
            assert data['data']['downvotes'] == 0
