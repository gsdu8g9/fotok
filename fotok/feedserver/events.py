"""
This file is supposed to store handlers for Socket.IO communication between clients and server.
As for now, it only registers clients in various rooms.
"""

from . import sio, cache

@sio.on('subscribe')
def subscribe(sid, data):
    channel = data.get('channel')
    if not channel:
        return

    sio.enter_room(sid, channel)

@sio.on('unsubscribe')
def unsubscribe(sid, data):
    channel = data.get('channel')
    if not channel:
        return

    sio.leave_room(sid, channel)
