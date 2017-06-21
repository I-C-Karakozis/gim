from flask import request, make_response, jsonify, send_file
from flask_restful import Resource, reqparse

from app.mod_api import models
from app.mod_api.resources import auth
from app.mod_api.resources.rest_tools import json_utils, validators

from werkzeug.datastructures import CombinedMultiDict
from jsonschema import validate

import StringIO

class VideoFiles(Resource):
    """The VideoFiles endpoint is for retrieval of specific video files (see the Videos endpoint for metadata retrieval and manipulation).
    
    This endpoint supports the following http requests:
    get -- returns the file associated with the given video id; authentication token required

    All requests require the client to pass the video id of the target video.
    """

    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, video_id):
        """Given a video id, return the file associated with it. The user must provide a valid authentication token.

        Request: GET /VideoFiles/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
                  video file
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        video = models.Video.get_video_by_id(video_id)

        if video:
            vfile = send_file(video.retrieve(), mimetype='text/plain')
            return make_response(vfile, 200)
        else:
            response = json_utils.gen_response(success=False, msg='Video does not exist.')
            return make_response(jsonify(response), 404)

class Thumbnails(Resource):
    """The Thumbnails endpoint is for retrieval of thumbnails of specific video files.
    
    This endpoint supports the following http requests:
    get -- returns the thumbnail associated with the given video id; authentication token required

    All requests require the client to pass the video id of the target video.
    """

    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, video_id):
        """Given a video id, return the thumbnail associated with it. The user must provide a valid authentication token.

        Request: GET /Thumbnails/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
                  thumbnail file
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        video = models.Video.get_video_by_id(video_id)

        if video:
            exists, thumbnail = video.retrieve_thumbnail()
            vfile = send_file(thumbnail, mimetype='text/plain')
            if exists:
                return make_response(vfile, 200)
            else:
                return make_response(jsonify({}), 204)
        else:
            response = json_utils.gen_response(success=False, msg='Video does not exist.')
            return make_response(jsonify(response), 404)

class Video(Resource):
    """The Videos endpoint is for retrieving and manipulating video metadata (see VideoFiles endpoint for retrieving the video file itself). The endpoint is implemented in the Video and Videos classes.

    This endpoint supports the following http requests:
    get -- returns metadata about the video; authentication token required
    patch -- updates the tags of the video; authentication token required
    delete -- deletes the video; authentication token required

    All requests require the client to pass the video of the target video.
    """

    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, video_id):
        """Returns metadata for the video corresponding to the given video id. If the token is invalid, returns an error.

        Request: GET /Videos/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': 
                {
                    'video_id': 5,
                    'uploaded_on': 'Wed, 12 Apr 2017 21:14:57 GMT',
                    'tags': ['some', 'tags'],
                    'upvotes': 9001,
                    'downvotes': 666,
                    'user_vote': -1
                }
        }
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        video = models.Video.get_video_by_id(video_id)

        if video:
            response = json_utils.gen_response(data=json_utils.video_info(video, u_id))
            return make_response(jsonify(response), 200)
        else:
            response = json_utils.gen_response(success=False, msg='Video does not exist.')
            return make_response(jsonify(response), 404)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def patch(self, video_id):
        """Updates the votes of the video.

        Request: PATCH /Videos/5
                 Authorization: Bearer auth_token
        {
            'upvote': True 
        }
        }
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': 
                {
                    'video_id': 5,
                    'upvotes': 9001,
                    'downvotes': 666
                }
        }
        """
        schema = {
            "type": "object",
            "properties": {
                "upvote": {"type": "boolean"}
                },
            "required": ["upvote"],
            }
        post_data = request.get_json()
        try:
            validate(post_data, schema)
        except:
            response = json_utils.gen_response(success=False, msg='Bad JSON: upvote required.')
            return make_response(jsonify(response), 401)

        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)

        video = models.Video.get_video_by_id(video_id)
        if video:
            old_vote = models.Vote.query.filter_by(u_id = u_id, vid_id = video_id).first()
            
            # repeat of existing vote
            if old_vote:
                # remove vote
                if old_vote.upvote == post_data['upvote']:
                    old_vote.delete()
                else:
                    old_vote.upvote = post_data['upvote']
                    old_vote.commit()
            else:   
                new_vote = models.Vote(u_id, video_id, post_data['upvote'])       
                new_vote.commit(insert = True)

            data = {
                'video_id': video.v_id,
                'upvotes': len([vt for vt in video.votes if vt.upvote]),
                'downvotes': len([vt for vt in video.votes if not vt.upvote])
                }
            response = json_utils.gen_response(success=True, data = data)
            return make_response(jsonify(response), 200)    
        else:
            response = json_utils.gen_response(success=False, msg='You do not own a video with this id.')
            return make_response(jsonify(response), 401)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def delete(self, video_id):
        """Deletes a video. Requesting user must own the video in order to delete it. If the auth token is invalid, returns an error.

        Request: DELETE /Videos/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        
        video = models.Video.get_video_by_id(video_id)
        if video and video.u_id == u_id:
            video.delete()
            response = json_utils.gen_response(success=True)
            return make_response(jsonify(response), 200)
        else:
            response = json_utils.gen_response(success=False, msg='You do not own a video with this id.')
            return make_response(jsonify(response), 401)

class Videos(Resource):
    """The Videos endpoint is for retrieving and manipulating video metadata (see VideoFiles endpoint for retrieving the video file itself). The endpoint is implemented in the Video and Videos classes.

    This endpoint supports the following http requests:
    get -- returns metadata for some number of videos; authentication token required
    post -- uploads a video and returns its video id; authentication token required
    """

    LIMIT = 20

    @auth.require_auth_token
    def get(self):
        """Uploads a video to the database and returns a new video id. If the auth token is invalid, returns an error.

        Request: GET /Videos?lat=22.0&lon=67.8&tag=t1&tag=t2&sortBy=popular
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': 
                {
                    'videos': 
                        [
                            {
                                'video_id': 5,
                                'uploaded_on': ,
                                'tags': ['tiger', ...],
                                'upvotes': 46,
                                'downvotes': 0
                            }, 
                            ...
                        ]
                }
        }
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)

        parser = reqparse.RequestParser()
        parser.add_argument('lat', type=float, required=True,
                            help='Latitude required')
        parser.add_argument('lon', type=float, required=True,
                            help='Longitude required')
        parser.add_argument('tag', action='append')
        parser.add_argument('limit', type=int)
        parser.add_argument('offset', type=int)
        parser.add_argument('sortBy', type=str)
        args = parser.parse_args()
        
        lat = args['lat']
        lon = args['lon']
        tags = args.get('tag', [])
        limit = args.get('limit') if args.get('limit') else Videos.LIMIT 
        offset = args.get('offset') if args.get('offset') else 0
        sort_by = args.get('sortBy') if args.get('sortBy') else 'popular'
        
        # check for illegal query coordinates
        if lat > 90 or lat < -90 or lon > 180 or lon < -180:
            response = json_utils.gen_response(success=False, msg='Illegal coordinates entered.')
            return make_response(jsonify(response), 400)

        videos = models.Video.search(lat, lon, tags, min(limit, Videos.LIMIT), offset, sort_by)
        video_infos = [json_utils.video_info(v, u_id) for v in videos]
        response = json_utils.gen_response(data={'videos': video_infos})
        return make_response(jsonify(response), 200)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def post(self):
        """Uploads a video to the database and returns a new video id. If the auth token is invalid, returns an error.

        Request: POST /Videos
                 Authorization: Bearer auth_token
                 Content-type: multipart/form-data
        {
            'file': <video_file, filename.mov>,
            'lat': 57.2,
            'lon': 39.4,
            'tags': ['soulja', 'boy', 'tell', 'em']
        }
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': 
                {
                    'video_id': 7
                }
        }
        """
        form = validators.VideoUploadForm(CombinedMultiDict((request.files, request.form)))
        if not form.validate():
            response = json_utils.gen_response(success=False, msg=form.errors)
            return make_response(jsonify(response), 400)

        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        
        # collect video file and metadata
        vfile = request.files.get('file')
        post_data = request.form
        lat = post_data.get('lat')
        lon = post_data.get('lon')
        tags = post_data.getlist('tags')       

        video = models.Video(vfile, u_id, lat, lon)
        video.commit(insert=True)
        video.add_tags(tags) 

        response = json_utils.gen_response(data={'video_id': video.v_id})
        return make_response(jsonify(response), 200)
