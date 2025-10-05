import abc
import functools
import math
import random

import pygame

from configs import config, adjust_color
from effects import Sound


class Entity(abc.ABC):

    def __init__(self, location):
        self.location = location

    def update(self, time, level):
        self.update_state(time, level)
        self.alight_sprite()

    @abc.abstractmethod
    def update_state(self, time, level):
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

    def alight_sprite(self):
        self.sprite.center = self.rect.center

        self.sprite.left -= config.offset_x
        self.sprite.top -= config.offset_y


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
            self._finalization_time -= time
        self.dx = 0

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
        margin = Block.SIZE * (1 - self.SCALE) * 0.5
        super().__init__(
            location=location + pygame.Vector2(margin, margin)
        )
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

    def render(self, screen):
        color = (255, 100, 100)
        pygame.draw.rect(screen, adjust_color(color), self.sprite)

    def _handle_collision(self, level):
        for entity in level.entities:
            if self.collides(entity):
                if isinstance(entity, Block):
                    if self.is_repeatable:
                        self.rect.left = self.location.x
                        self.rect.top = self.location.y
                    else:
                        self.direction.rotate_ip(180)


class Coin(Entity):
    FREQ = 0.01

    def __init__(self, location):
        super().__init__(location)
        self.timeline = math.pi * random.uniform(-1, 1) / self.FREQ
        self.wobble = 0
        self.is_hit = False
        self.is_free = True

    def update_state(self, time, level):
        self.timeline += time
        max_speed = 1.5
        self.wobble = max_speed * level.speed_factor * math.sin(self.FREQ * self.timeline)
        self.rect.move_ip(0, self.wobble)
        self._handle_collision(level)

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
            adjust_color(color),
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

    def get_rect(self):
        return pygame.Rect(self.location.x, self.location.y, self.SIZE, self.SIZE)

    def update_state(self, time, level):
        pass

    def render(self, screen):
        color = (60, 60, 60)
        pygame.draw.rect(screen, color, self.sprite)
