# Import flask dependencies
from flask import Blueprint, request, abort
from flask_restful import Resource, Api, reqparse

from app import db

mod_api = Blueprint('api', __name__, url_prefix='/api')
api_v1 = Api(mod_api)

parser = reqparse.RequestParser()

class Video(Resource):
    def get(self, video_id):
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

api_v1.add_resource(Videos, '/Videos')
api_v1.add_resource(Video, '/Videos/<int:video_id>')
