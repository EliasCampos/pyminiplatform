import enum
from functools import cached_property

import pygame

from miniplatform.configs import STATIC_DIR


class Sound(enum.Enum):
    VICTORY = 1, "victory.wav"
    FAIL = 1, "fail.wav"
    JUMP = 2, "jump.wav"
    COIN = 3, "coin.wav"
    TIME_STOP = 4, "time_stop.wav"
    WORLD_RESET = 5, "world_reset.wav"
    PUNCH = 6, "punch.wav"

    def __init__(self, channel_id, filename):
        self._channel_id = channel_id
        self._sound_path = STATIC_DIR / "sounds" / filename
        self._sound = None

    def play(self):
        if not self._sound:
            self._sound = pygame.mixer.Sound(str(self._sound_path))

        if not self.sound_channel.get_busy():
            self.sound_channel.play(self._sound)

    def pause(self):
        if self._sound and self.sound_channel.get_busy():
            self.sound_channel.pause()

    def unpause(self):
        if self._sound and self.sound_channel.get_busy():
            self.sound_channel.unpause()

    def stop(self):
        if self._sound and self.sound_channel.get_busy():
            self.sound_channel.stop()

    @cached_property
    def sound_channel(self):
        return pygame.mixer.Channel(self._channel_id)


def play_soundtrack(name="soundtrack"):
    soundtrack_path = STATIC_DIR / "music" / f"{name}.ogg"
    pygame.mixer.music.load(str(soundtrack_path))
    pygame.mixer.music.play(-1)
