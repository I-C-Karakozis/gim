from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse
import datetime

from app import app, db, flask_bcrypt
from app.mod_api import models
from app.mod_api.resources import auth

parser = reqparse.RequestParser()

class Users(Resource):
    def post(self):
        response = {
            'status': 'failed',
            'message': 'use the /api/Auth/Register endpoint to create a new user.',
            'next_url': '/api/Auth/Register'
            }
        return make_response(jsonify(response), 301)

class User(Resource):
    """The Users endpoint is for deleting a user and patching and getting the information of a user.

    This endpoint supports the following http requests:
    patch -- updates the password of the user; authentication token required
    get -- returns the user id, user email, the last time they were active, and when they were registered; authentication token required
    delete -- deletes the user; authentication token required

    All requests require the client to pass the user id of the target user.
    """

    @auth.require_auth_token
    def patch(self, user_id): 
        """Given correct current password and a new password, it updates the password of the user with the id corresponding to the authentication token presented in the Authorizaton header to the new password. If the token is invalid, returns an error.

        Request: PATCH /Users/5
                Authorizaton: Bearer auth_token
        {
            'password': 'password'
            'new_password': 'new_password'
        }
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': {
                'user_id': 5
            }
        }
        Returns 404 if no user with the given id was found.
        """
        args = parser.parse_args()
        if request.query_string:
            abort(400)
            
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''

        if auth_token:
            token_u_id = models.User.decode_auth_token(auth_token) 
            if not isinstance(token_u_id, str): 
                if (token_u_id != user_id):
                    response = {
                        'status': 'failed',
                        'message': "Unauthorized access: You are not allowed to patch that user's information."
                        } 
                    return make_response(jsonify(response), 401)

                user = models.User.query.get_or_404(user_id) 
                post_data = request.get_json()           

                if post_data.has_key('password') & post_data.has_key('new_password'):
                    passed_old_password = post_data.get('password')
                    passed_new_password = post_data.get('new_password')

                    if not auth.meets_password_requirements(passed_new_password):
                        response = {
                            'status': 'failed',
                            'message': 'password must be at least 6 chars long, contain 1 number, 1 letter, and 1 punctuation'
                            }
                        return make_response(jsonify(response), 400)

                    if not flask_bcrypt.check_password_hash(user.password_hash, passed_old_password):
                        response = {
                            'status': 'failed',
                            'message': "Unauthorized access: Incorrect password entered."
                            } 
                        return make_response(jsonify(response), 401)

                    user.password_hash = flask_bcrypt.generate_password_hash(passed_new_password, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
                    now = datetime.datetime.now()
                    user.last_active_on = now
                    db.session.commit()

                    response = {
                    'status': 'success',
                    'data': {
                        'user_id': user_id ,
                        }
                    }
                    return make_response(jsonify(response), 200)
                else:
                    response = {
                        'status': 'failed',
                        'message': "Incomplete information passed: Patch request requires 'password'' and 'new_password' attributes"
                        } 
                    return make_response(jsonify(response), 400)                

            else:
                response = {
                    'status': 'failed',
                    'message': user_id
                    }
                return make_response(jsonify(response), 401)
        else:
            response = {
                'status': 'failed',
                'message': 'Provide a valid auth token.'
                }
            return make_response(jsonify(response), 401)

    @auth.require_auth_token
    def get(self, user_id):
        """Returns all information of the user with the id corresponding to the authentication token presented in the Authorizaton header. If the token is invalid, returns an error.
        
        Request: GET /Users
                Authorizaton: Bearer auth_token
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': {
                'user_id': user_id ,
                'email': user.email ,
                'registered_on': user.registered_on
                'last_active_on': user.last_active_on
                }
        }
        Returns 404 if no user with the given id was found.
        """
        args = parser.parse_args()
        if request.query_string:
            abort(400)

        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''

        if auth_token:
            token_u_id = models.User.decode_auth_token(auth_token) 
            if not isinstance(token_u_id, str): 
                if (token_u_id != user_id):
                    response = {
                        'status': 'failed',
                        'message': "Unauthorized access: You are not allowed to patch that user's information."
                        } 
                    return make_response(jsonify(response), 401)

                user = models.User.query.get_or_404(user_id)
                now = datetime.datetime.now()
                user.last_active_on = now
                db.session.commit()

                response = {
                    'status': 'success',
                    'data': {
                        'user_id': user_id ,
                        'email': user.email ,
                        'registered_on': user.registered_on ,
                        'last_active_on': user.last_active_on
                        }
                    }
                return make_response(jsonify(response), 200)
            else:
                response = {
                    'status': 'failed',
                    'message': user_id
                    }
                return make_response(jsonify(response), 401)
        else:
            response = {
                'status': 'failed',
                'message': 'Provide a valid auth token.'
                }
            return make_response(jsonify(response), 401)

    @auth.require_auth_token
    def delete(self, user_id):
        """Deletes user with the id corresponding to the authentication token presented in the Authorizaton header. If the token is invalid, returns an error.
        
        Request: DELETE /Users
                Authorizaton: Bearer auth_token
        {
            'password': 'password'
        }
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': {
                'user_id': user_id ,
                }
        }
        Returns 404 if no user with the given id was found.
        """
        args = parser.parse_args()
        if request.query_string:
            abort(400)

        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''

        if auth_token:
            token_u_id = models.User.decode_auth_token(auth_token) 
            if not isinstance(token_u_id, str): 
                if (token_u_id != user_id):
                    response = {
                        'status': 'failed',
                        'message': "Unauthorized access: You are not allowed to patch that user's information."
                        } 
                    return make_response(jsonify(response), 401)

                user = models.User.query.get_or_404(user_id)
                now = datetime.datetime.now()
                user.last_active_on = now
                post_data = request.get_json()           

                if post_data.has_key('password'):
                    password = post_data.get('password')

                    if not flask_bcrypt.check_password_hash(user.password_hash, password):
                        response = {
                            'status': 'failed',
                            'message': "Unauthorized access: Incorrect password entered."
                            } 
                        return make_response(jsonify(response), 401)

                    db.session.delete(user)
                    db.session.commit()

                    response = {
                        'status': 'success',
                        'data': {
                            'user_id': user_id ,
                            }
                        }
                    return make_response(jsonify(response), 200)
                else:
                    response = {
                        'status': 'failed',
                        'message': "Incomplete information passed: Delete request requires 'password' attribute."
                        } 
                    return make_response(jsonify(response), 400) 
            else:
                response = {
                    'status': 'failed',
                    'message': user_id
                    }
                return make_response(jsonify(response), 401)
        else:
            response = {
                'status': 'failed',
                'message': 'Provide a valid auth token.'
                }
            return make_response(jsonify(response), 401)
