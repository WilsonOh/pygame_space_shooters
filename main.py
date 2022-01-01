import pygame
import time
import os
import random

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooters")
pygame.font.init()

# Ship Images
RED_SHIP = pygame.image.load(os.path.join("pixel_ship_red_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("pixel_ship_green_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("pixel_ship_blue_small.png"))

# Player Ship
YELLOW_SHIP = pygame.image.load(os.path.join("pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale((pygame.image.load(os.path.join("background-black.png"))), (WIDTH, HEIGHT))

# Font for text
main_font = pygame.font.SysFont("firacodenerdfontcompletemono", 30, bold=False)


# Create Parent Ship Class
class Ship:
    def __init__(self, x: int, y: int, health: int = 100) -> None:
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

    @property
    def width(self):
        return self.ship_img.get_width()

    @property
    def height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x: int, y: int, health: int = 100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health


class Enemy(Ship):
    colors = {
        "red": (RED_SHIP, RED_LASER),
        "green": (GREEN_SHIP, GREEN_LASER),
        "blue": (BLUE_SHIP, BLUE_LASER)
    }

    def __init__(self, x: int, y: int, color: str, health: int = 100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.colors[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def render(self, laser_img):
        WIN.blit(laser_img, (self.x, self.y))


class LostFont:
    def __init__(self, font_size):
        self.font_size = font_size

    def render(self):
        lost_font = pygame.font.SysFont("arial", self.font_size, bold=True)
        lost_text = lost_font.render("YOU LOST!!", True, (255, 0, 0))
        WIN.blit(lost_text, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 - lost_text.get_height()//2))


def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    player_vel = 5
    clock = pygame.time.Clock()

    enemies = []
    wave_len = 0
    enemy_vel = 10

    lost = False
    lost_count = 0

    player = Player(WIDTH//2 - 70, HEIGHT - 100)
    lost_text = LostFont(20)

    # function to draw images onto the window
    def redraw_window():
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", True, (255, 0, 127))
        level_label = main_font.render(f"Level: {level}", True, (255, 0, 127))
        # render the lives and level labels
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        laser = Laser(player.x, player.y - 100)
        laser.render(player.laser_img)

        if lost:
            if lost_text.font_size < 200:
                lost_text.render()
                lost_text.font_size += 1

        for en in enemies:
            en.draw(WIN)

        player.draw(WIN)

        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count >= fps * 4 or lost_text.font_size > 200:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_len += 5
            for i in range(wave_len):
                enemy = Enemy(random.randrange(50, WIDTH - 100, 20),
                              random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x > 0:
            player.x -= player_vel
        if keys[pygame.K_w] and player.y > 150:
            player.y -= player_vel
        if keys[pygame.K_d] and player.x < WIDTH - player.width:
            player.x += player_vel
        if keys[pygame.K_s] and player.y < HEIGHT - player.height:
            player.y += player_vel

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            if enemy.y > HEIGHT - enemy.height:
                if lives > 0:
                    lives -= 1
                enemies.remove(enemy)


if __name__ == '__main__':
    main()
