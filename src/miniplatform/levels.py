import itertools
import json
import logging
import math
import operator

import pygame

from miniplatform import effects
from miniplatform.configs import config, STATIC_DIR, adjust_color
from miniplatform.entities import Block, Lava, Coin, Player
from miniplatform.serializers import Serializable
from miniplatform.utils import TimeFactor


class Level(Serializable):
    TIME_STOP = 5_000
    TIME_FREEZE = 1_000
    TIME_STOP_IDLE = TIME_STOP + TIME_FREEZE
    TIME_ACCELERATION_SCALE = 50

    BAR_WIDTH = 100

    WARNING_TIME = 30_000

    def __init__(self, level_map, number, is_final=False, time_to_reset_factor=None):
        self.player = None
        self.lavas = ()
        self.coins = ()
        self.blocks = ()
        self.level_map = level_map
        self.number = number
        self.is_final = is_final

        self._time_stop_left = TimeFactor()
        self._time_stop_freeze = TimeFactor()
        self._time_stop_idle = TimeFactor()
        self._time_stop_factors = {
            self._time_stop_left: self.TIME_STOP,
            self._time_stop_freeze: self.TIME_FREEZE,
            self._time_stop_idle: self.TIME_STOP_IDLE,
        }

        w_width, w_height = pygame.display.get_window_size()

        self._time_reset_factor = TimeFactor()
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

        self._game_time_to_reset_factor = time_to_reset_factor

        self.info_font = pygame.font.Font(None, 24)
        self.coins_surface = None
        self.refresh_coins_text()

    def reset(self):
        self.player = None

        for factor in self._time_stop_factors:
            factor.set(0)
        self._time_reset_factor.set(0)

        lavas = []
        coins = []
        blocks = []

        for i, line in enumerate(self.level_map):
            for j, el in enumerate(line):
                location = pygame.Vector2(j * Block.SIZE, i * Block.SIZE)
                if el in ("+", "v", "|", "="):
                    direction = pygame.Vector2(el == "=", el in ("v", "|"))
                    lava = Lava(location, direction, is_repeatable=el == "v")
                    lavas.append(lava)
                elif el == "o":
                    coin = Coin(location)
                    coins.append(coin)
                elif el == "@":
                    self.player = Player(location)
                    w_width, w_height = pygame.display.get_window_size()
                    config.offset_x = self.player.rect.x - w_width // 2
                    config.offset_y = self.player.rect.y - w_height // 2
                elif el == "#":
                    block = Block(location)
                    blocks.append(block)

        self.lavas = tuple(lavas)
        self.coins = tuple(coins)
        self.blocks = tuple(blocks)

        self.time_stop_bar.width = self.BAR_WIDTH
        self.refresh_coins_text()

    @property
    def entities(self):
        return itertools.chain(
            self.blocks,
            self.free_coins,
            self.lavas,
        )

    @property
    def free_coins(self):
        return filter(operator.attrgetter("is_free"), self.coins)

    @property
    def coins_number(self):
        return len(self.coins)

    @property
    def collected_coins_number(self):
        return self.coins_number - sum(map(bool, self.free_coins))

    @property
    def has_free_coins(self):
        return any(self.free_coins)

    def update(self, time):
        self.player.update(time, level=self)

        w_width, w_height = pygame.display.get_window_size()
        config.offset_x = self.player.rect.x - w_width // 2
        config.offset_y = self.player.rect.y - w_height // 2

        for entity in self.entities:
            entity.update(time, level=self)

        if not self.has_free_coins:
            self.player.set_won(level=self)
        elif self.player.is_alive:
            self._handle_time_stop(time)

    def redraw(self, screen):
        self.player.render(screen)
        for entity in self.entities:
            entity.render(screen)
        if self._time_reset_factor:
            alpha = int(self._time_reset_factor.value * 255)
            self._time_reset_screen.set_alpha(alpha)
            screen.blit(self._time_reset_screen, (0, 0))
        self._draw_infographics(screen)

    @property
    def is_running(self):
        return not (self.player.is_dead or self.player.is_winner)

    @property
    def is_complete(self):
        return self.player.is_winner

    @property
    def is_time_stopped(self):
        return any([self._time_stop_left, self._time_stop_freeze])

    @property
    def speed_factor(self):
        if self._time_stop_left:
            return 0

        if self._time_stop_freeze:
            return (self.TIME_FREEZE - self._time_stop_freeze.value) / self.TIME_FREEZE

        if self._time_reset_factor:
            return self.time_acceleration

        return 1

    @property
    def color_factor(self):
        if self._time_stop_left:
            return 0
        if self._time_stop_freeze:
            return 1 - (self._time_stop_freeze.value / self.TIME_FREEZE)
        return 1

    @property
    def time_acceleration(self):
        if not self._time_reset_factor:
            return 1

        t = self._time_reset_factor.value
        return 1 + self.TIME_ACCELERATION_SCALE * ((1 / (1 + math.exp(-t))) - 0.5)

    @time_acceleration.setter
    def time_acceleration(self, value):
        self._time_reset_factor.set(value)

    def set_time_stop(self):
        if not (self._time_stop_left or self._time_stop_idle):
            logging.info("Stopping time ...")
            for factor, value in self._time_stop_factors.items():
                factor.set(value)
            if self._time_reset_factor:
                effects.Sound.WORLD_RESET.pause()
            effects.Sound.TIME_STOP.play()

    def _handle_time_stop(self, time):
        is_frozen_before = bool(self._time_stop_freeze)
        for factor in self._time_stop_factors:
            if factor:
                factor -= time * self.time_acceleration  # decreasing one by one, not all at once
                break
        if self._time_stop_left or self._time_stop_freeze:
            charge = sum([factor.value for factor in (self._time_stop_left, self._time_stop_freeze)])
            total_charge = sum((self.TIME_STOP, self.TIME_FREEZE))
            self.time_stop_bar.width = int(self.BAR_WIDTH * (charge / total_charge))
        elif self._time_stop_idle:
            scale = (self.TIME_STOP_IDLE - self._time_stop_idle.value) / self.TIME_STOP_IDLE
            self.time_stop_bar.width = int(self.BAR_WIDTH * scale)
        config.color_factor = self.color_factor
        if not self._time_stop_freeze and is_frozen_before:
            effects.Sound.TIME_STOP.stop()
            effects.Sound.WORLD_RESET.unpause()

    def _draw_infographics(self, screen):
        pygame.draw.rect(screen, "gray", self.time_stop_back_bar)
        if self._time_stop_left or self._time_stop_freeze:
            time_left_text_color = adjust_color((0, 255, 0))
        elif self._time_stop_idle:
            time_left_text_color = (0, 125, 0)
        else:
            time_left_text_color = (0, 255, 0)
        pygame.draw.rect(screen, time_left_text_color, self.time_stop_bar)

        coins_text_margin = 10
        coins_text_pos = (self.time_stop_back_bar.left, self.time_stop_back_bar.bottom + coins_text_margin)
        screen.blit(self.coins_surface, coins_text_pos)

        if self._game_time_to_reset_factor is not None:
            time_left = self._game_time_to_reset_factor.value
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

    @property
    def coins_text(self):
        return f"coins: {self.collected_coins_number} / {self.coins_number}"

    def refresh_coins_text(self):
        coins_text = f"Coins: {self.collected_coins_number} / {self.coins_number}"
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
        lavas_data = data.pop("lavas")
        coins_data = data.pop("coins")
        blocks_data = data.pop("blocks")

        level_map = data.pop("level_map")
        number = data.pop("number")
        is_final = data.pop("is_final")

        time_stop_left = data.pop("_time_stop_left")
        time_stop_freeze = data.pop("_time_stop_freeze")
        time_stop_idle = data.pop("_time_stop_idle")

        obj = cls(level_map, number, is_final=is_final)

        obj.player = Player.to_internal_value(player_data) if player_data else None
        obj.lavas = tuple([Lava.to_internal_value(data) for data in lavas_data])
        obj.coins = tuple([Coin.to_internal_value(data) for data in coins_data])
        obj.blocks = tuple([Block.to_internal_value(data) for data in blocks_data])

        obj._time_stop_left.set(time_stop_left)
        obj._time_stop_freeze.set(time_stop_freeze)
        obj._time_stop_idle.set(time_stop_idle)

        obj.refresh_coins_text()

        return obj

    def to_representation(self):
        return {
            "type": "level",
            "player": self.player.to_representation() if self.player else None,
            "lavas": [lava.to_representation() for lava in self.lavas],
            "coins": [coin.to_representation() for coin in self.coins],
            "blocks": [block.to_representation() for block in self.blocks],
            "level_map": self.level_map,
            "number": self.number,
            "is_final": self.is_final,
            "_time_stop_left": self._time_stop_left.value,
            "_time_stop_freeze": self._time_stop_freeze.value,
            "_time_stop_idle": self._time_stop_idle.value,
        }
