'''
The JWT authentication herein was achieved by following this tutorial:
https://realpython.com/blog/python/token-based-authentication-with-flask
'''

import datetime
import jwt
import math
import cv2
import StringIO

from app import app, db, flask_bcrypt
from app import video_client

from sqlalchemy import and_, func, case, desc

HALL_OF_FAME_LIMIT = 10

class User(db.Model):
    u_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    video = db.relationship('Video', backref='user', lazy='dynamic')
    votes = db.relationship('Vote', backref='user', lazy='dynamic') 
    registered_on = db.Column(db.DateTime, nullable=False)
    last_active_on = db.Column(db.DateTime, nullable=False)
    stored_score = db.Column(db.Integer, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password_hash = flask_bcrypt.generate_password_hash(password, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        now = datetime.datetime.now()
        self.registered_on = now
        self.last_active_on = now
        self.stored_score = 0

    def get_score(self):
        votes = Vote.query.filter_by(u_id = self.u_id).count()
        video_scores = db.session.query(func.sum(case(value=Vote.upvote, whens={1:1, 0:- 1}, else_=0)).label('net_votes')).select_from(Video).join(Vote).filter(Video.u_id == self.u_id)
        video_score = db.session.query(func.sum(video_scores.subquery().columns.net_votes)).scalar()
        video_score = 0 if not video_score else video_score
        return votes + video_score + self.stored_score

    def commit(self, insert = False):
        now = datetime.datetime.now()
        self.last_active_on = now
        if insert:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

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

tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id')),
                db.Column('video_id', db.Integer, db.ForeignKey('video.v_id'))
                )

class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name
        
    @staticmethod
    def get_or_create_tag(name):
        tag = Tag.query.filter_by(name=name).first()
        if tag is None:
            tag = Tag(name)
            db.session.add(tag)
            db.session.commit()
        return tag
        
class Vote(db.Model):
    v_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    vid_id = db.Column(db.Integer, db.ForeignKey('video.v_id'))
    upvote = db.Column(db.Boolean, nullable=False)

    def __init__(self, u_id, vid_id, upvote):
        self.u_id = u_id
        self.vid_id = vid_id
        self.upvote = upvote

    def commit(self, insert = False):
        if insert:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # returns 0 if user has not voted the video, 1 if he has upvoted it and -1 if he has downvoted it
    @staticmethod
    def get_vote(u_id, vid_id):
        user_vote = Vote.query.filter_by(u_id = u_id, vid_id = vid_id).first()
        if user_vote:
            if user_vote.upvote:
                return 1
            else:
                return -1
        else:
            return 0

class Video(db.Model):
    v_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    uploaded_on = db.Column(db.DateTime, nullable=False)
    last_edited_on = db.Column(db.DateTime, nullable=False)
    lat = db.Column(db.Float(precision=8), nullable=False)
    lon = db.Column(db.Float(precision=8), nullable=False)
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('videos', lazy='dynamic'))
    votes = db.relationship('Vote', backref='video', lazy='dynamic')
    filepath = db.Column(db.String(84), nullable=False)

    def __init__(self, video, u_id, lat, lon):
        self.u_id = u_id
        now = datetime.datetime.now()
        self.uploaded_on = now
        self.last_edited_on = now
        self.lat = lat
        self.lon = lon

        # handle video file
        video.seek(0)
        self.filepath = video_client.get_filepath(video.read())
        video_client.upload_video(self.filepath, video)

        # generate video thumbnail; same filepath with video, but in different folder
        cap = cv2.VideoCapture(video.read())
        hello, img = cap.read()
        thumb_buf = StringIO.StringIO()
        thumb_buf.write(img) 
        # question: should I store the StringIO object or should I get itis value and store it as a string? 
        video_client.upload_thumbnail(self.filepath, thumb_buf)
        thumb_buf.close()
        cap.release()

    def retrieve(self):
        return video_client.retrieve_videos([self.filepath])[0]

    def retrieve_thumbnail(self):
        return video_client.retrieve_thumbnails([self.filepath])[0]

    def add_tags(self, tags):
        for tag in tags:
            t = Tag.get_or_create_tag(tag)
            if t not in self.tags:
                self.tags.append(t)
        self.commit()

    def net_votes(self):
        return sum((1 if vote.upvote else -1 for vote in self.votes))

    def commit(self, insert=False):
        if insert:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        # update video owners base score
        user = User.query.filter_by(u_id = self.u_id).first()
        user.stored_score += self.net_votes()
        user.commit()

        # update users' base scores who voted on this video
        voters = User.query.join(Vote).filter(Vote.vid_id == self.v_id)
        for voter in voters:
            voter.stored_score += 1
            voter.commit()

        # delete votes associated with video
        expired_votes = Vote.query.filter_by(vid_id = self.v_id)
        for vote in expired_votes:
            vote.delete()

        # delete the video
        video_client.delete_videos([self.filepath])
        db.session.delete(self)
        db.session.commit()

    def delete_thumbnail():
        video_client.delete_thumbnails([self.filepath])

    @staticmethod
    def get_video_by_id(_id):
        return Video.query.filter_by(v_id=_id).first()

    @staticmethod
    def get_videos_by_user_id(u_id):
        videos = Video.query.filter_by(u_id=u_id) 

        order = Video.uploaded_on.desc()
        videos = videos.order_by(order)

        return videos.all()       

    @staticmethod
    def search(lat, lon, tags=[], limit=5, offset=0, sort_by='popular'):    
        lat_max, lat_min, lon_max, lon_min = boxUser(lat, lon)
        tag_filter = lambda : Video.tags.any(Tag.name.in_(tags)) # holy shit functional programming!!
        geo_filter = and_(Video.lat < lat_max, Video.lat > lat_min, Video.lon < lon_max, Video.lon > lon_min)
        videos = Video.query.join(Tag, Video.tags).filter(and_(tag_filter(), geo_filter)) if tags else Video.query.filter(geo_filter)

        # order the videos        
        videos = videos.outerjoin(Vote, Video.votes).group_by(Video.v_id)

        # default to sort_by popularity
        order = func.sum(case(value=Vote.upvote, whens={1:1, 0:- 1}, else_=0)).desc()
    
        if sort_by == 'recent':
            order = Video.uploaded_on.desc()

        videos = videos.order_by(order)

        # limit videos
        videos = videos.limit(limit)

        # offset the videos
        videos = videos.offset(offset)

        return videos.all()

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


class HallOfFame(db.Model):
    hof_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    uploaded_on = db.Column(db.DateTime, nullable=False)
    lat = db.Column(db.Float(precision=8), nullable=False)
    lon = db.Column(db.Float(precision=8), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    filepath = db.Column(db.String(84), nullable=False)

    def __init__(self, video, net_votes = 0):
        self.u_id = video.u_id
        self.uploaded_on = video.uploaded_on
        self.lat = video.lat
        self.lon = video.lon
        self.score = net_votes
        self.filepath = video.filepath

    def retrieve(self):
        return video_client.retrieve_videos([self.filepath], is_hof=True)[0]

    def retrieve_thumbnail(self):
        return video_client.retrieve_thumbnails([self.filepath])[0]

    def commit(self, insert = False):
        if insert:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        video_client.delete_videos([self.filepath], is_hof=True)
        video_client.delete_thumbnails([self.filepath])
        db.session.delete(self)
        db.session.commit()        

    @staticmethod
    def add_to_hof_or_delete(videos):
        # measure score
        for video in videos:           
            net_votes = video.net_votes() 
            user = User.query.filter_by(u_id = video.u_id).first()

            # update HoF
            last = HallOfFame.retrieve_last()
            all_HoF = len(HallOfFame.sort_desc_and_retrieve_all())

            if all_HoF < HALL_OF_FAME_LIMIT:
                winner = HallOfFame(video, net_votes)
                winner.commit(insert=True)
                video_client.upload_video(winner.filepath, video.retrieve(), is_hof=True)
                user.stored_score += net_votes
                user.commit()
            elif net_votes > last.score:
                winner = HallOfFame(video, net_votes)
                winner.commit(insert=True)   
                video_client.upload_video(winner.filepath, video.retrieve(), is_hof=True)
                last.delete()
                user.stored_score += net_votes
                user.commit()            
            else:
                video.delete_thumbnail()

            video.delete()        

    @staticmethod
    def get_video_by_id(_id):
        return HallOfFame.query.filter_by(hof_id=_id).first()

    @staticmethod
    def sort_desc_and_retrieve_all():
        hof = HallOfFame.query.filter()
        order = HallOfFame.score.desc()
        hof = hof.order_by(order)
        return hof.all()

    @staticmethod
    def retrieve_last():
        hof = HallOfFame.query.filter()
        order = HallOfFame.score.asc()
        hof = hof.order_by(order)
        return hof.first()


# implemented using equirectangular approximation; accurate for small distances
def boxUser(lat, lon):
    R = 6371 # value in kilometers
    radius = 2.5 # initially set to 2.5 km
    c = radius / R

    # edge case to avoid division by zero
    if lat >= 90 or lat <= -90:
        cos_lat = 0.00000000001 # zero approximation; 10^(-1)
    else:
        cos_lat = math.cos(lat)
    lat_radians = math.radians(lat)
    lon_radians = math.radians(lon)    

    # latitude calculations
    lat_max = lat_radians + c
    lat_min = lat_radians - c

    # longitude calculations
    lon_max = lon_radians + c / math.fabs(cos_lat)
    lon_min = lon_radians - c / math.fabs(cos_lat)

    # convert return values to degrees
    lat_max = math.degrees(lat_max)
    lat_min = math.degrees(lat_min)
    lon_max = math.degrees(lon_max)
    lon_min = math.degrees(lon_min)

    # no need check for wrapping around because the edge of the world 
    # is comprised of the ocean and a couple of fringe islandss

    return lat_max, lat_min, lon_max, lon_min

