import contextlib
import threading

from common import Vector


FPS = 60
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

config = threading.local()
config.camera_offset = Vector(0, 0)


@contextlib.contextmanager
def camera_offset_context(x, y):
    config.camera_offset = Vector(int(x), int(y))
    yield
    config.camera_offset = Vector(0, 0)
