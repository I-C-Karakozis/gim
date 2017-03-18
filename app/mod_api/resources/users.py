from flask import request, abort
from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()

class User(Resource):
    def get(self, user_id):
        return user_id

    def post(self, user_id):
        args = parser.parse_args()
        if request.query_string:
            abort(400)
        return 'post successful'

    def patch(self, user_id):
        args = parser.parse_args()
        if request.query_string:
            abort(400)
        output = 'patch successful ' + user_id
        return output

    def delete(self, user_id):
        return user_id

class Users(Resource):
    def get(self):
        if '/' in request.query_string:
            abort(400)
        return request.query_string

    