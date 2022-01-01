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
    COOLDOWN = 30

    def __init__(self, x: int, y: int, health: int = 100) -> None:
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown = 0

    def cooldown_count(self):
        if self.cooldown >= self.COOLDOWN:
            self.cooldown = 0
        elif self.cooldown >= 0:
            self.cooldown += 1

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.render()

    def move_lasers(self, vel, obj):
        self.cooldown_count()
        for laser in self.lasers:
            laser.move(vel)
            if laser.is_offscreen():
                self.lasers.remove(laser)
            elif laser.is_colliding(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    @property
    def width(self):
        return self.ship_img.get_width()

    @property
    def height(self):
        return self.ship_img.get_height()

    def shoot(self):
        if self.cooldown == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown = 1


class Player(Ship):
    def __init__(self, x: int, y: int, health: int = 100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown_count()
        for laser in self.lasers:
            laser.move(vel)
            if laser.is_offscreen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.is_colliding(obj):
                        print("Collision!")
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)


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
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def render(self):
        WIN.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y -= vel

    def is_offscreen(self):
        return self.y <= 0 or self.y >= HEIGHT

    def is_colliding(self, obj):
        return collision(self, obj)


class LostFont:
    def __init__(self, font_size):
        self.font_size = font_size

    def render(self):
        lost_font = pygame.font.SysFont("arial", self.font_size, bold=True)
        lost_text = lost_font.render("YOU LOST!!", True, (255, 0, 0))
        WIN.blit(lost_text, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 - lost_text.get_height()//2))


# Function to determine if two surfaces are overlapping each other (colliding)
def collision(obj1, obj2):
    x_offset = obj1.x - obj2.x
    y_offset = obj1.y - obj2.x
    return obj1.mask.overlap(obj2.mask, (x_offset, y_offset)) is not None


def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    player_vel = 5
    clock = pygame.time.Clock()

    enemies = []
    wave_len = 0
    enemy_vel = 2
    laser_vel = 5

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
        test_label = main_font.render(f"Number of enemies = {len(enemies)}", True, (255, 255, 255))
        WIN.blit(test_label, (10, HEIGHT - test_label.get_height() - 10))
        laser_label = main_font.render(f"Number of lasers = {len(player.lasers)}", True, (255, 255, 255))
        WIN.blit(laser_label, (WIDTH - laser_label.get_width() - 10, HEIGHT - test_label.get_height() - 10))

        # if lost:
        #     if lost_text.font_size < 200:
        #         lost_text.render()
        #         lost_text.font_size += 1

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

        # if lost:
        #     if lost_count >= fps * 4 or lost_text.font_size > 200:
        #         run = False
        #     else:
        #         continue

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
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if enemy.y > HEIGHT - enemy.height:
                if lives > 0:
                    lives -= 1
                enemies.remove(enemy)

        player.move_lasers(laser_vel, enemies)


if __name__ == '__main__':
    main()
