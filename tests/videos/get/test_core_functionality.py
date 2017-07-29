from tests import GimTestCase
from tests import user_helpers as users_api
from tests import video_helpers as videos_api
from tests import http_helpers as http

import json
import StringIO
import os

class TestGetVideos(GimTestCase.GimFreshDBTestCase):
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

            # GET on Thumbnails endpoint
            # response = videos_api.get_thumbnail(self.client,
            #                                 v_id,
            #                                 auth=auth
            #                                 )

            # assert response.status_code == http.OK
            # assert response.data == contents --> not sure how to test contents

            response = videos_api.get_video(self.client,
                                            v_id,
                                            auth=auth
                                            )

            data = json.loads(response.data.decode())

            assert response.status_code == http.OK
            assert data['data']['upvotes'] == 0
            assert data['data']['downvotes'] == 0
            assert set(data['data']['tags']) == set(tags)
            assert data['data']['user_vote'] == 0

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

             # GET on VideoFiles endpoint
            response = videos_api.get_video_file(self.client,
                                            v_id=9001,
                                            auth=auth
                                            )

            assert response.status_code == http.NOT_FOUND

            # GET on Thumbnails endpoint
            response = videos_api.get_thumbnail(self.client,
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

    def test_get_invalid_feedType(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # GET on Videos endpoint
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
                                                 feedType='asdf',
                                                 lat=0.0,
                                                 lon=0.0
                                                 )

            assert response.status_code == http.BAD_REQ

    def test_get_missing_required_args(self):
        with self.client:
            # register a user
            auth, u_id = users_api.register_user_quick(self.client)
            
            # GET on Videos endpoint
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
                                                 lat=0.0,
                                                 lon=0.0
                                                 )

            assert response.status_code == http.BAD_REQ

            # GET on Videos endpoint
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
                                                 feedType='asdf',
                                                 lon=0.0
                                                 )

            assert response.status_code == http.BAD_REQ

            # GET on Videos endpoint
            response = videos_api.get_all_videos(self.client,
                                                 auth=auth,
                                                 tags=[],
                                                 feedType='asdf',
                                                 lat=0.0
                                                 )

            assert response.status_code == http.BAD_REQ


    