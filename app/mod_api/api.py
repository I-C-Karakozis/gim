# Import flask dependencies
from flask import Blueprint
from flask_restful import Api

from resources import videos, users
from app import db

mod_api = Blueprint('api', __name__, url_prefix='/api')
api_v1 = Api(mod_api)

api_v1.add_resource(videos.Videos, '/Videos')
api_v1.add_resource(videos.Video, '/Videos/<int:video_id>')

api_v1.add_resource(users.Users, '/Users')
api_v1.add_resource(users.User, '/Users/<int:user_id>')
