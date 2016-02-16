"""
This file describes ORM classes that represent various entities in the database.
It also assigns additional functionality to models, according to MVC spirit.
"""

import dateutil.tz, datetime
from sqlalchemy.sql import func
from hashlib import sha256
from . import app, db

class DateTimeField(db.TypeDecorator):
    """
    This class stores datetime objects as UNIX timestamps and tries to handle timezone correctly.
    """

    impl = db.Integer

    def process_bind_param(self, value, dialect):
        # Get datetime object, convert into timestamp
        if value is not None:
            if value.tzinfo is None: #Naive time, assume local
                value = value.replace(tzinfo=dateutil.tz.tzlocal())

            value = int(value.astimezone(dateutil.tz.tzutc()).timestamp())

        return value

    def process_result_value(self, value, dialect):
        # Get timestamp, convert into aware datetime object
        if value is not None:
            value = datetime.datetime.utcfromtimestamp(value).replace(tzinfo=dateutil.tz.tzutc())

        return value

def convert_timestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=dateutil.tz.tzutc())

subscriptions = db.Table('subscriptions',
        db.Column('subscriber_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('subscribed_id', db.Integer, db.ForeignKey('user.id')),
)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    time = db.Column(DateTimeField, default=datetime.datetime.now)

    text = db.Column(db.Unicode(512))

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    time = db.Column(DateTimeField, default=datetime.datetime.now)

    comments = db.relationship('Comment', backref='photo', lazy='dynamic')

    @property
    def URL(self):
        return 'http://lorempixel.com/{}/{}/cats/'.format(self.width, self.height)

    @classmethod
    def recent(cls):
        return cls.query.order_by(cls.id.desc()).limit(app.config['RECENT_PHOTOS']).all()

    @classmethod
    def older_than(cls, timestamp):
        time_offset = convert_timestamp(timestamp)
        return cls.query.order_by(cls.id.desc()).filter(Photo.time < time_offset).limit(app.config['RECENT_PHOTOS']).all()

    def recent_comments(self):
        return self.comments.order_by(Comment.id.desc()).limit(app.config['RECENT_COMMENTS']).all()

    def comments_older_than(self, timestamp):
        time_offset = convert_timestamp(timestamp)
        return self.comments.order_by(Comment.id.desc()).filter(Comment.time < time_offset).limit(app.config['RECENT_COMMENTS']).all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(100), unique=True)
    password = db.Column(db.Unicode(100))

    photos = db.relationship('Photo', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    subscriptions = db.relationship('User',
        secondary=subscriptions,
        primaryjoin=(id == subscriptions.c.subscriber_id),
        secondaryjoin=(id == subscriptions.c.subscribed_id),
        backref="subscribers"
    )

    # Following four methods are needed for Flask-Login

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password = sha256(password.encode('utf8')).hexdigest()

    def check_password(self, password):
        digest = sha256(password.encode('utf8')).hexdigest()
        return digest == self.password

    def recent_photos(self):
        return self.photos.order_by(Photo.id.desc()).limit(app.config['RECENT_PHOTOS']).all()

    def photos_older_than(self, timestamp):
        time_offset = convert_timestamp(timestamp)
        return self.photos.order_by(Photo.id.desc()).filter(Photo.time < time_offset).limit(app.config['RECENT_PHOTOS']).all()
