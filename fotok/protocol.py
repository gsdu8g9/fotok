"""
This file abstracts the representation of data that is passed to clients and stored in cache.
Serializer class converts objects into Python dictionaries which are later converted to JSON where needed.
"""

import json
from flask import jsonify
from . import models

class Message:

    def _payload(self):
        raise NotImplementedError

    def _result(self):
        raise NotImplementedError

    @property
    def data(self):
        answer = {
            'result': self._result()
        }
        answer.update(self._payload())

        return jsonify(answer)

class ErrorMessage(Message):

    def __init__(self, error):
        super(ErrorMessage, self).__init__()

        self.error = error

    def _result(self):
        return 'error'

    def _payload(self):
        return {'message': self.error}

    @classmethod
    def NotAuthorized(cls):
        return cls('NotAuthorized').data

    @classmethod
    def UserNotFound(cls):
        return cls('UserNotFound').data

    @classmethod
    def PhotoNotFound(cls):
        return cls('PhotoNotFound').data

    @classmethod
    def SubscriptionError(cls):
        return cls('SubscriptionError').data

    @classmethod
    def BadCommentFormat(cls):
        return cls('BadCommentFormat').data

    @classmethod
    def BadPhoto(cls):
        return cls('BadPhoto').data

class SimpleMessage(Message):

    def __init__(self, payload):
        super(SimpleMessage, self).__init__()

        self.payload = payload

    def _result(self):
        return 'ok'

    def _payload(self):
        return self.payload

class Serializer:

    def __init__(self, include_user=True):
        self.include_user = include_user

    def serialize(self, obj):
        if isinstance(obj, models.User):
            return self.serializeUser(obj)
        elif isinstance(obj, models.Photo):
            return self.serializePhoto(obj)
        elif isinstance(obj, models.Comment):
            return self.serializeComment(obj)
        elif isinstance(obj, list):
            return [self.serialize(elem) for elem in obj]

    def serializeUser(self, user):
        return {
            'id': user.id,
            'username': user.username,
        }

    def serializePhoto(self, photo):
        data = {
            'id': photo.id,
            'width': photo.width,
            'height': photo.height,
            'URL': photo.URL,
            'time': photo.time.timestamp()
        }
        if self.include_user:
            data['user'] = self.serialize(photo.user)
        return data

    def serializeComment(self, comment):
        data = {
            'id': comment.id,
            'text': comment.text,
            'time': comment.time.timestamp()
        }
        if self.include_user:
            data['author'] = self.serialize(comment.author)
        return data

    def dump(self, data):
        return json.dumps(data)

    def load(self, data):
        return json.loads(data)
