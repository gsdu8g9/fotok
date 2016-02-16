"""
This file stores configuration for both the web app and feed server.
Should be changed on deployment.
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
SECRET_KEY = 'abcdimverysilly'
MAX_CONTENT_LENGTH = 1024*1024
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'fotok.db')

CACHE_KIND = 'redis'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
TOKEN_TTL = 1800

RECENT_PHOTOS = 10
RECENT_COMMENTS = 3

FEEDSERVER_HOST = '127.0.0.1'
FEEDSERVER_PORT = 8000

if FEEDSERVER_PORT == 80:
    FEEDSERVER_URL = 'http://{}/'.format(FEEDSERVER_HOST)
else:
    FEEDSERVER_URL = 'http://{}:{}/'.format(FEEDSERVER_HOST, FEEDSERVER_PORT)

MAX_WIDTH = 1920
MIN_WIDTH = 100

MAX_HEIGHT = 1080
MIN_HEIGHT = 100

