"""
This file implements cache interface from the feedserver's side.
It's purpose is to receive tasks from main web app, maintain cache state and notify clients
that listen to various feeds.
"""

import json
import redis
from . import config, sio

# This class can be wrapped into factory or whatever if the need for other caches arises

class RedisCache:

    def __init__(self):
        self.r = redis.StrictRedis(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB)

    def loop(self):
        while True:
            _, task = self.r.blpop(['sio_task_queue'])
            task = json.loads(task.decode(('utf8')))

            if task['kind'] == 'new_photo':
                self.add_new_photo(task['photo'])
            elif task['kind'] == 'new_comment':
                self.add_new_comment(task['comment'], task['photo_id'])

    def add_new_photo(self, photo):
        # Deliver new photo to users
        sio.emit('new_photo', photo, room='feed')
        sio.emit('new_photo', photo, room='user{}'.format(photo['user']['id']))

        jphoto = json.dumps(photo)

        # And update our cache state
        self.r.lpush('recent_photos', jphoto)
        self.r.ltrim('recent_photos', 0, config.RECENT_PHOTOS-1)

        key = 'user:{}:photos'.format(photo['user']['id'])
        self.r.lpush(key, jphoto)
        self.r.ltrim(key, 0, config.RECENT_PHOTOS-1)

    def add_new_comment(self, comment, photo_id):
        # Logic is the same as above
        sio.emit('new_comment', comment, room='photo{}'.format(photo_id))

        jcomment = json.dumps(comment)

        key = 'photo:{}:comments'.format(photo_id)
        self.r.lpush(key, jcomment)
        self.r.ltrim(key, 0, config.RECENT_COMMENTS-1)

Cache = RedisCache
