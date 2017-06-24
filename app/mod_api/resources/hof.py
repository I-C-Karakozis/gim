from flask import request, make_response, jsonify, send_file
from flask_restful import Resource, reqparse

from app.mod_api import models
from app.mod_api.resources import auth
from app.mod_api.resources.rest_tools import json_utils, validators

from werkzeug.datastructures import CombinedMultiDict
from jsonschema import validate

def hof_video_info(video):
    return {
        'video_id': video.hof_id,
        'uploaded_on': video.uploaded_on,
        'score': video.score
        }

class HallOfFameFiles(Resource):
    """The HallOfFameFiles endpoint is for retrieval of specific video files (see the HallOfFame endpoint for metadata retrieval and manipulation).
    
    This endpoint supports the following http requests:
    get -- returns the file associated with the given video id; authentication token required

    All requests require the client to pass the video id of the target video in the Hall of Fame.
    """

    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, video_id):
        """Given a video id, return the file associated with it. The user must provide a valid authentication token.

        Request: GET /HallOfFameFiles/5
                 Authorization: Bearer auth_token
        Response: HTTP 200 OK
                  hof video file
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        video = models.HallOfFame.get_video_by_id(video_id)

        if video:
            vfile = send_file(video.retrieve(), mimetype='text/plain')
            return make_response(vfile, 200)
        else:
            response = json_utils.gen_response(success=False, msg='Video does not exist in the Hall Of Fame.')
            return make_response(jsonify(response), 404)

class HallOfFameThumbnails(Resource):
    """The HallOfFameThumbnails endpoint is for retrieval of thumbnails of specific hof video files.
    
    This endpoint supports the following http requests:
    get -- returns the thumbnail associated with the given hof video id; authentication token required

    All requests require the client to pass the hof video id of the target video.
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
        video = models.HallOfFame.get_video_by_id(video_id)

        if video:
            # vfile = send_file(video.retrieve_thumbnail(), mimetype='text/plain')
            return make_response(jsonify({}),200)
        else:
            response = json_utils.gen_response(success=False, msg='Video does not exist in the Hall Of Fame.')
            return make_response(jsonify(response), 404)

class HallOfFame(Resource):
    """The HallOfFame endpoint is for retrieving hall of fame video metadata (see HallOfFameFiles endpoint for retrieving the video file itself). 

    This endpoint supports the following http requests:
    get -- returns metadata about all videos in the Hall Of Fame; authentication token required

    All requests require the client to pass the video of the target video.
    """

    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self):
        """Returns metadata for all 10 videos in the Hall Of Fame in descending order w.r.t the video score. If the token is invalid, returns an error.

        Request: GET /HallOfFame
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
                                'score': 46
                            }, 
                            ...
                        ]
                }
        }
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization'))
        u_id = models.User.decode_auth_token(auth_token)

        videos = models.HallOfFame.sort_desc_and_retrieve_all()
        video_infos = [hof_video_info(v) for v in videos]
        response = json_utils.gen_response(data={'videos': video_infos})
        return make_response(jsonify(response), 200)

