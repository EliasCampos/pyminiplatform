import pygame

from miniplatform import configs
from miniplatform.game import Game


def main():
    pygame.init()

    video_info = pygame.display.Info()
    screen = pygame.display.set_mode((video_info.current_w, video_info.current_h))
    pygame.display.set_caption("Mini platform")

    clock = pygame.time.Clock()

    game = Game()
    is_running = True
    while is_running:
        frame = clock.tick(configs.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        game.update_state(frame)

        screen.fill((255, 255, 255))
        game.render(screen)

        pygame.display.flip()
