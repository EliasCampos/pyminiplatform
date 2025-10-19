import abc
import functools
import logging
import math
import random

import pygame

from miniplatform.configs import config, adjust_color
from miniplatform.effects import Sound
from miniplatform.serializers import Serializable


class Entity(Serializable):

    def __init__(self, location):
        self.location = location

    def update(self, time, level):
        self.update_state(time, level)

    @abc.abstractmethod
    def update_state(self, time, level):
        ...

    def render(self, screen):
        self.sprite.center = self.rect.center

        self.sprite.left -= config.offset_x
        self.sprite.top -= config.offset_y

        self.render_entity(screen)

    @abc.abstractmethod
    def render_entity(self, screen):
        ...

    @abc.abstractmethod
    def get_rect(self):
        ...

    @functools.cached_property
    def rect(self):
        return self.get_rect()

    @functools.cached_property
    def sprite(self):
        return self.get_rect()

    def collides(self, entity):
        return self.rect.colliderect(entity.rect)


class Player(Entity):
    WIDTH = 16
    HEIGHT = 30
    PLAYER_STEP = 0.01

    def __init__(self, location):
        super().__init__(location)
        self.dx = 0
        self.dy = 0
        self.is_on_ground = False

        self._is_won = False
        self._is_dead = False
        self._finalization_time = 3000

    def update_state(self, time, level):
        if not self.is_on_ground:
            gravity = 0.0005
            self.dy += gravity * time
        self.is_on_ground = False
        self.rect.move_ip(
            0,
            self.dy * time,
        )
        self._handle_collision(level, is_vertical=True)
        self.rect.move_ip(
            self.dx * time,
            0,
        )
        self._handle_collision(level, is_vertical=False)
        if self._is_dead or self._is_won:
            self._finalization_time -= time * level.time_acceleration
        self.dx = 0

    def get_rect(self):
        return pygame.Rect(
            self.location.x,
            self.location.y,
            self.WIDTH,
            self.HEIGHT,
        )

    def render_entity(self, screen):
        if self._is_dead:
            color = (255, 0, 0)
        elif self._is_won:
            color = (255, 255, 0)
        else:
            color = (50, 200, 100)
        pygame.draw.rect(screen, adjust_color(color), self.sprite)

    def move_left(self, time):
        self.dx = -self.PLAYER_STEP * time

    def move_right(self, time):
        self.dx = self.PLAYER_STEP * time

    def jump(self, time):
        if self.is_on_ground:
            self.dy -= self.PLAYER_STEP * 2 * time
            Sound.JUMP.play()

    def set_position(self, position):
        self.location = position

    @property
    def is_alive(self):
        return not self._is_dead

    @property
    def is_dead(self):
        return not self._is_won and self._is_dead and self._finalization_time <= 0

    def set_dead(self):
        if not (self._is_won or self._is_dead):
            logging.info("Player has died.")
            self._is_dead = True
            Sound.FAIL.play()
            config.color_factor = 1

    @property
    def is_winner(self):
        return not self._is_dead and self._is_won and self._finalization_time <= 0

    def set_won(self, level):
        if not (self._is_won or self._is_dead):
            logging.info("Winning level %s ...", level.number)
            self._is_won = True
            Sound.VICTORY.play()
            if level.is_final:
                pygame.mixer.music.fadeout(self._finalization_time)
            config.color_factor = 1

    def _handle_collision(self, level, is_vertical):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, Block):
                    self._handle_wall_collision(entity, is_vertical)
                elif isinstance(entity, Lava):
                    self.set_dead()
                elif isinstance(entity, Coin):
                    entity.set_taken(level)

    def _handle_wall_collision(self, block, is_vertical):
        if self.dx != 0 and not is_vertical:
            if self.dx > 0:
                self.rect.right = block.rect.left
            elif self.dx < 0:
                self.rect.left = block.rect.right
            self.dx = 0
        if self.dy != 0 and is_vertical:
            if self.dy > 0:
                self.rect.bottom = block.rect.top
                self.is_on_ground = True
            elif self.dy < 0:
                self.rect.top = block.rect.bottom
            self.dy = 0

    @classmethod
    def to_internal_value(cls, data):
        data.pop("type")
        location = pygame.Vector2(data.pop("location"))
        obj = cls(location=location)
        for key, value in data.items():
            setattr(obj, key, value)
        return obj

    def to_representation(self):
        return {
            "type": "player",
            "location": [self.rect.x, self.rect.y],
            "dx": self.dx,
            "dy": self.dy,
            "is_on_ground": self.is_on_ground,
            "_is_won": self._is_won,
            "_is_dead": self._is_dead,
            "_finalization_time": self._finalization_time,
        }


class Lava(Entity):
    SCALE = 0.9

    def __init__(self, location, direction, is_repeatable, init_location=None):
        super().__init__(location=location + self.margin)
        self.init_location = init_location or location
        self.direction = direction
        self.is_repeatable = is_repeatable

    def update_state(self, time, level):
        speed = 0.1
        step = speed * level.speed_factor * time
        self.rect.move_ip(self.direction.x * step, self.direction.y * step)
        self._handle_collision(level)

    def get_rect(self):
        size = Block.SIZE * self.SCALE
        return pygame.Rect(self.location.x, self.location.y, size, size)

    def render_entity(self, screen):
        color = (255, 100, 100)
        pygame.draw.rect(screen, adjust_color(color), self.sprite)

    def _handle_collision(self, level):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, Block):
                    if self.is_repeatable:
                        self.rect.left = self.init_location.x
                        self.rect.top = self.init_location.y
                    else:
                        if self.direction.x > 0:
                            self.rect.right = entity.rect.left
                        elif self.direction.x < 0:
                            self.rect.left = entity.rect.right
                        if self.direction.y > 0:
                            self.rect.bottom = entity.rect.top
                        elif self.direction.y < 0:
                            self.rect.top = entity.rect.bottom
                        self.direction.rotate_ip(180)

    @property
    def margin(self):
        margin = Block.SIZE * (1 - self.SCALE) * 0.5
        return pygame.Vector2(margin, margin)

    @classmethod
    def to_internal_value(cls, data):
        data.pop("type")
        location = pygame.Vector2(data.pop("location"))
        init_location = pygame.Vector2(data.pop("init_location"))
        direction = pygame.Vector2(data.pop("direction"))
        is_repeatable = data.pop("is_repeatable")
        obj = cls(location=location, direction=direction, is_repeatable=is_repeatable, init_location=init_location)
        return obj

    def to_representation(self):
        location = pygame.Vector2(self.rect.x, self.rect.y) - self.margin
        return {
            "type": "lava",
            "location": [location.x, location.y],
            "init_location": [self.init_location.x, self.init_location.y],
            "direction": [self.direction.x, self.direction.y],
            "is_repeatable": self.is_repeatable,
        }


class Coin(Entity):
    WOBBLE_SPEED = 6
    WOBBLE_DIST = 2

    def __init__(self, location, init_location=None, timeline=None):
        super().__init__(location)
        self.init_location = init_location or location.copy()
        self.timeline = timeline if timeline is not None else 2 * math.pi * random.random()
        self.is_free = True

    def update_state(self, time, level):
        self.timeline += time * 1e-3 * self.WOBBLE_SPEED * level.speed_factor
        wobble = self.WOBBLE_DIST * level.speed_factor * math.sin(self.timeline)
        self.rect.move_ip(0, wobble)
        self._handle_collision(level)

    def get_rect(self):
        return pygame.Rect(
            self.location.x,
            self.location.y,
            Block.SIZE,
            Block.SIZE,
        )

    def render_entity(self, screen):
        color = (255, 215, 0)
        radius = Block.SIZE // 3
        pygame.draw.circle(
            screen,
            adjust_color(color),
            self.sprite.center,
            radius,
        )

    def _handle_collision(self, level):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, Block):
                    if self.rect.y > 0:
                        self.rect.bottom = entity.rect.top
                    elif self.rect.y < 0:
                        self.rect.top = entity.rect.bottom

    def set_taken(self, level):
        self.is_free = False
        level.refresh_coins_text()
        Sound.COIN.play()

    @classmethod
    def to_internal_value(cls, data):
        data.pop("type")
        location = pygame.Vector2(data.pop("location"))
        init_location = pygame.Vector2(data.pop("init_location"))
        timeline = data.pop("timeline")
        obj = cls(location=location, init_location=init_location, timeline=timeline)
        for key, value in data.items():
            setattr(obj, key, value)
        return obj

    def to_representation(self):
        return {
            "type": "coin",
            "location": [self.rect.x, self.rect.y],
            "init_location": [self.init_location.x, self.init_location.y],
            "timeline": self.timeline,
            "is_free": self.is_free,
        }


class Block(Entity):
    SIZE = 20

    def get_rect(self):
        return pygame.Rect(self.location.x, self.location.y, self.SIZE, self.SIZE)

    def update_state(self, time, level):
        pass

    def render_entity(self, screen):
        color = (60, 60, 60)
        pygame.draw.rect(screen, color, self.sprite)

    @classmethod
    def to_internal_value(cls, data):
        data.pop("type")
        location = pygame.Vector2(data.pop("location"))
        obj = cls(location=location)
        return obj

    def to_representation(self):
        return {
            "type": "block",
            "location": [self.rect.x, self.rect.y],
        }
