'''
The JWT authentication herein was achieved by following this tutorial:
https://realpython.com/blog/python/token-based-authentication-with-flask
'''

import datetime
import jwt
import math
import cv2
import StringIO
import os

from app import app, db, flask_bcrypt
from app import video_client

from sqlalchemy import and_, func, case, desc, not_

permissions = db.Table('permissions',
                        db.Column('permission_id', db.Integer, db.ForeignKey('permission.p_id')),
                        db.Column('group_id', db.Integer, db.ForeignKey('usergroup.group_id'))
                        )

class Permission(db.Model):
    p_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    @staticmethod
    def initialize_permissions():
        for name in app.config.get('PERMISSIONS'):
            p = Permission.query.filter_by(name=name).first()
            if not p:
                p = Permission(name)
                db.session.add(p)
                db.session.commit()

    @staticmethod
    def get_permissions_on_user(u_id):
        return Restriction.query.filter(and_(name==name, Restriction.users.any(User.u_id==u_id))).first()

class Usergroup(db.Model):
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    permissions = db.relationship('Permission', secondary=permissions, backref=db.backref('usergroups', lazy='dynamic'))

    def __init__(self, name, permissions):
        self.name = name
        self.add_permissions(permissions)


    def add_permissions(self, permissions):
        for name in permissions:
            permission = Permission.query.filter_by(name=name).first()
            if (permission is not None) and (permission not in self.permissions):
                self.permissions.append(permission)
        db.session.commit()

    @staticmethod
    def initialize_usergroups():
        usergroups = app.config.get('USER_GROUPS')
        for name in usergroups:
            p = Usergroup.query.filter_by(name=name).first()
            if not p:
                p = Usergroup(name,usergroups[name])
                db.session.add(p)
                db.session.commit()


class User(db.Model):
    u_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('usergroup.group_id'))
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

        usergroup = Usergroup.query.filter_by(name='member').first()
        self.group_id = usergroup.group_id 

    def commit(self, insert = False):
        now = datetime.datetime.now()
        self.last_active_on = now
        if insert:
            db.session.add(self)
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

    def get_score(self):
        votes = Vote.query.filter_by(u_id = self.u_id).count()
        video_scores = db.session.query(func.sum(case(value=Vote.upvote, whens={1:1, 0:- 1}, else_=0)).label('net_votes')).select_from(Video).join(Vote).filter(Video.u_id == self.u_id)
        video_score = db.session.query(func.sum(video_scores.subquery().columns.net_votes)).scalar()
        video_score = 0 if not video_score else video_score
        return votes + video_score + self.stored_score

    def delete(self):
        # delete videos owned by the user
        videos = Video.query.filter_by(u_id=self.u_id)
        for video in videos:
            video.delete()

        # delete hall of fame videos produced by the user
        hof_videos = HallOfFame.query.filter_by(u_id=self.u_id)
        for video in hof_videos:
            video.delete()

        db.session.delete(self)
        db.session.commit()

    def check_user_permission(self, permission):
        usergroup = Usergroup.query.filter_by(group_id=self.group_id).first()
        permission = Permission.query.filter_by(name=permission).first()
        if (usergroup is not None) and (permission is not None) and (permission in usergroup.permissions):
            return True
        else:
            return False

    def count_warnings(self):
        return Banned_Video.query.filter_by(u_id=self.u_id).count()

    def get_warning_ids(self):
        banned_videos = Banned_Video.query.filter_by(u_id=self.u_id, user_warned=False)
        bv_ids = []
        for video in banned_videos:
            bv_ids.append(video.bv_id)
            video.user_warned = True
            video.commit()

        return bv_ids
        
    def restrict(self):
        if self.count_warnings() >= app.config.get('RESTRICT_THRESHOLD'):
            self.group_id = Usergroup.query.filter_by(name='restricted').first().group_id 
            self.commit()       

    @staticmethod
    def get_user_by_id(_id):
        return User.query.filter_by(u_id=_id).first()

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

banned_tags = db.Table('banned_tags',
                        db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id')),
                        db.Column('banned_video_id', db.Integer, db.ForeignKey('banned__video.bv_id'))
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
    voted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, u_id, vid_id, upvote):
        self.u_id = u_id
        self.vid_id = vid_id
        self.upvote = upvote
        self.voted_on = datetime.datetime.now()

    def commit(self, insert=False):
        self.voted_on = datetime.datetime.now()
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

class Flag(db.Model):
    flag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    v_id = db.Column(db.Integer, db.ForeignKey('video.v_id'))

    def __init__(self, u_id, v_id):
        self.u_id = u_id
        self.v_id = v_id

    def commit(self, insert=False):
        if insert:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Video(db.Model):
    v_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    uploaded_on = db.Column(db.DateTime, nullable=False)
    last_edited_on = db.Column(db.DateTime, nullable=False)
    lat = db.Column(db.Float(precision=8), nullable=False)
    lon = db.Column(db.Float(precision=8), nullable=False)
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('videos', lazy='dynamic'))
    votes = db.relationship('Vote', backref='video', lazy='dynamic')
    flags = db.relationship('Flag', backref='video', lazy='dynamic')
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
        # video.seek(0)
        # video.save('temp.avi')
        # image = video_to_frames('temp.avi')
        # thumbnail = image_to_thumbs(image)
        # cap = cv2.VideoCapture(video.read())
        # _, img = cap.read()
        # thumb_buf = StringIO.StringIO()
        # thumb_buf.write(img) 
        # video_client.upload_thumbnail(self.filepath, thumb_buf)
        # thumb_buf.close()
        # cap.release()

    def retrieve(self):
        return video_client.retrieve_videos([self.filepath])[0]

    def retrieve_thumbnail(self):        
        return video_client.retrieve_thumbnail(self.filepath)

    def add_tags(self, tags):
        for tag in tags:
            t = Tag.get_or_create_tag(tag)
            if t not in self.tags:
                self.tags.append(t)
        self.commit()

    def net_votes(self):
        return sum((1 if vote.upvote else -1 for vote in self.votes))

    def delete_status(self):
        score = self.net_votes() - 2 * Flag.query.filter_by(v_id=self.v_id).count()
        if score < app.config.get('DELETE_THRESHOLD'):
            # ban video
            banned_video = Banned_Video(self)
            banned_video.commit(insert=True)
            self.delete()

            # check owner needs to be banned
            user = User.get_user_by_id(self.u_id)
            user.restrict()

            return True 
        else:
            return False

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

        # delete flags associated with video
        expired_flags = Flag.query.filter_by(v_id = self.v_id)
        for flag in expired_flags:
            flag.delete()

        # delete the video
        video_client.delete_videos([self.filepath])
        db.session.delete(self)
        db.session.commit()

    def delete_thumbnail(self):
        video_client.delete_thumbnails([self.filepath])

    @staticmethod
    def get_video_by_id(_id):
        return Video.query.filter_by(v_id=_id).first()

    @staticmethod
    def get_videos_by_user_id(u_id, limit=5, offset=0, sort_by='recent'):           
        videos = Video.query.filter_by(u_id=u_id)

        # order the videos; default to sort_by recency        
        order = Video.uploaded_on.desc()
        if sort_by == 'popular':
            videos = videos.outerjoin(Vote, Video.votes).group_by(Video.v_id)      
            order = func.sum(case(value=Vote.upvote, whens={1:1, 0:- 1}, else_=0)).desc()  

        return Video.order_limit_offset_videos(videos, limit, offset, order) 

    @staticmethod
    def get_liked_videos_by_user_id(u_id, limit=5, offset=0, sort_by='recent'):        
        # order the videos; default to sort_by recency 
        if sort_by == 'popular':
            videos = Video.query.filter(Video.votes.any(and_(Vote.u_id==u_id, Vote.upvote==True)))
            videos = videos.outerjoin(Vote, Video.votes).group_by(Video.v_id)      
            order = func.sum(case(value=Vote.upvote, whens={1:1, 0:- 1}, else_=0)).desc()
        else:
            videos = Video.query.join(Vote).filter((and_(Vote.u_id==u_id, Vote.upvote==True)))       
            order = Vote.voted_on.desc()

        return Video.order_limit_offset_videos(videos, limit, offset, order)      

    @staticmethod
    def search(lat, lon, u_id, tags=[], limit=5, offset=0, sort_by='popular'):            
        # fetch videos based on tags, flags and geolocation
        tag_filter = and_()
        tags = tags if tags else []
        for tag in tags:
            tag_filter =  and_(tag_filter, Video.tags.any(Tag.name == tag))
        lat_max, lat_min, lon_max, lon_min = boxUser(lat, lon)
        geo_filter = and_(Video.lat < lat_max, Video.lat > lat_min, Video.lon < lon_max, Video.lon > lon_min)
        flagged_filter = not_(Video.flags.any(Flag.u_id==u_id))
        videos = Video.query.join(Tag, Video.tags).filter(and_(and_(tag_filter, geo_filter), flagged_filter)) if tags else Video.query.filter(and_(flagged_filter, geo_filter))
        
        # order the videos; default to sort_by popularity        
        videos = videos.outerjoin(Vote, Video.votes).group_by(Video.v_id)      
        order = func.sum(case(value=Vote.upvote, whens={1:1, 0:- 1}, else_=0)).desc()    
        if sort_by == 'recent':
            order = Video.uploaded_on.desc()

        return Video.order_limit_offset_videos(videos, limit, offset, order)

    @staticmethod
    def order_limit_offset_videos(videos, limit, offset, order):
        # order videos
        videos = videos.order_by(order)

        # limit videos
        videos = videos.limit(limit)

        # offset the videos
        videos = videos.offset(offset)

        return videos.all()

class Banned_Video(db.Model):
    bv_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    uploaded_on = db.Column(db.DateTime, nullable=False)
    lat = db.Column(db.Float(precision=8), nullable=False)
    lon = db.Column(db.Float(precision=8), nullable=False)
    tags = db.relationship('Tag', secondary=banned_tags, backref=db.backref('banned_videos', lazy='dynamic'))
    filepath = db.Column(db.String(84), nullable=False)
    user_warned = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, video):
        self.u_id = video.u_id
        self.uploaded_on = video.uploaded_on
        self.lat = video.lat
        self.lon = video.lon

        # handle video file
        self.filepath = video.filepath 
        video_client.upload_banned_video(self.filepath, video.retrieve())   

        # pass tags to banned video
        for tag in video.tags:
            t = Tag.get_or_create_tag(tag.name)
            if t not in self.tags:
                self.tags.append(t)

    def commit(self, insert=False):
        if insert:
            db.session.add(self)
        db.session.commit()

    def retrieve(self):
        return video_client.retrieve_banned_video(self.filepath)


    @staticmethod
    def get_banned_video_by_id(_id):
        return Banned_Video.query.filter_by(bv_id=_id).first()

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
        return video_client.retrieve_thumbnail(self.filepath)[0]

    def commit(self, insert = False):
        if insert:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        video_client.delete_videos([self.filepath], is_hof=True)
        # video_client.delete_thumbnails([self.filepath])
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

            if all_HoF < app.config.get('HALL_OF_FAME_LIMIT'):
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
            # else:
                # video.delete_thumbnail()

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

def video_to_frames(video_filename):
    """Extract frames from video"""
    cap = cv2.VideoCapture(video_filename)
    if not cap.isOpened():
        cap.open(video_filename)
    if cap.isOpened():
        success, image = cap.read()
        if success:
            return image
        else:
            print 'error2'
    else:
        print 'error1'
    return None

def image_to_thumbs(img):
    """Create thumbs from image"""
    height, width, channels = img.shape
    thumbs = {"original": img}
    sizes = [640, 320, 160]
    for size in sizes:
        if (width >= size):
            r = (size + 0.0) / width
            max_size = (size, int(height * r))
            thumbs[str(size)] = cv2.resize(img, max_size, interpolation=cv2.INTER_AREA)
    return thumbs

