from flask import request, make_response, jsonify, send_file
from flask_restful import Resource, reqparse

from app.mod_api import models
from app.mod_api.resources import auth
from app.mod_api.resources import json_utils
from app.mod_api.resources import validators

from werkzeug.datastructures import CombinedMultiDict
from jsonschema import validate

import StringIO

class BannedVideoFiles(Resource):
    """The BannedVideoFiles endpoint is for retrieval of specific banned video files 

    This endpoint supports the following http requests:
    get -- returns the file associated with the given video id; authentication token required

    All requests require the client to pass the video id of the target video.
    """
    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, video_id):
        """Given a video id, return the file associated with it. The user must provide a valid authentication token.

        Request: GET /BannedVideoFiles/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
                  banned video file
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        banned_video = models.Banned_Video.get_banned_video_by_id(video_id)

        if banned_video:
            bvfile = send_file(banned_video.retrieve(), mimetype='text/plain')
            return make_response(bvfile, 200)
        else:
            response = json_utils.gen_response(success=False, msg='Banned Video does not exist.')
            return make_response(jsonify(response), 404)

class BannedVideo(Resource):
    """The Banned Videos endpoint is for retrieving and manipulating banned video metadata 

    This endpoint supports the following http requests:
    get -- returns metadata about the banned video; authentication token required

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
                    'user_id': 5,
                    'uploaded_on': 'Wed, 12 Apr 2017 21:14:57 GMT',
                    'tags': ['some', 'tags'],
                    'lat': 60.30,
                    'lon': 30.60,
                    'user_warned': False
                }
        }
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        banned_video = models.Banned_Video.get_banned_video_by_id(video_id)

        if banned_video:
            response = json_utils.gen_response(data=json_utils.banned_video_info(banned_video))
            return make_response(jsonify(response), 200)
        else:
            response = json_utils.gen_response(success=False, msg='Banned video does not exist.')
            return make_response(jsonify(response), 404)

