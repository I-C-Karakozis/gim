from flask import request, abort
from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()

class Video(Resource):
    def get(self, video_id):
        return video_id

    def patch(self, video_id):
        args = parser.parse_args()
        if request.query_string:
            abort(400)
        output = 'patch successful ' + video_id
        return output

    def delete(self, video_id):
        return video_id

class Videos(Resource):
    def get(self):
        if '/' in request.query_string:
            abort(400)
        return request.query_string

    def post(self):
        args = parser.parse_args()
        if request.query_string:
            abort(400)
        return 'post successful'

