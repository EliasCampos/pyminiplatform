import abc

import pygame


class InputHandler:

    def __init__(self, commands=None):
        commands = commands or ()
        self._commands_registry = {
            key: command for key, command in commands
        }

    def handle_input(self, time):
        keys = pygame.key.get_pressed()
        for key, command in self._commands_registry.items():
            if keys[key]:
                command.execute(time)


class Command(abc.ABC):

    @abc.abstractmethod
    def execute(self, time):
        ...


class _PlayerMixin:

    def __init__(self, player):
        self.player = player


class MoveLeftCommand(_PlayerMixin, Command):

    def execute(self, time):
        self.player.move_left(time)


class MoveRightCommand(_PlayerMixin, Command):

    def execute(self, time):
        self.player.move_right(time)


class JumpCommand(_PlayerMixin, Command):

    def execute(self, time):
        self.player.jump(time)


class TimeStopCommand(Command):

    def __init__(self, level):
        self.level = level

    def execute(self, time):
        self.level.set_time_stop()
