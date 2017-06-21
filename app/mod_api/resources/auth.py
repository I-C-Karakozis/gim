from flask import request, make_response, jsonify, render_template, url_for
from flask_restful import Resource

from app import app, db, flask_bcrypt
from app.mod_api import models
from app.mod_api.resources.rest_tools import json_utils, validators, email
from app.mod_api.resources.rest_tools.authentication import *
 
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
        password = post_data.get('password')

        if not meets_password_requirements(password):
            response = json_utils.gen_response(success=False, msg='Password must be at least 6 characters long and must contain 1 number, 1 letter, and 1 punctuation mark.')
            return make_response(jsonify(response), 400) 
            
        user = models.User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                # initial registration
                user = models.User(
                    email=post_data.get('email'),
                    password=post_data.get('password')
                    )

                db.session.add(user)
                db.session.commit()

                # generate token, confirmation url and send email
                token = email.generate_confirmation_token(user.email)
                confirm_url = url_for('user.confirm_email', token=token, _external=True)
                html = render_template('user/activate.html', confirm_url=confirm_url)
                subject = "Confirm your email for your Purview Account!"
                email.send_email(user.email, subject, html)

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
