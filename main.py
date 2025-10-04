import pygame

import configs
from game import Game


def main():
    pygame.init()

    screen = pygame.display.set_mode((configs.WINDOW_WIDTH, configs.WINDOW_HEIGHT))
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


if __name__ == "__main__":
    main()
