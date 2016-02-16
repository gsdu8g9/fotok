
import eventlet
eventlet.monkey_patch()

import socketio

sio = socketio.Server(async_mode='eventlet')
sapp = socketio.Middleware(sio)

from .. import config

from .cache import Cache

cache = Cache()

from . import events, main
