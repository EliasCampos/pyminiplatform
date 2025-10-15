import enum

import pygame

from miniplatform.configs import STATIC_DIR


class Sound(enum.Enum):
    VICTORY = 1, "victory.wav"
    FAIL = 1, "fail.wav"
    JUMP = 2, "jump.wav"
    COIN = 3, "coin.wav"
    TIME_STOP = 4, "time_stop.wav"
    WORLD_RESET = 4, "world_reset.wav"

    def __init__(self, channel_id, filename):
        self._channel_id = channel_id
        self._sound_path = STATIC_DIR / "sounds" / filename
        self._sound = None

    def play(self):
        if not self._sound:
            self._sound = pygame.mixer.Sound(str(self._sound_path))

        sound_channel = pygame.mixer.Channel(self._channel_id)
        if not sound_channel.get_busy():
            sound_channel.play(self._sound)


def play_soundtrack(name="soundtrack"):
    soundtrack_path = STATIC_DIR / "music" / f"{name}.ogg"
    pygame.mixer.music.load(str(soundtrack_path))
    pygame.mixer.music.play(-1)
