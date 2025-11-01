import json
import logging
import math

import pygame

from miniplatform import effects
from miniplatform.configs import config, STATIC_DIR, adjust_color
from miniplatform.entities import Block, Lava, Coin, Player, Monster
from miniplatform.serializers import Serializable


class Level(Serializable):
    TIME_STOP = 5_000
    TIME_FREEZE = 1_000
    TIME_STOP_IDLE = TIME_STOP + TIME_FREEZE
    TIME_ACCELERATION_SCALE = 50

    BAR_WIDTH = 100

    WARNING_TIME = 30_000

    def __init__(self, level_map, number, is_final=False, time_to_reset_factor=None):
        self.player = None
        self._entities = []
        self.level_map = level_map
        self.number = number
        self.is_final = is_final

        self._time_stop_left = 0
        self._time_stop_freeze = 0
        self._time_stop_idle = 0
        self._time_stop_factors = {
            '_time_stop_left': self.TIME_STOP,
            '_time_stop_freeze': self.TIME_FREEZE,
            '_time_stop_idle': self.TIME_STOP_IDLE,
        }

        w_width, w_height = pygame.display.get_window_size()

        # external factors:
        self.game_time_to_reset_factor = time_to_reset_factor
        self.game_time_reset_factor = 0

        self._time_reset_screen = pygame.Surface((w_width, w_height))
        self._time_reset_screen.fill((255, 255, 255))
        self._time_reset_screen.set_alpha(0)

        info_margin = 0.01
        bar_margin = 5
        bar_size = (self.BAR_WIDTH, 20)

        self.time_stop_back_bar = pygame.Rect(
            (w_width * info_margin, w_height * info_margin),
            tuple(size + bar_margin * 2 for size in bar_size),
        )
        self.time_stop_bar = pygame.Rect(
            (w_width * info_margin + bar_margin, w_height * info_margin + bar_margin),
            bar_size,
        )

        # pre-update state:
        self.active_entities = []
        self.coins = []
        self.free_coins = []
        self.monsters = []
        self.alive_monsters = []

        # post-update state:
        self.is_running = True
        self.is_complete = False
        self.is_time_stopped = False

        self.speed_factor = 1
        self.time_acceleration = 1

        self.has_win_condition = False

        self.info_font = pygame.font.Font(None, 24)
        self.coins_surface = None
        self.refresh_stats_text()

    def reset(self):
        self.player = None

        for factor in self._time_stop_factors:
            setattr(self, factor, 0)
        self.game_time_reset_factor = 0

        self._entities.clear()

        for i, line in enumerate(self.level_map):
            for j, el in enumerate(line):
                location = pygame.Vector2(j * Block.SIZE, i * Block.SIZE)
                if el in ("+", "v", "|", "="):
                    direction = pygame.Vector2(el == "=", el in ("v", "|"))
                    lava = Lava(location, direction, is_repeatable=el == "v")
                    self._entities.append(lava)
                elif el == "o":
                    coin = Coin(location)
                    self._entities.append(coin)
                elif el == "@":
                    self.player = Player(location)
                    w_width, w_height = pygame.display.get_window_size()
                    config.offset_x = self.player.rect.x - w_width // 2
                    config.offset_y = self.player.rect.y - w_height // 2
                elif el == "#":
                    block = Block(location)
                    self._entities.append(block)
                elif el in ("m", "M"):
                    monster = Monster(location, is_auto_target=el == "M")
                    self._entities.append(monster)

        self._pre_update_setup()
        self._post_update_setup()

        self.time_stop_bar.width = self.BAR_WIDTH
        self.refresh_stats_text()

    def update(self, time):
        self._pre_update_setup()

        self.player.update(time, level=self)

        w_width, w_height = pygame.display.get_window_size()
        config.offset_x = self.player.rect.x - w_width // 2
        config.offset_y = self.player.rect.y - w_height // 2

        for entity in self.active_entities:
            entity.update(time, level=self)

        self.has_win_condition = not any(self.free_coins) and not any(self.alive_monsters)
        if self.has_win_condition:
            self.player.set_won(level=self)
        elif self.player.is_alive:
            self._handle_time_stop(time)

        self._post_update_setup()

    def redraw(self, screen):
        self.player.render(screen)
        for entity in self.active_entities:
            entity.render(screen)
        if self.game_time_reset_factor > 0:
            alpha = int(self.game_time_reset_factor * 255)
            self._time_reset_screen.set_alpha(alpha)
            screen.blit(self._time_reset_screen, (0, 0))
        self._draw_infographics(screen)

    def _pre_update_setup(self):
        for l in (
            self.active_entities,
            self.coins,
            self.free_coins,
            self.monsters,
            self.alive_monsters,
        ):
            l.clear()

        for entity in self._entities:
            if entity.is_active:
                self.active_entities.append(entity)

            if isinstance(entity, Coin):
                self.coins.append(entity)
                if entity.is_active:
                    self.free_coins.append(entity)
            elif isinstance(entity, Monster):
                self.monsters.append(entity)
                if entity.is_active:
                    self.alive_monsters.append(entity)

    def _post_update_setup(self):
        self.is_running = not (self.player.is_dead or self.player.is_winner)
        self.is_complete = self.player.is_winner
        self.is_time_stopped = any(value > 0 for value in (self._time_stop_left, self._time_stop_freeze))

        if self.game_time_reset_factor <= 0:
            time_acceleration = 1
        else:
            t = self.game_time_reset_factor
            time_acceleration = 1 + self.TIME_ACCELERATION_SCALE * ((1 / (1 + math.exp(-t))) - 0.5)
        self.time_acceleration = time_acceleration

        if self._time_stop_left > 0:
            speed_factor = 0
        elif self._time_stop_freeze > 0:
            speed_factor = (self.TIME_FREEZE - self._time_stop_freeze) / self.TIME_FREEZE
        elif self.game_time_reset_factor > 0:
            speed_factor = self.time_acceleration
        else:
            speed_factor = 1
        self.speed_factor = speed_factor

    def set_time_stop(self):
        if all(value <= 0 for value in (self._time_stop_left, self._time_stop_freeze, self._time_stop_idle)):
            logging.info("Stopping time ...")
            for factor, value in self._time_stop_factors.items():
                setattr(self, factor, value)
            if self.game_time_reset_factor > 0:
                effects.Sound.WORLD_RESET.pause()
            effects.Sound.TIME_STOP.play()

    def _handle_time_stop(self, time):
        is_frozen_before = self._time_stop_freeze > 0
        for factor in self._time_stop_factors:
            factor_value = getattr(self, factor)
            if factor_value > 0:
                factor_value -= time * self.time_acceleration  # decreasing one by one, not all at once
                setattr(self, factor, factor_value)
                break

        stop_factor_values = (self._time_stop_left, self._time_stop_freeze)
        if any(value > 0 for value in stop_factor_values):
            charge = sum(stop_factor_values)
            total_charge = sum((self.TIME_STOP, self.TIME_FREEZE))
            self.time_stop_bar.width = int(self.BAR_WIDTH * (charge / total_charge))
        elif self._time_stop_idle > 0:
            scale = (self.TIME_STOP_IDLE - self._time_stop_idle) / self.TIME_STOP_IDLE
            self.time_stop_bar.width = int(self.BAR_WIDTH * scale)

        if self._time_stop_left > 0:
            color_factor = 0
        elif self._time_stop_freeze > 0:
            color_factor =  1 - (self._time_stop_freeze / self.TIME_FREEZE)
        else:
            color_factor = 1
        config.color_factor = color_factor

        if self._time_stop_freeze <= 0 and is_frozen_before:
            effects.Sound.TIME_STOP.stop()
            effects.Sound.WORLD_RESET.unpause()

    def _draw_infographics(self, screen):
        pygame.draw.rect(screen, "gray", self.time_stop_back_bar)
        if any(value > 0 for value in (self._time_stop_left, self._time_stop_freeze)):
            time_left_text_color = adjust_color((0, 255, 0))
        elif self._time_stop_idle > 0:
            time_left_text_color = (0, 125, 0)
        else:
            time_left_text_color = (0, 255, 0)
        pygame.draw.rect(screen, time_left_text_color, self.time_stop_bar)

        coins_text_margin = 10
        coins_text_pos = (self.time_stop_back_bar.left, self.time_stop_back_bar.bottom + coins_text_margin)
        screen.blit(self.coins_surface, coins_text_pos)

        if self.game_time_to_reset_factor is not None:
            time_left = self.game_time_to_reset_factor
            if self.is_time_stopped:
                time_left_text = f"ZA WARUDO!"
                time_left_text_color = "goldenrod"
            elif time_left > 0:
                time_left_text = f"Time left: {time_left // 1000}"
                time_left_text_color = "black" if time_left >= self.WARNING_TIME else "red"
            else:
                time_left_text = "MADE IN HEAVEN!"
                time_left_text_color = "blueviolet"
            time_left_surface = self.info_font.render(
                time_left_text, True, time_left_text_color, "white"
            )
            _, coin_bar_shift = self.coins_surface.get_size()
            time_left_post = (
                self.time_stop_back_bar.left,
                self.time_stop_back_bar.bottom + coin_bar_shift + coins_text_margin,
            )
            screen.blit(time_left_surface, time_left_post)

    def refresh_stats_text(self):
        coins_number = len(self.coins)
        collected_coins_number = coins_number - len(self.free_coins)
        coins_text = f"Coins: {collected_coins_number} / {coins_number}"
        if any(self.monsters):
            monsters_number = len(self.monsters)
            defeated_monsters_number = monsters_number - len(self.alive_monsters)
            coins_text = f"{coins_text} | Monsters: {defeated_monsters_number} / {monsters_number}"
        self.coins_surface = self.info_font.render(
            coins_text, True, "black", "white"
        )

    @staticmethod
    def load_level_maps():
        levels_path = STATIC_DIR / "level_maps.json"
        with levels_path.open("r") as f:
            return json.load(f)

    @classmethod
    def to_internal_value(cls, data):
        data.pop("type")
        player_data = data.pop("player")
        entities_data = data.pop("_entities")

        level_map = data.pop("level_map")
        number = data.pop("number")
        is_final = data.pop("is_final")

        time_stop_left = data.pop("_time_stop_left")
        time_stop_freeze = data.pop("_time_stop_freeze")
        time_stop_idle = data.pop("_time_stop_idle")

        obj = cls(level_map, number, is_final=is_final)

        obj.player = Player.to_internal_value(player_data) if player_data else None
        entity_class_mapping = {
            "lava": Lava,
            "coin": Coin,
            "block": Block,
            "monster": Monster,
        }
        obj._entities = [
            (entity_class_mapping[data["type"]]).to_internal_value(data)
            for data in entities_data
        ]

        obj._time_stop_left = time_stop_left
        obj._time_stop_freeze = time_stop_freeze
        obj._time_stop_idle = time_stop_idle

        obj._pre_update_setup()
        obj._post_update_setup()

        obj.refresh_stats_text()

        return obj

    def to_representation(self):
        return {
            "type": "level",
            "player": self.player.to_representation() if self.player else None,
            "_entities": [entity.to_representation() for entity in self._entities],
            "level_map": self.level_map,
            "number": self.number,
            "is_final": self.is_final,
            "_time_stop_left": self._time_stop_left,
            "_time_stop_freeze": self._time_stop_freeze,
            "_time_stop_idle": self._time_stop_idle,
        }
