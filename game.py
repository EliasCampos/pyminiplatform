import pygame

import configs
from levels import Level


class Game:

    def __init__(self):
        self._font = pygame.font.Font(None, 48)

        self.levels = Level.get_default_set()
        self.level = None
        iter(self)
        next(self)

    def update_state(self, time):
        if not self.level:
            return

        self.level.update(time)

        if not self.level.is_running:
            if self.level.is_complete:
                try:
                    next(self)
                except StopIteration:
                    self.level = None
            else:
                self.level.reset()

    def render(self, screen):
        if not self.level:
            self._draw_game_over(screen)
        else:
            self.level.redraw(screen)

    def _draw_game_over(self, screen):
        end_text = self._font.render("Congratulations, You Won!", True, (0, 0, 0))
        screen.blit(end_text, (configs.WINDOW_WIDTH * 0.1, configs.WINDOW_HEIGHT * 0.3))

    def __iter__(self):
        self.levels_iter = iter(self.levels)
        return self

    def __next__(self):
        self.level = next(self.levels_iter)
        self.level.reset()
