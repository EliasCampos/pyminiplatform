import threading
import json
import os

import pygame

from miniplatform import effects
from miniplatform.configs import VAR_DIR
from miniplatform.levels import Level
from miniplatform.serializers import Serializable


class Game(Serializable):
    SAVE_GAME_DELAY = 1_000  # every second

    def __init__(self, level_maps=None):
        window_sizes = pygame.display.get_window_size()

        end_font = pygame.font.Font(None, 72)
        self._end_text = end_font.render("Congratulations, You Won!", True, (0, 0, 0))
        self._end_text_rect = self._end_text.get_rect(
            center=tuple(size * 0.5 for size in window_sizes),
        )

        self.level_maps = level_maps if level_maps is not None else Level.load_level_maps()
        self.level = None

        self._is_saving_game = False
        self._save_game_delay = self.SAVE_GAME_DELAY
        self._save_game_thread = None

    def update_state(self, time):
        if not self.level:
            return

        if self._save_game_delay > 0:
            self._save_game_delay = self._save_game_delay - time
        else:
            self.save_game()

        self._handle_keypress(time)
        self.level.update(time)

        if not self.level.is_running:
            if self.level.is_complete:
                try:
                    self.next_level()
                except IndexError:
                    self._finish_off()
                else:
                    self.level.reset()
                    self.save_game()
            else:
                self.level.reset()
                self.save_game()

    def render(self, screen):
        if not self.level:
            screen.blit(self._end_text, self._end_text_rect)  # draw game over
        else:
            self.level.redraw(screen)

    def next_level(self):
        level_maps = self.level_maps.pop(0)
        self.level = Level(level_maps, is_final=not self.level_maps)

    def _handle_keypress(self, time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.level.player.move_left(time)
        if keys[pygame.K_RIGHT]:
            self.level.player.move_right(time)
        if keys[pygame.K_UP]:
            self.level.player.jump(time)
        if keys[pygame.K_z]:
            self.level.set_time_stop()

    @classmethod
    def to_internal_value(cls, data):
        data.pop("type")
        level_maps = data.pop("level_maps")
        level_data = data.pop("level")

        obj = cls(level_maps=level_maps)
        obj.level = Level.to_internal_value(level_data)

        return obj

    def to_representation(self):
        return {
            "type": "game",
            "level_maps": self.level_maps,
            "level": self.level.to_representation() if self.level else None,
        }

    def start_off(self):
        self.next_level()
        self.level.reset()

    def save_game(self):
        if self._save_game_thread and self._save_game_thread.is_alive():
            self._save_game_thread.join()
        if self._save_game_delay <= 0 and not self._is_saving_game:
            self._is_saving_game = True
            data = self.json()
            file = self.get_saved_game_file()
            self._save_game_thread = threading.Thread(target=self._save_game_data, args=(data, file))
            self._save_game_thread.start()

    def _save_game_data(self, data, file):
        with threading.Lock():
            with file.open(mode="w") as f:
                f.write(data)
            self._is_saving_game = False
            self._save_game_delay = self.SAVE_GAME_DELAY

    def _finish_off(self):
        self.level = None
        saved_game_file = self.get_saved_game_file()
        if saved_game_file.exists():
            saved_game_file.unlink()  # delete the save
        effects.play_soundtrack(name="ending")

    @staticmethod
    def get_saved_game_file():
        return VAR_DIR / "saved_game.json"

    @classmethod
    def load_game(cls):
        file = cls.get_saved_game_file()
        if not file.exists():
            obj = cls()
            obj.start_off()
        else:
            with file.open(mode="r") as f:
                game_data = json.load(f)
            obj = cls.to_internal_value(game_data)
        return obj
