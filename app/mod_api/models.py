'''
The JWT authentication herein was achieved by following this tutorial:
https://realpython.com/blog/python/token-based-authentication-with-flask
'''

import datetime
import jwt

from app import app, db, flask_bcrypt

class User(db.Model):
    u_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    #video_ids = db.relationship('Video', backref='user', lazy='dynamic')
    registered_on = db.Column(db.DateTime, nullable=False)
    last_active_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password_hash = flask_bcrypt.generate_password_hash(password, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        now = datetime.datetime.now()
        self.registered_on = now
        self.last_active_on = now

    def encode_auth_token(self):
        now = datetime.datetime.now()
        delta = datetime.timedelta(seconds=100000) # TODO: change
        payload = {
            'exp': now + delta,
            'iat': now,
            'sub': self.u_id
            }
        return jwt.encode(
            payload, 
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
            )

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'
    
    def __repr__(self):
        return '<User %d>' % self.u_id
        
class Video(db.Model):
    # TODO: many more fields
    v_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
class BlacklistToken(db.Model):
    t_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    @staticmethod
    def check_blacklist(auth_token):
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        return True if res else False

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
