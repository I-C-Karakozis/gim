from flask import request, make_response, abort, jsonify, send_file
from flask_restful import Resource, reqparse

from app.mod_api import models
from app.mod_api.resources import auth

import json

class VideoFiles(Resource):
    """The VideoFiles endpoint is for retrieval of specific video files (see the Videos endpoint for metadata retrieval and manipulation).
    
    This endpoint supports the following http requests:
    get -- returns the file associated with the given video id; authentication token required

    All requests require the client to pass the video id of the target video.
    """

    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, video_id):
        """
        Given a video id, return the file associated with it. The user must provide a valid authentication token.

        Request: GET /VideoFiles/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
                  video file
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        video = models.Video.get_video_by_id(video_id)

        if video:
            vfile = send_file(video.retrieve(), mimetype='text/plain')
            return make_response(vfile, 200)
        else:
            response = {
                'status': 'failed',
                'message': 'Video does not exist',
                }
            return make_response(jsonify(response), 404)

class Video(Resource):
    """The Videos endpoint is for retrieving and manipulating video metadata (see VideoFiles endpoint for retrieving the video file itself). The endpoint is implemented in the Video and Videos classes.

    This endpoint supports the following http requests:
    get -- returns metadata about the video; authentication token required
    patch -- updates the tags of the video; authentication token required
    delete -- delets the video; authentication token required

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
                    'downvotes': 666
                }
        }
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        video = models.Video.get_video_by_id(video_id)

        if video and video.u_id == u_id:
            response = {
                'status': 'success',
                'data': {
                    'video_id': video.v_id,
                    'uploaded_on': video.uploaded_on,
                    'tags': [t.name for t in video.tags],
                    'upvotes': len([vt for vt in video.votes if vt.upvote]),
                    'downvotes': len([vt for vt in video.votes if not vt.upvote]) 
                    }
                } 
            return make_response(jsonify(response), 200)
        else:
            response = {
                'status': 'failed',
                'message': 'Video does not exist',
                }
            return make_response(jsonify(response), 404)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def patch(self, video_id):
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)

        video = models.Video.get_video_by_id(video_id)
        if video and video.u_id == u_id:
            post_data = request.get_json()
            if 'tags' in post_data:
                video.add_tags(post_data['tags'])                
                # TODO: voting
            response = {
                'status': 'success'
                }
            return make_response(jsonify(response), 200)    
        else:
            response = {
                'status': 'failed',
                'message': 'you do not own a video with this id'
                }
            return make_response(jsonify(response), 401)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def delete(self, video_id):
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        
        video = models.Video.get_video_by_id(video_id)
        if video and video.u_id == u_id:
            video.delete()
            response = {
                'status': 'success',
                }
            return make_response(jsonify(response), 200)
        else:
            response = {
                'status': 'failed',
                'message': 'you do not own a video with this id'
                }
            return make_response(jsonify(response), 401)

class Videos(Resource):
    """The Videos endpoint is for retrieving and manipulating video metadata (see VideoFiles endpoint for retrieving the video file itself). The endpoint is implemented in the Video and Videos classes.

    This endpoint supports the following http requests:
    get -- returns metadata for some number of videos; authentication token required
    post -- uploads a video and returns its video id; authentication token required
    """

    @auth.require_auth_token
    def get(self):
        """
        Uploads a video to the database and returns a new video id. If the auth token is invalid, returns an error.

        Request: GET /Videos?lat=22.0&lon=67.8&tag=t1&tag=t2
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
        parser = reqparse.RequestParser()
        parser.add_argument('lat', type=float, required=True,
                            help='Latitude required')
        parser.add_argument('lon', type=float, required=True,
                            help='Longitude required')
        parser.add_argument('tag', action='append')
        parser.add_argument('limit', type=int)
        parser.add_argument('offset', type=int)
        args = parser.parse_args()
        
        lat = args['lat']
        lon = args['lon']
        tags = args.get('tag', [])
        limit = args.get('limit', 5)
        offset = args.get('offset', 0)

        videos = models.Video.search(lat, lon, tags, limit, offset)
        response = {
            'status': 'success',
            'data': {
                'videos': [
                    {
                        'video_id': v.v_id,
                        'uploaded_on': v.uploaded_on,
                        'tags': [t.name for t in v.tags],
                        'upvotes': len([vt for vt in v.votes if vt.upvote]),
                        'downvotes': len([vt for vt in v.votes if not vt.upvote])
                        } 
                    for v in videos]
                }
            }
        return make_response(jsonify(response), 200)

    @auth.require_auth_token
    @auth.require_empty_query_string
    def post(self):
        """
        Uploads a video to the database and returns a new video id. If the auth token is invalid, returns an error.

        Request: POST /Videos
                 Authorization: Bearer auth_token
                 Content-type: multipart/form-data
        {
            'file': video_file,
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
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)
        
        if 'file' in request.files:
            # TODO: some validation that this file is just a video file...
            vfile = request.files.get('file')
            post_data = request.form
            if 'lat' in post_data and 'lon' in post_data:
                tags = post_data.getlist('tags')
                video = models.Video(vfile, u_id, post_data['lat'], post_data['lon'], tags)
                video.commit(insert=True)
                video.add_tags(tags)
                response = {
                    'status': 'success',
                    'data': {
                        'video_id': video.v_id
                        }
                    }
                return make_response(jsonify(response), 200)
            else:
                response = {
                    'status': 'failed',
                    'message': 'lat and lon data missing'
                    }
                return make_response(jsonify(response), 400)
        else:
            response = {
                'status': 'failed',
                'message': 'no video file included, please attach video'
                }
            return make_response(jsonify(response), 400)

