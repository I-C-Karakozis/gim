from flask import request, make_response, jsonify, flash
from flask_restful import Resource

from app import app, db, flask_bcrypt
from app.mod_api import models
from app.mod_api.resources.rest_tools import authentication, email, json_utils 

from jsonschema import validate
import re
import string

def require_auth_token(func):
    def fail_without_auth(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        if auth_token:
            u_id = models.User.decode_auth_token(auth_token)
            if not isinstance(u_id, str):
                return func(*args, **kwargs)
            else:
                response = json_utils.gen_response(success=False, msg=u_id)
                return make_response(jsonify(response), 401)
        else:
            response = json_utils.gen_response(success=False, msg='Provide a valid auth token.')
            return make_response(jsonify(response), 401)
    return fail_without_auth

def get_auth_token(auth_header):
    return auth_header.split(" ")[1] if auth_header else ''

def require_empty_query_string(func):
    def fail_on_query_string(*args, **kwargs):
        if request.query_string:
            response = json_utils.gen_response(success=False, msg='Query string must be empty.')
            return make_response(jsonify(response), 400)
        else:
            return func(*args, **kwargs)
    return fail_on_query_string
    
class Register(Resource):
    """ The Register endpoint is for creating a new user.

    This endpoint supports the following http requests:
    post -- register a new user
    """

    @require_empty_query_string
    def post(self):
        """ Given an email and password, creates a user and returns their authentication credentials.

        Request: POST /Register
        {
            'email': 'host@domain.com',
            'password': 'password'
        }

        Response: HTTP 200 OK
        {
            'status': 'success',
            'auth_token': 'auth_token'
            'data': {
                'user_id': 5
            }
        }
        """
        post_data = request.get_json()
        try:
            validate(post_data, json_utils.auth_schema)
        except:
            response = json_utils.gen_response(success=False, msg='Bad JSON: email and password required.')
            return make_response(jsonify(response), 400)

        password = post_data.get('password')
        if not authentication.meets_password_requirements(password):
            message = 'Password must be at least' + str(app.config.get('MIN_PASS_LEN')) + 'characters long and must contain 1 number, 1 letter, and 1 punctuation mark.'
            response = json_utils.gen_response(success=False, msg=message)
            return make_response(jsonify(response), 400) 
            
        user = models.User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = models.User(
                    email=post_data.get('email'),
                    password=password)
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
                response = json_utils.gen_response(success=False, msg='Some error occured. Please try again.')
                return make_response(jsonify(response), 401)
        else:
            response = json_utils.gen_response(success=False, msg='User already exists. Please log in.')
            return make_response(jsonify(response), 202)

class Confirm(Resource):
    """The Confirm endpoint is for validating a user'email.

    The Confirm endpoint supports the following http requests:
    patch -- obtain the email confirmation token of a user; verify the user account
    """

    @require_empty_query_string
    def patch(self, token):
        """Verifies the email and app acount of the user.

        Request: PATCH /Confirm/<token>

        Response: Web view
            flash('You have confirmed your account. Thanks!', 'success')
        """
        try:
            email = confirm_token(token)
        except:
            flash('The confirmation link is invalid or has expired.', 'danger')
        user = User.query.filter_by(email=email).first_or_404()
        if user.confirmed:
            flash('Account already confirmed. Please login.', 'success')
        else:
            user.confirm()
            flash('You have confirmed your account. Thanks!', 'success')

class Login(Resource):
    """The Login endpoint is for logging in a user.

    This endpoint supports the following requests:
    post -- login an existing user
    """

    @require_empty_query_string
    def post(self):
        """Given an email and a password, verifies the credentials and returns authentication credentials.

        Request: POST /Login
        {
            'email': 'host@domain.com',
            'password': 'password'
        }

        Response: HTTP 200 OK
        {
            'status': 'success',
            'auth_token': 'auth_token',
            'data': {
                'user_id': 5
            }
        }
        """
        post_data = request.get_json()
        try:
            validate(post_data, json_utils.auth_schema)
        except:
            response = json_utils.gen_response(success=False, msg='Bad JSON: email and password required.')
            return make_response(jsonify(response), 400)
        
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
                response = json_utils.gen_response(success=False, msg='User/Password pair is incorrect.')
                return make_response(jsonify(response), 404)
        except Exception as e:
            print(e) # TODO: log this--> what is this for?
            response = json_utils.gen_response(success=False, msg='Try again.')
            return make_response(jsonify(response), 500)

class Status(Resource):
    """The Status endpoint is for obtaining a user's id and validating their authentication token.

    The Status endpoint supports the following http requests:
    get -- obtain the id of a user; authentication token required
    """

    @require_auth_token
    @require_empty_query_string
    def get(self):
        """Returns the id of the user corresponding to the authentication token presented in the Authorizaton header. If the token is invalid, returns an error.

        Request: GET /Status
                 Authorizaton: Bearer auth_token

        Response: HTTP 200 OK
        {
            'status': 'success',
            'data': {
                'user_id': 5
            }
        }
        """
        auth_token = get_auth_token(request.headers.get('Authorization'))

        u_id = models.User.decode_auth_token(auth_token)
        if not isinstance(u_id, str):
            user = models.User.query.filter_by(u_id=u_id).first()
            response = json_utils.gen_response(data={'user_id': user.u_id})
            return make_response(jsonify(response), 200)
        else:
            response = json_utils.gen_response(success=False, msg=u_id)
            return make_response(jsonify(response), 401)

                
class Logout(Resource):
    """The Logout endpoint is for logging a user out.

    This endpoint supports the following http requests:
    get -- log a user out; authentication token required
    """

    @require_auth_token
    @require_empty_query_string
    def get(self):
        """Log out the user who corresponds to the authentication token found in the Authorizaton field. Error if the token is invalid

        Request: GET /Logout
                 Authorization: Bearer auth_token

        Response: HTTP 200 OK
        {
            'status': 'success'
        }
        """
        auth_token = get_auth_token(request.headers.get('Authorization'))

        u_id = models.User.decode_auth_token(auth_token)
        if not isinstance(u_id, str):
            blacklist_token = models.BlacklistToken(token=auth_token)
            try:
                db.session.add(blacklist_token)
                db.session.commit()
                response = json_utils.gen_response(msg='Succesfully logged out.')
                return make_response(jsonify(response), 200)
            except Exception as e:
                response = json_utils.gen_response(success=False, msg=e)
                return make_response(jsonify(response), 200)
        else:
            response = json_utils.gen_response(success=False, msg=u_id)
            return make_response(jsonify(response), 401)
