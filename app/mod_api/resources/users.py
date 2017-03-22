from flask import request, abort, make_response, jsonify
from flask_restful import Resource, reqparse

from app.mod_api.resources import auth

parser = reqparse.RequestParser()

class User(Resource):
    @auth.require_auth_token
    def get(self, user_id):
        return user_id

    @auth.require_auth_token
    def patch(self, user_id):
        args = parser.parse_args()
        if request.query_string:
            abort(400)
        output = 'patch successful ' + str(user_id)
        return output

    @auth.require_auth_token
    def delete(self, user_id):
        return user_id

class Users(Resource):
    def post(self):
        response = {
            'status': 'failed',
            'message': 'use the /api/Auth/Register endpoint to create a new user.',
            'next_url': '/api/Auth/Register'
            }
        return make_response(jsonify(response), 301)
