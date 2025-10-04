import abc
import copy
import math
import random

import pygame

from common import Vector
from configs import config
from effects import Sound


class Entity(abc.ABC):

    @abc.abstractmethod
    def update(self, time, level):
        ...

    @abc.abstractmethod
    def render(self, screen):
        ...

    @abc.abstractmethod
    def get_rect(self, offset):
        ...

    @property
    def rect(self):
        return self.get_rect(offset=Vector(0, 0))

    def collides(self, entity):
        return self.rect.colliderect(entity.rect)


class Player(Entity):
    WIDTH = 16
    HEIGHT = 30

    def __init__(self, location):
        self.location = location
        self.speed = Vector(0, 0)
        self.color = (50, 200, 100)
        self.is_on_ground = False

        self._gravity = 0.0005
        self._player_step = 0.01
        self._is_won = False
        self._is_dead = False

        self._finalization_time = 3000

    def update(self, time, level):
        if not self.is_on_ground:
            self.speed.y += self._gravity * time
        self.location.y += self.speed.y * time
        self.is_on_ground = False
        self._handle_collision(level, is_vertical=True)
        self.location.x += self.speed.x * time
        self._handle_collision(level, is_vertical=False)
        if self._is_dead or self._is_won:
            self._finalization_time -= time
        self.speed.x = 0

    def get_rect(self, offset):
        return pygame.Rect(
            self.location.x - offset.x,
            self.location.y - offset.y,
            self.WIDTH,
            self.HEIGHT,
        )

    def render(self, screen):
        if self._is_dead:
            color = (255, 0, 0)
        elif self._is_won:
            color = (255, 255, 0)
        else:
            color = self.color
        pygame.draw.rect(screen, color, self.get_rect(offset=config.camera_offset))

    def move_left(self, time):
        self.speed.x = -self._player_step * time

    def move_right(self, time):
        self.speed.x = self._player_step * time

    def jump(self, time):
        if self.is_on_ground:
            self.speed.y -= self._player_step * 1.8 * time
            Sound.JUMP.play()

    def set_position(self, position):
        self.location = position

    @property
    def is_dead(self):
        return not self._is_won and self._is_dead and self._finalization_time <= 0

    def set_dead(self):
        if not (self._is_won or self._is_dead):
            self._is_dead = True
            Sound.FAIL.play()

    @property
    def is_winner(self):
        return not self._is_dead and self._is_won and self._finalization_time <= 0

    def set_won(self):
        if not (self._is_won or self._is_dead):
            self._is_won = True
            Sound.VICTORY.play()

    def _handle_collision(self, level, is_vertical):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, Block):
                    self._handle_wall_collision(entity, is_vertical)
                elif isinstance(entity, Lava):
                    self.set_dead()
                elif isinstance(entity, Coin):
                    entity.set_taken()

    def _handle_wall_collision(self, block, is_vertical):
        if self.speed.x != 0 and not is_vertical:
            if self.speed.x > 0:
                self.location.x = block.rect.left - self.WIDTH
            elif self.speed.x < 0:
                self.location.x = block.rect.right
            self.speed.x = 0
        if self.speed.y != 0 and is_vertical:
            if self.speed.y > 0:
                self.location.y = block.rect.y - self.HEIGHT
                self.is_on_ground = True
            if self.speed.y < 0:
                self.location.y = block.rect.bottom
            self.speed.y = 0


class Lava(Entity):
    SPEED = 0.05
    SCALE = 0.95

    def __init__(self, location, direction, is_repeatable):
        self.start_location = location + Vector(*([Block.SIZE * (1 - self.SCALE)] * 2))
        self.speed = direction * self.SPEED
        self.location = copy.copy(self.start_location)
        self.direction = direction
        self.is_repeatable = is_repeatable
        self.sizes = Vector(*([Block.SIZE * self.SCALE] * 2))
        self.color = (255, 100, 100)
        self.is_on_ground = False

        self._gravity = 0.0005
        self._player_step = 0.1
        self._is_won = False
        self._is_dead = False

    def update(self, time, level):
        speed = self.speed * level.speed_factor
        self.location += speed * time
        self._handle_collision(level)

    def get_rect(self, offset):
        return pygame.Rect(
            self.location.x - offset.x,
            self.location.y - offset.y,
            self.sizes.x,
            self.sizes.y,
        )

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.get_rect(offset=config.camera_offset))

    def _handle_collision(self, level):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, Block):
                    if self.is_repeatable:
                        self.location = copy.copy(self.start_location)
                    else:
                        self.speed *= -1


class Coin(Entity):

    def __init__(self, location):
        self.start_location = location
        self.location = copy.copy(location)
        self.wobble = 2 * math.pi * random.uniform(-1, 1)
        self.wobble_pos = Vector(0, 0)
        self.is_hit = False
        self.is_free = True
        self.color = (255, 215, 0)
        self.radius = Block.SIZE // 3

        self._wobble_speed = 0.005
        self._wobble_distance = 5

    def update(self, time, level):
        current_wobble_speed = self._wobble_speed * level.speed_factor
        self.wobble += current_wobble_speed * time
        self._handle_collision(level)
        if not self.is_hit:
            self.location = self.start_location + Vector(
                0,
                self._wobble_distance * math.sin(self.wobble)
            )
        self.is_hit = False

    def get_rect(self, offset):
        return pygame.Rect(
            self.location.x - offset.x,
            self.location.y - offset.y,
            Block.SIZE,
            Block.SIZE,
        )

    def render(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (self.location.x - config.camera_offset.x, self.location.y - config.camera_offset.y),
            self.radius,
        )

    def _handle_collision(self, level):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, (Block, Lava)):
                    self.is_hit = True

    def set_taken(self):
        self.is_free = False
        Sound.COIN.play()


class Block(Entity):
    SIZE = 20

    def __init__(self, location):
        self.start_location = location
        self.location = copy.copy(location)
        self.color = (60, 60, 60)

    def get_rect(self, offset):
        return pygame.Rect(
            self.location.x - offset.x,
            self.location.y - offset.y,
            self.SIZE,
            self.SIZE,
        )

    def update(self, time, level):
        pass

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.get_rect(offset=config.camera_offset))
