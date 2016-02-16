"""
This file declares URLs that are part of REST-like api accessible by JavaScript or other clients.
Currently API token can be obtained only by browser login with cookies, powered by Flask-Login.
"""

import os, binascii

from functools import wraps
from flask import request, jsonify
from flask.ext.login import login_required, current_user
from . import app, db, cache, models, protocol

def load_token():
    """
    This function abstracts the way of loading tokens from input request.
    Currently it uses HTTP Authorization header with Basic auth type.
    """

    auth_data = request.authorization
    if auth_data is None:
        return None
    return auth_data.password

def closed_api(f):
    """
    This decorator ensures that API call bears correct token and injects User object into function arguments
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = load_token()
        user_id = cache.get_user_by_token(token)

        if user_id is None:
            return protocol.ErrorMessage.NotAuthorized()

        user = models.User.query.filter_by(id=user_id).first()

        return f(user, *args, **kwargs)

    return wrapper

def load_user(user_id):
    user = models.User.query.filter_by(id=user_id).first()
    if user is None:
        return None, protocol.ErrorMessage.UserNotFound()

    return user, None

def load_photo(photo_id):
    photo = models.Photo.query.filter_by(id=photo_id).first()
    if photo is None:
        return None, protocol.ErrorMessage.PhotoNotFound()

    return photo, None

@app.route('/api/user/token')
def getToken():
    #TODO Support other types of auth besides Flask-Login based
    if not current_user.is_authenticated:
        return protocol.ErrorMessage.NotAuthorized()

    token = binascii.hexlify(os.urandom(20))
    cache.put_user_token(current_user.id, token)

    s = protocol.Serializer()

    return protocol.SimpleMessage({
        'token': token.decode('ascii'),
        'user': s.serialize(models.User.query.filter_by(id=current_user.id).first())
    }).data

@app.route('/api/feed')
@app.route('/api/feed/<int:offset>')
def getRecentPhotos(offset=None):
    if offset is None:
        photos = cache.get_recent_photos()
    else:
        s = protocol.Serializer()
        photos = s.serialize(models.Photo.older_than(offset))

    return protocol.SimpleMessage({
        'photos': photos
    }).data

@app.route('/api/user/<int:id>/subscriptions')
def getUserSubscriptions(id):
    user, error = load_user(id)
    if error is not None:
        return error

    s = protocol.Serializer()
    return protocol.SimpleMessage({
        'subscriptions': s.serialize(user.subscriptions)
    }).data

@app.route('/api/user/<int:id>/subscribe', methods=['POST'])
@closed_api
def addUserSubscription(subscriber, id):
    user, error = load_user(id)
    if error is not None:
        return error

    if subscriber.id == user.id:
        return protocol.ErrorMessage.SubscriptionError()

    user.subscribers.append(subscriber)

    db.session.commit()

    return protocol.SimpleMessage({}).data

@app.route('/api/user/<int:id>/photos')
@app.route('/api/user/<int:id>/photos/<int:offset>')
def getUserPhotos(id, offset=None):
    user, error = load_user(id)
    if error is not None:
        return error

    if offset is None:
        photos = cache.get_user_recent_photos(user.id)
    else:
        s = protocol.Serializer(include_user=False)
        photos = s.serialize(user.photos_older_than(offset))

    return protocol.SimpleMessage({
        'photos': photos
    }).data

@app.route('/api/photo/<int:id>/comments')
@app.route('/api/photo/<int:id>/comments/<int:offset>')
def getPhotoComments(id, offset=None):
    photo, error = load_photo(id)
    if error is not None:
        return error

    if offset is None:
        comments = cache.get_photo_recent_comments(photo.id)
    else:
        s = protocol.Serializer()
        comments = s.serialize(photo.comments_older_than(offset))

    return protocol.SimpleMessage({
        'comments': comments
    }).data

@app.route('/api/photo/<int:id>/comment', methods=['POST'])
@closed_api
def addPhotoComment(user, id):
    photo, error = load_photo(id)
    if error is not None:
        return error

    text = request.form.get('comment')
    if not text:
        return protocol.ErrorMessage.BadCommentFormat()

    comment = models.Comment(text=text, photo=photo, author=user)

    db.session.add(comment)
    db.session.commit()

    s = protocol.Serializer()
    cache.cache_new_comment(s.serialize(comment), photo.id)

    return protocol.SimpleMessage({}).data

@app.route('/api/photo/add', methods=['POST'])
@closed_api
def addPhoto(user):
    width = request.form.get('width')
    height = request.form.get('height')

    if width is None or height is None:
        return protocol.ErrorMessage.BadPhoto()

    photo = models.Photo()
    try:
        photo.width = int(width)
        photo.height = int(height)
    except ValueError:
        return protocol.ErrorMessage.BadPhoto()

    if photo.width > app.config['MAX_WIDTH'] or \
       photo.width < app.config['MIN_WIDTH'] or \
       photo.height > app.config['MAX_HEIGHT'] or \
       photo.height < app.config['MIN_HEIGHT']:
        return protocol.ErrorMessage.BadPhoto()

    photo.user = user

    db.session.add(photo)
    db.session.commit()

    s = protocol.Serializer()
    cache.cache_new_photo(s.serialize(photo))

    return protocol.SimpleMessage({}).data
