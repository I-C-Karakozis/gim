# Import flask dependencies
from flask import Blueprint

from app import db

mod_api = Blueprint('api', __name__, url_prefix='/api')

@mod_api.route('/Videos/', methods=['GET', 'POST'])
def videos():
    return 'TODO'

@mod_api.route('/Users/', methods=['GET', 'POST'])
def users():
    return 'TODO'
