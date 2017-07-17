from flask import request, make_response, jsonify

from app.mod_api import models
from app.mod_api.resources import json_utils

def check_vote_restrictions(func):
    def fail_if_vote_restriction(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        u_id = models.User.decode_auth_token(auth_token)
        restriction = models.Restriction.get_restriction_on_user('vote', u_id)
        if restriction:
            response = json_utils.gen_response(success=False, msg='Voting Restricted.')
            return make_response(jsonify(response), 401)
        else:
            return func(*args, **kwargs)        
    return fail_if_vote_restriction

def check_post_restrictions(func):
    def fail_if_post_restriction(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        u_id = models.User.decode_auth_token(auth_token)
        restriction = models.Restriction.get_restriction_on_user('post', u_id)
        if restriction:
            response = json_utils.gen_response(success=False, msg='Posting Restricted.')
            return make_response(jsonify(response), 401)
        else:
            return func(*args, **kwargs)        
    return fail_if_post_restriction
    