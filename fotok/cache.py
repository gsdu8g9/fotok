"""
This file abstracts different cache implementations.
Currently there is only Redis cache.
"""

import json
import redis
from . import models, protocol

class DBFetcher:
    """
    This class decouples database interaction from cache interaction
    """

    def __get_user(self, user_id):
        return models.User.query.filter_by(id=user_id).first()

    def __get_photo(self, photo_id):
        return models.Photo.query.filter_by(id=photo_id).first()

    def __get_comment(self, comment_id):
        return models.Comment.query.filter_by(id=comment_id).first()

    def fetch_recent_photos(self):
        s = protocol.Serializer()
        return s.serialize(models.Photo.recent())

    def fetch_user_recent_photos(self, user_id):
        user = self.__get_user(user_id)
        s = protocol.Serializer(include_user=False)
        return s.serialize(user.recent_photos())

    def fetch_photo_recent_comments(self, photo_id):
        photo = self.__get_photo(photo_id)
        s = protocol.Serializer()
        return s.serialize(photo.recent_comments())

class RedisCache:
    """
    This class provides absctract cache interface using Redis as a backend.
    """

    def __init__(self, config, fetcher):
        self.r = redis.StrictRedis(config['REDIS_HOST'], config['REDIS_PORT'], config['REDIS_DB'])
        self.fetcher = fetcher
        self.token_ttl = config['TOKEN_TTL']
        self.recent_photos = config['RECENT_PHOTOS']
        self.recent_comments = config['RECENT_COMMENTS']

        self.s = protocol.Serializer()

    def put_user_token(self, user, token):
        self.r.set(token, user, ex=self.token_ttl)

    def get_user_by_token(self, token):
        user = self.r.get(token)

        if user is not None:
            return int(user)
        else:
            return None

    # The following three methods clearly need some generalization
    # Maybe it's worth introducing generic Feed class that will incapsulate various feed types:
    # all photos, user's photos, photo's comments and whatever else.

    # These methods work as follows:
    # - get recent objects from Redis
    # - check if there's enough of them
    # - if not, load the rest from DB
    # - finally, return the result

    def get_recent_photos(self):
        photos = [self.s.load(photo.decode('utf8')) for photo in self.r.lrange('recent_photos', 0, -1)]

        if len(photos) < self.recent_photos:
            count = len(photos)
            photos = self.fetcher.fetch_recent_photos()
            for photo in photos[count:]:
                self.r.rpush('recent_photos', self.s.dump(photo))

        return photos

    def get_user_recent_photos(self, user_id):
        key = 'user:{}:photos'.format(user_id)
        photos = [self.s.load(photo.decode('utf8')) for photo in self.r.lrange(key, 0, -1)]

        if len(photos) < self.recent_photos:
            count = len(photos)
            photos = self.fetcher.fetch_user_recent_photos(user_id)
            for photo in photos[count:]:
                self.r.rpush(key, self.s.dump(photo))

        return photos

    def get_photo_recent_comments(self, photo_id):
        key = 'photo:{}:comments'.format(photo_id)
        comments = [self.s.load(comment.decode('utf8')) for comment in self.r.lrange(key, 0, -1)]

        if len(comments) < self.recent_comments:
            count = len(comments)
            comments = self.fetcher.fetch_photo_recent_comments(photo_id)
            for comment in comments[count:]:
                self.r.rpush(key, self.s.dump(comment))

        return comments

    # And this part implements a message queue on top of the cache
    # It is used to push updates to feedserver and finally to the clients

    def __cache_task(self, kind, data):
        task = {'kind': kind}
        task.update(data)
        self.r.rpush('sio_task_queue', self.s.dump(task))

    def cache_new_photo(self, photo):
        self.__cache_task('new_photo', {'photo': photo})

    def cache_new_comment(self, comment, photo_id):
        self.__cache_task('new_comment', {'comment': comment, 'photo_id': photo_id})

# Kinda abstract factory that creates specific Cache object
def create_cache(kind, config):
    fetcher = DBFetcher()
    if kind == 'redis':
        return RedisCache(config, fetcher)
    else:
        raise ValueError('Unknown cache kind')
