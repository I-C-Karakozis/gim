from flask import request, make_response, jsonify
from flask_restful import Resource

from app import app, db, flask_bcrypt
from app.mod_api import models

def require_auth_token(func):
    def fail_without_auth(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        if auth_token:
            u_id = models.User.decode_auth_token(auth_token)
            if not isinstance(u_id, str):
                return func(*args, **kwargs)
            else:
                response = {
                    'status': 'failed',
                    'message': u_id
                    }
                return make_response(jsonify(response), 401)
        else:
            response = {
                'status': 'failed',
                'message': 'Provide a valid auth token.'
                }
            return make_response(jsonify(response), 401)
    return fail_without_auth

class Register(Resource):
    def post(self):
        post_data = request.get_json()
        user = models.User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = models.User(
                    email=post_data.get('email'),
                    password=post_data.get('password')
                    )

                db.session.add(user)
                db.session.commit()

                auth_token = user.encode_auth_token()
                response = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode(),
                    'data': {
                        'user_id': user.u_id
                        }
                    }

                return make_response(jsonify(response), 201)
            except Exception as e:
                response = {
                    'status': 'fail',
                    'message': 'Some error occured. Please try again'
                    }
                return make_response(jsonify(response), 401)
        else:
            response = {
                'status': 'fail',
                'message': 'User already exists. Please log in.'
                }
            return make_response(jsonify(response), 202)

class Login(Resource):
    def post(self):
        post_data = request.get_json()
        try:
            user = models.User.query.filter_by(email=post_data.get('email')).first()
            if user and flask_bcrypt.check_password_hash(user.password_hash, post_data.get('password')):
                auth_token = user.encode_auth_token()
                if auth_token:
                    response = {
                        'status': 'success',
                        'message': 'Succesfully logged in.',
                        'auth_token': auth_token.decode(),
                        'data': {
                            'user_id': user.u_id
                            }
                        }
                    return make_response(jsonify(response), 200)
            else:
                response = {
                    'status': 'failed',
                    'message': 'User/Password pair is incorrect.'
                    }
                return make_response(jsonify(response), 404)
        except Exception as e:
            print(e) # TODO: log this
            response = {
                'status': 'failed',
                'message': 'Try again.'
                }
            return make_response(jsonify(response), 500)

class Status(Resource):
    def get(self):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        if auth_token:
            u_id = models.User.decode_auth_token(auth_token)
            if not isinstance(u_id, str):
                user = models.User.query.filter_by(u_id=u_id).first()
                response = {
                    'status': 'success',
                    'data': {
                        'user_id': user.u_id
                        }
                    }
                return make_response(jsonify(response), 200)
            else:
                response = {
                    'status': 'failed',
                    'message': u_id
                    }
                return make_response(jsonify(response), 401)
        else:
            response = {
                'status': 'failed',
                'message': 'Provide a valid auth token.'
                }
            return make_response(jsonify(response), 401)
                
class Logout(Resource):
    def get(self):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        if auth_token:
            u_id = models.User.decode_auth_token(auth_token)
            if not isinstance(u_id, str):
                blacklist_token = models.BlacklistToken(token=auth_token)
                try:
                    db.session.add(blacklist_token)
                    db.session.commit()
                    response = {
                        'status': 'success',
                        'message': 'Succesfully logged out'
                        }
                    return make_response(jsonify(response), 200)
                except Exception as e:
                    response = {
                        'status': 'failed',
                        'message': e
                        }
                    return make_response(jsonify(response), 200)
            else:
                response = {
                    'status': 'failed',
                    'message': u_id
                    }
                return make_response(jsonify(response), 401)
        else:
            response = {
                'status': 'failed',
                'message': 'Provide a valid auth token.'
                }
            return make_response(jsonify(response), 403)
