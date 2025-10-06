import os

import pygame

from miniplatform import configs
from miniplatform import effects
from miniplatform.levels import Level


class Game:

    def __init__(self):
        self._font = pygame.font.Font(None, 72)
        self._end_text = self._font.render("Congratulations, You Won!", True, (0, 0, 0))
        self._end_text_rect = self._end_text.get_rect(
            center = (configs.WINDOW_WIDTH * 0.5, configs.WINDOW_HEIGHT * 0.5),
        )

        self.levels = Level.get_default_set()
        self.level = None

        if level_number := os.getenv('TEST_LEVEL_NUMBER'):
            # test mode
            for i in range(int(level_number)):
                self.next_level()
        else:
            self.next_level()
        self.level.reset()

        effects.play_soundtrack()

    def update_state(self, time):
        if not self.level:
            return

        self.level.update(time)

        if not self.level.is_running:
            if self.level.is_complete:
                try:
                    self.next_level()
                except IndexError:
                    self.level = None
                    effects.play_soundtrack(name="ending")
                else:
                    self.level.reset()
            else:
                self.level.reset()

    def render(self, screen):
        if not self.level:
            self._draw_game_over(screen)
        else:
            self.level.redraw(screen)

    def _draw_game_over(self, screen):
        screen.blit(self._end_text, self._end_text_rect)

    def next_level(self):
        self.level = self.levels.pop(0)
