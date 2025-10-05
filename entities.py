import abc
import copy
import functools
import math
import random

import pygame

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

    def set_offset(self):
        self.sprite.center = self.rect.center

        self.sprite.left -= config.offset_x
        self.sprite.top -= config.offset_y


class Player(Entity):
    WIDTH = 16
    HEIGHT = 30

    def __init__(self, location):
        self.location = location
        self.dx = 0
        self.dy = 0
        self.is_on_ground = False

        self._gravity = 0.0005
        self._player_step = 0.01
        self._is_won = False
        self._is_dead = False

        self._finalization_time = 3000

    def update(self, time, level):
        if not self.is_on_ground:
            self.dy += self._gravity * time
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
            self._finalization_time -= time
        self.dx = 0

        self.set_offset()

    def get_rect(self):
        return pygame.Rect(
            self.location.x,
            self.location.y,
            self.WIDTH,
            self.HEIGHT,
        )

    def render(self, screen):
        if self._is_dead:
            color = (255, 0, 0)
        elif self._is_won:
            color = (255, 255, 0)
        else:
            color = (50, 200, 100)
        pygame.draw.rect(screen, color, self.sprite)

    def move_left(self, time):
        self.dx = -self._player_step * time

    def move_right(self, time):
        self.dx = self._player_step * time

    def jump(self, time):
        if self.is_on_ground:
            self.dy -= self._player_step * 2 * time
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
            if self.dy < 0:
                self.rect.top = block.rect.bottom
            self.dy = 0


class Lava(Entity):
    SCALE = 0.9

    def __init__(self, location, direction, is_repeatable):
        self.speed = 0.1
        self.location = location + pygame.Vector2(*([Block.SIZE * (1 - self.SCALE) * 0.5] * 2))
        self.direction = direction
        self.is_repeatable = is_repeatable
        self.size = Block.SIZE * self.SCALE
        self.color = (255, 100, 100)
        self.is_on_ground = False

        self._gravity = 0.0005
        self._player_step = 0.1
        self._is_won = False
        self._is_dead = False

    def update(self, time, level):
        step = self.speed * level.speed_factor * time
        self.rect.move_ip(
            self.direction.x * step,
            self.direction.y * step,
        )
        self._handle_collision(level)

        self.set_offset()

    def get_rect(self):
        return pygame.Rect(
            self.location.x,
            self.location.y,
            self.size,
            self.size,
        )

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.sprite)

    def _handle_collision(self, level):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, Block):
                    if self.is_repeatable:
                        self.rect.left = self.location.x
                        self.rect.top = self.location.y
                    else:
                        self.speed *= -1


class Coin(Entity):

    def __init__(self, location):
        self._wobble_distance = 5
        self._wobble_speed = 0.005
        self._t = math.pi * random.uniform(-1, 1) / self._wobble_speed

        self.location = location
        self.wobble = 0
        self.is_hit = False
        self.is_free = True

    def update(self, time, level):
        self._t += time
        current_wobble_speed = self._wobble_speed * level.speed_factor
        self.wobble = self._wobble_distance * math.sin(current_wobble_speed * self._t)
        self.rect.top = self.location.y + self.wobble
        self._handle_collision(level)
        self.set_offset()

    def get_rect(self):
        return pygame.Rect(
            self.location.x,
            self.location.y,
            Block.SIZE,
            Block.SIZE,
        )

    def render(self, screen):
        color = (255, 215, 0)
        radius = Block.SIZE // 3
        pygame.draw.circle(
            screen,
            color,
            self.sprite.center,
            radius,
        )

    def _handle_collision(self, level):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, (Block, Lava)):
                    if self.wobble > 0:
                        self.rect.bottom = entity.rect.top
                    elif self.wobble < 0:
                        self.rect.top = entity.rect.bottom

    def set_taken(self):
        self.is_free = False
        Sound.COIN.play()


class Block(Entity):
    SIZE = 20

    def __init__(self, location):
        self.start_location = location
        self.location = copy.copy(location)
        self.color = (60, 60, 60)

    def get_rect(self):
        return pygame.Rect(
            self.location.x,
            self.location.y,
            self.SIZE,
            self.SIZE,
        )

    def update(self, time, level):
        self.set_offset()

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.sprite)
