from flask import request, make_response, jsonify
from flask_restful import Resource

from app import app, db, flask_bcrypt
from app.mod_api import models
from app.mod_api.resources.rest_tools import json_utils

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

def meets_password_requirements(password):
    len_req = len(password) >= app.config.get('MIN_PASS_LEN')
    letter_req = re.search('[A-Za-z]', password)
    number_req = re.search('\\d', password)
    punctuation_req = re.search('[^A-Za-z0-9]', password)
    return len_req and letter_req and number_req and punctuation_req