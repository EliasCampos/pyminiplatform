import threading
import json

import pygame

from miniplatform import effects
from miniplatform.configs import VAR_DIR
from miniplatform.exceptions import FinishedGameException
from miniplatform.levels import Level
from miniplatform.serializers import Serializable
from miniplatform.utils import TimeFactor


class Game(Serializable):
    SAVE_GAME_DELAY = 1_000  # every second
    GAME_RESET_DELAY = 10_000

    INITIAL_TIME = 90_000
    LEVEL_BONUS_TIME = 60_000

    def __init__(self, level_maps=None, initial_time=None):
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

        self._time_to_reset_factor = TimeFactor(
            value=(initial_time if initial_time is not None else self.INITIAL_TIME)
        )

        self._is_game_reset = False
        self._game_reset_time = 0

    def update_state(self, time):
        if not self.level:
            return

        if self._save_game_delay > 0:
            self._save_game_delay = self._save_game_delay - time
        else:
            self.save_game()

        self._handle_keypress(time)
        self.level.update(time)

        if self._time_to_reset_factor:
            if self.level.has_free_coins and not self.level.is_time_stopped:
                self._time_to_reset_factor -= time
        else:
            if self._is_game_reset and not self.level.is_time_stopped:
                self._game_reset_time += time
                self.level.time_acceleration = self._game_reset_time / self.GAME_RESET_DELAY
                if self._game_reset_time >= self.GAME_RESET_DELAY:
                    self.reset_game()
            else:
                self._set_off_game_reset()

        if not self.level.is_running:
            if self.level.is_complete:
                try:
                    self.next_level()
                except FinishedGameException:
                    self._finish_off()
                else:
                    self.reset_level()
            else:
                self.reset_level()

    def render(self, screen):
        if not self.level:
            screen.blit(self._end_text, self._end_text_rect)  # draw game over
        else:
            self.level.redraw(screen)

    def next_level(self):
        level_number = self.level.number + 1 if self.level else 0
        try:
            level_map = self.level_maps[level_number]
        except IndexError:
            raise FinishedGameException(f"All {level_number} levels complete")
        else:
            self.level = Level(
                level_map,
                number=level_number,
                is_final=level_number == len(self.level_maps) - 1,
                time_to_reset_factor=self._time_to_reset_factor,
            )
            if not self._is_game_reset:
                self._time_to_reset_factor += level_number * self.LEVEL_BONUS_TIME

    def reset_game(self):
        self._is_game_reset = False
        self._game_reset_time = 0
        self.level = None
        self._time_to_reset_factor.set(self.INITIAL_TIME)
        self.next_level()
        self.reset_level()

        effects.Sound.WORLD_RESET.sound_channel.stop()
        effects.play_soundtrack()

    def reset_level(self):
        self.level.reset()
        self.save_game()

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
        time_to_reset = data.pop("_time_to_reset_factor")

        obj = cls(level_maps=level_maps, initial_time=time_to_reset)
        obj.level = Level.to_internal_value(level_data)
        obj.level._game_time_to_reset_factor = obj._time_to_reset_factor

        return obj

    def to_representation(self):
        return {
            "type": "game",
            "level_maps": self.level_maps,
            "level": self.level.to_representation() if self.level else None,
            "_time_to_reset_factor": self._time_to_reset_factor.value,
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

    def _set_off_game_reset(self):
        if not self._is_game_reset and not (self.level and self.level.is_time_stopped):
            self._is_game_reset = True
            effects.Sound.WORLD_RESET.play()
            fadeout_time = int(self.GAME_RESET_DELAY * 0.5)
            pygame.mixer_music.fadeout(fadeout_time)

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
