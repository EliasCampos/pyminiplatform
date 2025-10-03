import pygame
import sys
import math

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 20
FPS = 60

WHITE = (255, 255, 255)
WALL_COLOR = (60, 60, 60)
LAVA_COLOR = (255, 100, 100)
PLAYER_COLOR = (100, 100, 255)
COIN_COLOR = (255, 215, 0)

LEVEL_MAPS = [
    [
        "............................................................................##..",
        ".............................................................................#..",
        ".............................................................................#..",
        ".............................................................................#..",
        ".............................................................................#..",
        ".............................................................................#..",
        "..##..............................................................###........#..",
        "..#................................................##......##....##+##.......#..",
        "..#.................................o.o......##..................#+++#.......#..",
        "..#..............................................................##+##.......#..",
        "..#................................#####..........................#v#........#..",
        "..#..........................................................................#..",
        "..#.......................................o.o................................#..",
        "..#.....................o....................................................#..",
        "..#..@...................................#####.............................o.#..",
        "..#..........####.......o....................................................#..",
        "..#..........#..#................................................#####.......#..",
        "..############..###############...####################.....#######...#########..",
        "..............................#...#..................#.....#....................",
        "..............................#+++#..................#+++++#....................",
        "..............................#+++#..................#+++++#....................",
        "..............................#####..................#######....................",
        "................................................................................",
        "................................................................................",
    ],
    [
        "................................................................................",
        "................................................................................",
        "....###############################.............................................",
        "...##.............................##########################################....",
        "...#.......................................................................##...",
        "...#....o...................................................................#...",
        "...#................................................=.......................#...",
        "...#.o........################...................o..o...........|........o..#...",
        "...#.........................#..............................................#...",
        "...#....o....................##########.....###################....##########...",
        "...#..................................#+++++#.................#....#............",
        "...###############....oo......=o.o.o..#######.###############.#....#............",
        ".....#...............o..o.............#.......#......#........#....#............",
        ".....#....................#############..######.####.#.########....########.....",
        ".....#.............########..............#...........#.#..................#.....",
        ".....#..........####......####...#####################.#..................#.....",
        ".....#........###............###.......................########....########.....",
        ".....#.......##................#########################......#....#............",
        ".....#.......#................................................#....#............",
        ".....###......................................................#....#............",
        ".......#...............o...........................................#............",
        ".......#...............................................o...........#............",
        ".......#########......###.....############.........................##...........",
        ".............#..................#........#####....#######.o.........########....",
        ".............#++++++++++++++++++#............#....#.....#..................#....",
        ".............#++++++++++++++++++#..........###....###...####.o.............#....",
        ".............####################..........#........#......#.....|.........#....",
        "...........................................#++++++++#......####........@...#....",
        "...........................................#++++++++#.........#............#....",
        "...........................................#++++++++#.........##############....",
        "...........................................##########...........................",
        "................................................................................",
    ],
]


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 18
        self.height = 18
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 0.2
        self.jump_power = 0.7
        self.gravity = 0.0015
        self.on_ground = False
        self.camera_x = 0
        self.camera_y = 0
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        
    def update(self, frame, level_map, time_scale=1.0):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed * time_scale
        elif keys[pygame.K_RIGHT]:
            self.vel_x = self.speed * time_scale
        else:
            self.vel_x = 0
            
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False
            
        self.vel_y += self.gravity * frame * time_scale
            
        self.x += self.vel_x * frame
        self.check_collision_x(level_map)
        
        self.y += self.vel_y * frame
        self.check_collision_y(level_map)
        
        self.camera_x = self.x - WINDOW_WIDTH / 2 + self.width / 2
        self.camera_y = self.y - WINDOW_HEIGHT / 2 + self.height / 2
        
    def check_collision_x(self, level_map):
        left = int(self.x / BLOCK_SIZE)
        right = int((self.x + self.width) / BLOCK_SIZE)
        top = int(self.y / BLOCK_SIZE)
        bottom = int((self.y + self.height - 1) / BLOCK_SIZE)
        
        for y in range(max(0, top), min(len(level_map), bottom + 1)):
            for x in range(max(0, left), min(len(level_map[y]), right + 1)):
                if level_map[y][x] == '#':
                    block_rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    if player_rect.colliderect(block_rect):
                        if self.vel_x > 0:
                            self.x = block_rect.left - self.width
                        elif self.vel_x < 0:
                            self.x = block_rect.right
                        self.vel_x = 0
                        
    def check_collision_y(self, level_map):
        left = int(self.x / BLOCK_SIZE)
        right = int((self.x + self.width) / BLOCK_SIZE)
        top = int(self.y / BLOCK_SIZE)
        bottom = int((self.y + self.height - 1) / BLOCK_SIZE)
        
        self.on_ground = False
        for y in range(max(0, top), min(len(level_map), bottom + 1)):
            for x in range(max(0, left), min(len(level_map[y]), right + 1)):
                if level_map[y][x] == '#':
                    block_rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    if player_rect.colliderect(block_rect):
                        if self.vel_y > 0:
                            self.y = block_rect.top - self.height
                            self.vel_y = 0
                            self.on_ground = True
                        elif self.vel_y < 0:
                            self.y = block_rect.bottom
                            self.vel_y = 0
                            
    def get_camera_offset(self):
        return (self.camera_x, self.camera_y)
        
    def draw(self, screen):
        draw_x = self.x - self.camera_x
        draw_y = self.y - self.camera_y
        pygame.draw.rect(screen, PLAYER_COLOR, (draw_x, draw_y, self.width, self.height))


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BLOCK_SIZE // 3
        self.collected = False
        self.animation_offset = 0
        
    def update(self, frame, time_scale=1.0):
        self.animation_offset += frame * time_scale * 0.01
        
    def draw(self, screen, camera_x, camera_y):
        if not self.collected:
            draw_x = self.x - camera_x + BLOCK_SIZE // 2
            draw_y = self.y - camera_y + BLOCK_SIZE // 2 + math.sin(self.animation_offset) * 3
            pygame.draw.circle(screen, COIN_COLOR, (int(draw_x), int(draw_y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 150), (int(draw_x - 2), int(draw_y - 2)), 3)
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)


class Lava:
    def __init__(self, x, y, is_vertical, is_horizontal):
        self.x = x
        self.y = y
        self.width = BLOCK_SIZE
        self.height = BLOCK_SIZE
        self.is_vertical = is_vertical
        self.is_horizontal = is_horizontal
        self.animation_offset = 0
        
    def update(self, frame, time_scale=1.0):
        self.animation_offset += frame * time_scale * 0.01
        
    def draw(self, screen, camera_x, camera_y, time_stop_factor):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        
        color = self.create_time_stop_color(LAVA_COLOR, time_stop_factor)
        
        if self.is_vertical or self.is_horizontal:
            offset_x = 0
            offset_y = 0
            if self.is_vertical:
                offset_y = math.sin(self.animation_offset) * BLOCK_SIZE // 4
            if self.is_horizontal:
                offset_x = math.sin(self.animation_offset) * BLOCK_SIZE // 4
            pygame.draw.rect(screen, color, (draw_x + offset_x, draw_y + offset_y, self.width, self.height))
        else:
            pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))
            
    def create_time_stop_color(self, color, time_stop_factor):
        if 0 < time_stop_factor < 1:
            r = int(((255 - color[0]) * (1 - time_stop_factor) + color[0] * time_stop_factor) / 2)
            g = int(((255 - color[1]) * (1 - time_stop_factor) + color[1] * time_stop_factor) / 2)
            b = int(((255 - color[2]) * (1 - time_stop_factor) + color[2] * time_stop_factor) / 2)
            return (r, g, b)
        return color
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Miniplatform")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.current_level = 0
        self.level_map = []
        self.player = Player(100, 100)
        self.coins = []
        self.lavas = []
        
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
        
        self.load_level(self.current_level)
        
    def load_level(self, level_index):
        if level_index >= len(LEVEL_MAPS):
            return False
            
        self.level_map = LEVEL_MAPS[level_index]
        self.coins = []
        self.lavas = []
        self.player = Player(100, 100)
        self.time_multiplier = 1.0
        
        for y, line in enumerate(self.level_map):
            for x, char in enumerate(line):
                pos_x = x * BLOCK_SIZE
                pos_y = y * BLOCK_SIZE
                
                if char == 'o':
                    self.coins.append(Coin(pos_x, pos_y))
                elif char == '@':
                    self.player.set_position(pos_x, pos_y)
                elif char in ['v', '|', '=']:
                    is_vert = (char == 'v' or char == '|')
                    is_horiz = (char == '=')
                    self.lavas.append(Lava(pos_x, pos_y, is_vert, is_horiz))
                    
        if len(self.coins) > 0:
            self.time_acceleration_delta = 0.1
        else:
            self.time_acceleration_delta = 0
            
        return True
        
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
            
    def get_time_stop_factor(self):
        if not self.time_stop_active:
            return 1.0
        if self.time_stop_timer > self.time_stop_duration - 1:
            return (self.time_stop_timer - (self.time_stop_duration - 1))
        return 0.0
            
    def update(self, frame):
        if self.time_stop_active:
            self.time_stop_timer -= frame / 1000.0
            if self.time_stop_timer <= 0:
                self.time_stop_active = False
                self.time_stop_timer = 0
            
            self.player.update(frame, self.level_map, time_scale=1.0)
        else:
            self.game_time += (frame / 1000.0) * self.time_multiplier
            self.player.update(frame, self.level_map, time_scale=self.time_multiplier)
            
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            for coin in self.coins:
                if not coin.collected and player_rect.colliderect(coin.get_rect()):
                    coin.collected = True
                    self.score += 10
                    self.time_multiplier += self.time_acceleration_delta
                    
            for coin in self.coins:
                coin.update(frame, self.time_multiplier if not self.time_stop_active else 0)
                
            for lava in self.lavas:
                lava.update(frame, self.time_multiplier if not self.time_stop_active else 0)
                if player_rect.colliderect(lava.get_rect()):
                    self.load_level(self.current_level)
                    
        if self.time_stop_cooldown_timer > 0:
            self.time_stop_cooldown_timer -= frame / 1000.0
            
        all_collected = all(coin.collected for coin in self.coins)
        if all_collected and len(self.coins) > 0:
            self.current_level += 1
            if not self.load_level(self.current_level):
                self.current_level -= 1
            
    def draw(self):
        self.screen.fill(WHITE)
        
        camera_x, camera_y = self.player.get_camera_offset()
        time_stop_factor = self.get_time_stop_factor()
        
        for y, line in enumerate(self.level_map):
            for x, char in enumerate(line):
                if char == '#':
                    draw_x = x * BLOCK_SIZE - camera_x
                    draw_y = y * BLOCK_SIZE - camera_y
                    color = self.create_time_stop_color(WALL_COLOR, time_stop_factor)
                    pygame.draw.rect(self.screen, color, (draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
                elif char == '+':
                    draw_x = x * BLOCK_SIZE - camera_x
                    draw_y = y * BLOCK_SIZE - camera_y
                    color = self.create_time_stop_color(LAVA_COLOR, time_stop_factor)
                    pygame.draw.rect(self.screen, color, (draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
                    
        for lava in self.lavas:
            lava.draw(self.screen, camera_x, camera_y, time_stop_factor)
            
        for coin in self.coins:
            coin.draw(self.screen, camera_x, camera_y)
            
        self.player.draw(self.screen)
        
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        
        time_text = self.font.render(f"Time: {self.game_time:.1f}s", True, (0, 0, 0))
        self.screen.blit(time_text, (10, 50))
        
        speed_text = self.small_font.render(f"Speed: {self.time_multiplier:.1f}x", True, (0, 0, 0))
        self.screen.blit(speed_text, (10, 90))
        
        level_text = self.small_font.render(f"Level: {self.current_level + 1}", True, (0, 0, 0))
        self.screen.blit(level_text, (10, 120))
        
        if self.time_stop_active:
            stop_text = self.font.render("TIME STOPPED!", True, (220, 20, 60))
            text_rect = stop_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
            self.screen.blit(stop_text, text_rect)
            
            timer_text = self.small_font.render(f"{self.time_stop_timer:.1f}s", True, (220, 20, 60))
            timer_rect = timer_text.get_rect(center=(WINDOW_WIDTH // 2, 60))
            self.screen.blit(timer_text, timer_rect)
        elif self.time_stop_cooldown_timer > 0:
            cooldown_text = self.small_font.render(f"Time Stop: {self.time_stop_cooldown_timer:.1f}s", True, (128, 128, 128))
            self.screen.blit(cooldown_text, (WINDOW_WIDTH - 200, 10))
        else:
            ready_text = self.small_font.render("Time Stop: Ready (Z)", True, (0, 128, 0))
            self.screen.blit(ready_text, (WINDOW_WIDTH - 220, 10))
            
        controls_text = self.small_font.render("Arrow Keys: Move | Z: Time Stop", True, (0, 0, 0))
        self.screen.blit(controls_text, (WINDOW_WIDTH // 2 - 180, WINDOW_HEIGHT - 25))
        
        pygame.display.flip()
        
    def create_time_stop_color(self, color, time_stop_factor):
        if 0 < time_stop_factor < 1:
            r = int(((255 - color[0]) * (1 - time_stop_factor) + color[0] * time_stop_factor) / 2)
            g = int(((255 - color[1]) * (1 - time_stop_factor) + color[1] * time_stop_factor) / 2)
            b = int(((255 - color[2]) * (1 - time_stop_factor) + color[2] * time_stop_factor) / 2)
            return (r, g, b)
        return color
        
    def run(self):
        while self.running:
            frame = self.clock.tick(FPS)
            
            self.handle_events()
            self.update(frame)
            self.draw()
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
