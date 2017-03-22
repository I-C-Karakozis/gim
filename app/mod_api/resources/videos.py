from flask import request, abort
from flask_restful import Resource, reqparse

from app.mod_api.resources import auth

parser = reqparse.RequestParser()

class Video(Resource):
    @auth.require_auth_token
    def get(self, video_id):
        return video_id

    @auth.require_auth_token
    def patch(self, video_id):
        args = parser.parse_args()
        if request.query_string:
            abort(400)
        output = 'patch successful ' + video_id
        return output

    @auth.require_auth_token
    def delete(self, video_id):
        return video_id

class Videos(Resource):
    @auth.require_auth_token
    def get(self):
        if '/' in request.query_string:
            abort(400)
        return request.query_string

    @auth.require_auth_token
    def post(self):
        args = parser.parse_args()
        if request.query_string:
            abort(400)
        return 'post successful'

