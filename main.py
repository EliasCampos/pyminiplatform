import pygame
import sys
import random

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
RED = (220, 20, 60)
GRAY = (169, 169, 169)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = 15
        self.gravity = 0.8
        self.on_ground = False
        
    def update(self, platforms, time_scale=1.0):
        keys = pygame.key.get_pressed()
        
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed * time_scale
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed * time_scale
            
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False
            
        self.vel_y += self.gravity * time_scale
        
        self.x += self.vel_x
        self.check_collision_x(platforms)
        
        self.y += self.vel_y
        self.check_collision_y(platforms)
        
        if self.y > WINDOW_HEIGHT:
            self.x = 100
            self.y = 100
            self.vel_y = 0
            
    def check_collision_x(self, platforms):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            if player_rect.colliderect(platform):
                if self.vel_x > 0:
                    self.x = platform.left - self.width
                elif self.vel_x < 0:
                    self.x = platform.right
                    
    def check_collision_y(self, platforms):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = False
        for platform in platforms:
            if player_rect.colliderect(platform):
                if self.vel_y > 0:
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.y = platform.bottom
                    self.vel_y = 0
                    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (int(self.x + self.width * 0.3), int(self.y + self.height * 0.25)), 4)
        pygame.draw.circle(screen, WHITE, (int(self.x + self.width * 0.7), int(self.y + self.height * 0.25)), 4)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False
        self.animation_offset = random.uniform(0, 360)
        
    def update(self, time):
        pass
        
    def draw(self, screen, time):
        if not self.collected:
            offset = pygame.math.Vector2(0, 3 * pygame.math.Vector2(0, 1).rotate(time * 100 + self.animation_offset).y)
            pygame.draw.circle(screen, YELLOW, (int(self.x + offset.x), int(self.y + offset.y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 150), (int(self.x + offset.x - 3), int(self.y + offset.y - 3)), 4)
            
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Miniplatform")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.player = Player(100, 100)
        
        self.platforms = [
            pygame.Rect(0, WINDOW_HEIGHT - 40, WINDOW_WIDTH, 40),
            pygame.Rect(150, 450, 150, 20),
            pygame.Rect(400, 380, 150, 20),
            pygame.Rect(600, 300, 150, 20),
            pygame.Rect(300, 250, 120, 20),
            pygame.Rect(100, 180, 100, 20),
            pygame.Rect(500, 150, 150, 20),
        ]
        
        self.coins = [
            Coin(225, 410),
            Coin(475, 340),
            Coin(675, 260),
            Coin(360, 210),
            Coin(150, 140),
            Coin(575, 110),
        ]
        
        self.score = 0
        self.game_time = 0
        self.time_multiplier = 1.0
        
        self.time_stop_active = False
        self.time_stop_duration = 5.0
        self.time_stop_timer = 0
        self.time_stop_cooldown = 10.0
        self.time_stop_cooldown_timer = 0
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.activate_time_stop()
                    
    def activate_time_stop(self):
        if not self.time_stop_active and self.time_stop_cooldown_timer <= 0:
            self.time_stop_active = True
            self.time_stop_timer = self.time_stop_duration
            self.time_stop_cooldown_timer = self.time_stop_cooldown
            
    def update(self, dt):
        if self.time_stop_active:
            self.time_stop_timer -= dt
            if self.time_stop_timer <= 0:
                self.time_stop_active = False
                self.time_stop_timer = 0
            
            self.player.update(self.platforms, time_scale=1.0)
        else:
            adjusted_dt = dt * self.time_multiplier
            self.game_time += adjusted_dt
            self.player.update(self.platforms, time_scale=self.time_multiplier)
            
            player_rect = self.player.get_rect()
            for coin in self.coins:
                if not coin.collected and player_rect.colliderect(coin.get_rect()):
                    coin.collected = True
                    self.score += 10
                    self.time_multiplier += 0.1
                    
        if self.time_stop_cooldown_timer > 0:
            self.time_stop_cooldown_timer -= dt
            
    def draw(self):
        self.screen.fill((135, 206, 235))
        
        for platform in self.platforms:
            pygame.draw.rect(self.screen, GREEN, platform)
            pygame.draw.rect(self.screen, (20, 100, 20), platform, 2)
            
        for coin in self.coins:
            coin.draw(self.screen, self.game_time)
            
        self.player.draw(self.screen)
        
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        time_text = self.font.render(f"Time: {self.game_time:.1f}s", True, BLACK)
        self.screen.blit(time_text, (10, 50))
        
        speed_text = self.small_font.render(f"Speed: {self.time_multiplier:.1f}x", True, BLACK)
        self.screen.blit(speed_text, (10, 90))
        
        if self.time_stop_active:
            stop_text = self.font.render("TIME STOPPED!", True, RED)
            text_rect = stop_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
            self.screen.blit(stop_text, text_rect)
            
            timer_text = self.small_font.render(f"{self.time_stop_timer:.1f}s", True, RED)
            timer_rect = timer_text.get_rect(center=(WINDOW_WIDTH // 2, 60))
            self.screen.blit(timer_text, timer_rect)
        elif self.time_stop_cooldown_timer > 0:
            cooldown_text = self.small_font.render(f"Time Stop: {self.time_stop_cooldown_timer:.1f}s", True, GRAY)
            self.screen.blit(cooldown_text, (WINDOW_WIDTH - 200, 10))
        else:
            ready_text = self.small_font.render("Time Stop: Ready (Z)", True, GREEN)
            self.screen.blit(ready_text, (WINDOW_WIDTH - 220, 10))
            
        controls_text = self.small_font.render("WASD/Arrows: Move | Space: Jump | Z: Time Stop", True, BLACK)
        self.screen.blit(controls_text, (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT - 25))
        
        pygame.display.flip()
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
