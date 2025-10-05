import enum
import pathlib

import pygame



class Sound(enum.Enum):
    JUMP = 2, "jump.wav"
    COIN = 3, "coin.wav"
    FAIL = 1, "fail.wav"
    VICTORY = 1, "victory.wav"

    def __init__(self, channel_id, filename):
        self._channel_id = channel_id
        self._sound_path = pathlib.Path(__file__).parent / "sounds" / filename
        self._sound = None

    def play(self):
        if not self._sound:
            self._sound = pygame.mixer.Sound(str(self._sound_path))

        sound_channel = pygame.mixer.Channel(self._channel_id)
        if not sound_channel.get_busy():
            sound_channel.play(self._sound)


def play_soundtrack():
    soundtrack_path = pathlib.Path(__file__).parent / "music" / "soundtrack.ogg"
    pygame.mixer.music.load(str(soundtrack_path))
    pygame.mixer.music.play(-1)
