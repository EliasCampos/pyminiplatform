import pygame
import logging
import os

from miniplatform import configs, effects
from miniplatform.game import Game


def main():
    setup_logging()

    if not configs.VAR_DIR.exists():
        configs.VAR_DIR.mkdir()

    pygame.init()

    video_info = pygame.display.Info()
    screen = pygame.display.set_mode((video_info.current_w, video_info.current_h))
    pygame.display.set_caption("Mini platform")

    clock = pygame.time.Clock()

    logging.info("Starting game session")

    game_session = Game.load_game()
    effects.play_soundtrack()

    is_running = True
    while is_running:
        frame = clock.tick(configs.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                logging.info("Stopping game session (quit event)")

        game_session.update_state(frame)

        screen.fill((255, 255, 255))
        game_session.render(screen)

        pygame.display.flip()


def setup_logging():
    level_name = os.getenv("MINI_PLATFORM_LOG_LEVEL", logging.getLevelName(logging.INFO))
    level = logging.getLevelNamesMapping()[level_name]
    logging.basicConfig(level=level, format='[%(asctime)s][%(filename)s][%(levelname)s] %(message)s')
