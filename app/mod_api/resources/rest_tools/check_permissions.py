from flask import request, make_response, jsonify

from app.mod_api import models
from app.mod_api.resources import json_utils

def check_vote_permissions(func):
    def fail_if_not_vote_permission(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        u_id = models.User.decode_auth_token(auth_token)
        user = models.User.get_user_by_id(u_id)
        if not user.check_user_permission('vote'):
            response = json_utils.gen_response(success=False, msg='Voting Restricted.')
            return make_response(jsonify(response), 401)
        else:
            return func(*args, **kwargs)        
    return fail_if_not_vote_permission

def check_post_permissions(func):
    def fail_if_not_post_permission(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        u_id = models.User.decode_auth_token(auth_token)
        user = models.User.get_user_by_id(u_id)
        if not user.check_user_permission('post'):
            response = json_utils.gen_response(success=False, msg='Posting Restricted.')
            return make_response(jsonify(response), 401)
        else:
            return func(*args, **kwargs)        
    return fail_if_not_post_permission
    