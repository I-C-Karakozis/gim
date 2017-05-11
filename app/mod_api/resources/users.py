from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from app import app, db, flask_bcrypt
from app.mod_api import models
from app.mod_api.resources import auth
from app.mod_api.resources import json_utils

from jsonschema import validate

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
    @auth.require_empty_query_string
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
        schema = {
            "type": "object",
            "properties": {
                "password": {"type": "string"},
                "new_password": {"type": "string"}
                },
            "required": ["password", "new_password"],
            }
        post_data = request.get_json()
        try:
            validate(post_data, schema)
        except:
            response = json_utils.gen_response(success=False, msg='Bad JSON: password and new_password required.')
            return make_response(jsonify(response), 400)

        auth_token = auth.get_auth_token(request.headers.get('Authorization'))        
        token_u_id = models.User.decode_auth_token(auth_token) 

        if not isinstance(token_u_id, str): 
            if (token_u_id != user_id):
                response = json_utils.gen_response(success=False, msg="Unauthorized access: You are not allowed to patch that user's information.") 
                return make_response(jsonify(response), 401)

            user = models.User.query.get_or_404(user_id) 
         
            passed_old_password = post_data.get('password')
            passed_new_password = post_data.get('new_password')

            if not auth.meets_password_requirements(passed_new_password):
                response = json_utils.gen_response(success=False, msg="Password must be at least 6 chars long, contain 1 number, 1 letter, and 1 punctuation.")
                return make_response(jsonify(response), 400)

            if not flask_bcrypt.check_password_hash(user.password_hash, passed_old_password):
                response = json_utils.gen_response(success=False, msg="Unauthorized access: Incorrect password entered.")
                return make_response(jsonify(response), 401)

            user.password_hash = flask_bcrypt.generate_password_hash(passed_new_password, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
            user.commit()

            response = {
            'status': 'success',
            'data': {
                'user_id': user_id ,
                }
            }
            return make_response(jsonify(response), 200)            
        else:
            response = json_utils.gen_response(success=False, msg=str(user_id))
            return make_response(jsonify(response), 401)


    @auth.require_auth_token
    @auth.require_empty_query_string
    def get(self, user_id):
        """Returns all information of the user with the id corresponding to the authentication token presented in the Authorizaton header. If the token is invalid, returns an error.
        
        Request: GET /Users/5
                Authorizaton: Bearer auth_token
        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': {
                'user_id': user_id ,
                'email': user.email ,
                'registered_on': user.registered_on ,
                'last_active_on': user.last_active_on ,
                'score': 22,
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
        Returns 404 if no user with the given id was found.
        """
        auth_token = auth.get_auth_token(request.headers.get('Authorization')) 
        token_u_id = models.User.decode_auth_token(auth_token) 

        if not isinstance(token_u_id, str): 
            if (token_u_id != user_id):
                response = json_utils.gen_response(success=False, msg="Unauthorized access: You are not allowed to patch that user's information.")
                return make_response(jsonify(response), 401)

            # users meta data
            user = models.User.query.get_or_404(user_id)
            user.commit()

            # users video
            videos = models.Video.get_videos_by_user_id(user_id)
            video_infos = [json_utils.video_info(v, user_id) for v in videos]
            
            data = {
                    'user_id': user_id ,
                    'email': user.email ,
                    'registered_on': user.registered_on ,
                    'last_active_on': user.last_active_on ,
                    'score': user.get_score(),
                    'videos': video_infos
                    }
            response = json_utils.gen_response(data=data)
            return make_response(jsonify(response), 200)
        else:
            response = json_utils.gen_response(success=False, msg=str(user_id))
            return make_response(jsonify(response), 401)


    @auth.require_auth_token
    @auth.require_empty_query_string
    def delete(self, user_id):
        """Deletes user with the id corresponding to the authentication token presented in the Authorizaton header. If the token is invalid, returns an error.
        
        Request: DELETE /Users/5
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
        schema = {
            "type": "object",
            "properties": {
                "password": {"type": "string"}
                },
            "required": ["password"],
            }
        post_data = request.get_json()
        try:
            validate(post_data, schema)
        except:
            response = json_utils.gen_response(success=False, msg='Bad JSON: password required.')
            return make_response(jsonify(response), 400)

        auth_token = auth.get_auth_token(request.headers.get('Authorization')) 
        token_u_id = models.User.decode_auth_token(auth_token) 

        if not isinstance(token_u_id, str): 
            if (token_u_id != user_id):
                response = json_utils.gen_response(success=False, msg="Unauthorized access: You are not allowed to patch that user's information.")
                return make_response(jsonify(response), 401)

            user = models.User.query.get_or_404(user_id)
            user.commit()
          
            password = post_data.get('password')

            if not flask_bcrypt.check_password_hash(user.password_hash, password):
                response = json_utils.gen_response(success=False, msg="Unauthorized access: Incorrect password entered.")
                return make_response(jsonify(response), 401)

            user.delete()
            response = {
                'status': 'success',
                'data': {
                    'user_id': user_id ,
                    }
                }
            return make_response(jsonify(response), 200)       
        else:
            response = json_utils.gen_response(success=False, msg=str(user_id))
            return make_response(jsonify(response), 401)