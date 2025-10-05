import enum
import pathlib

import pygame


MEDIA_DIR = pathlib.Path(__file__).parent / "media"


class Sound(enum.Enum):
    VICTORY = 1, "victory.wav"
    FAIL = 1, "fail.wav"
    JUMP = 2, "jump.wav"
    COIN = 3, "coin.wav"
    TIME_STOP = 4, "time_stop.wav"

    def __init__(self, channel_id, filename):
        self._channel_id = channel_id
        self._sound_path = MEDIA_DIR / "sounds" / filename
        self._sound = None

    def play(self):
        if not self._sound:
            self._sound = pygame.mixer.Sound(str(self._sound_path))

        sound_channel = pygame.mixer.Channel(self._channel_id)
        if not sound_channel.get_busy():
            sound_channel.play(self._sound)


def play_soundtrack():
    soundtrack_path = MEDIA_DIR / "music" / "soundtrack.ogg"
    pygame.mixer.music.load(str(soundtrack_path))
    pygame.mixer.music.play(-1)
