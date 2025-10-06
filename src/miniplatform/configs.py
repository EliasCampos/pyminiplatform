import pathlib
import threading


FPS = 60

STATIC_DIR = pathlib.Path(__file__).parent / "static"

config = threading.local()
config.offset_x = 0
config.offset_y = 0
config.color_factor = 1


def adjust_color(color):
    factor = config.color_factor
    if factor  == 1:
        return color
    return tuple(
        ((255 - p) * (1 - factor) + p * factor) / 2
        for p in color
    )
