
import eventlet
from . import config, sapp, cache

# Do not let cache loop stop
# TODO: Add more logging
def cache_loop():
    while True:
        try:
            cache.loop()
        except Exception as e:
            print('Cache loop failed with', e)

def main():
    host = config.FEEDSERVER_HOST
    port = config.FEEDSERVER_PORT

    eventlet.spawn(cache_loop)

    eventlet.wsgi.server(eventlet.listen((host, port)), sapp)
