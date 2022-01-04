from main import collision
import pygame
from pygame import mixer
import os

WIDTH, HEIGHT = 1000, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooters")

# Window Icon
window_icon = pygame.transform.scale(pygame.image.load('assets/pixel_ship_yellow.png'), (32, 32))
pygame.display.set_icon(window_icon)

# Ship Images
RED_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player Ship
YELLOW_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale((pygame.image.load(os.path.join("assets", "background-black.png"))), (WIDTH, HEIGHT))

# Exploded Enemy Ship
EXPLODED_ENEMY = pygame.transform.scale((pygame.image.load('assets/explosion.png')), (50, 50))

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
        self.max_health = health

    def cooldown_count(self):
        if self.cooldown >= self.COOLDOWN:
            self.cooldown = 0
        elif self.cooldown > 0:
            self.cooldown += 1

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        self.health_bar(window)
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown_count()
        for laser in self.lasers:
            laser.move(vel)
            if laser.is_offscreen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.is_colliding(obj):
                if obj.health > 0:
                    obj.health -= 10
                if laser in self.lasers:
                    self.lasers.remove(laser)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.height + 10, self.width, 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.height + 10,
                                               self.width * (self.health/self.max_health), 10))

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

    def exploded(self):
        return pygame.transform.scale((pygame.image.load('assets/explosion.png')), (self.width, self.height))


class Player(Ship):
    player_vel = 5
    BOOST_CD = 300
    number_hit = 1
    total_shots = 1
    highest_level = 0
    laser_vel = 5
    boost_cd = 300
    boost_duration = 120
    enable_boost = False
    boost_triggered = False

    def __init__(self, x: int, y: int, health: int = 100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    @property
    def get_number_hit(self):
        return self.number_hit

    def boost(self):
        if self.enable_boost:
            if self.boost_triggered:  # add boost features here
                self.laser_vel = 10
                self.COOLDOWN = 10
                self.player_vel = 10
                self.boost_duration -= 1
                if self.boost_duration <= 0:
                    self.player_vel = 5
                    self.boost_duration = 120
                    self.enable_boost = False
                    self.boost_cd = self.BOOST_CD
                    self.laser_vel = 5
                    self.COOLDOWN = 30
                    self.boost_triggered = False
        else:
            if self.boost_cd <= 0:
                self.enable_boost = True
                if self.boost_duration == 120:
                    print("Boost ready!")
            else:
                self.boost_cd -= 1

    def boost_bar(self, window):
        boost_font = pygame.font.SysFont("firacodenerdfontcompletemono", 20, bold=True)
        pygame.draw.rect(window, (51, 51, 255), (self.x, self.y + self.height + 30,
                                                 (self.boost_cd/self.BOOST_CD) * self.width, 15))
        bar_font = pygame.font.SysFont("arial", 15, bold=True)
        boost_label = bar_font.render("Boost Loading... ", True, (255, 255, 255))
        boost_cd_label = bar_font.render("BOOOOST!!", True, (255, 255, 153))
        boost_ready_label = bar_font.render("Boost Ready!", True, (255, 255, 153))
        boost_cd_counter = boost_font.render(f"{(self.boost_cd/60):.2f}", True, (255, 255, 255))
        boost_duration_counter = boost_font.render(f"{(self.boost_duration/60):.2f}", True, (255, 255, 255))
        if self.boost_cd <= 0:
            pygame.draw.rect(window, (204, 0, 204), (self.x, self.y + self.height + 30,
                                                     (self.boost_duration/120) * self.width, 15))
            if self.boost_triggered:
                window.blit(boost_cd_label, (self.x - 11 - boost_cd_label.get_width(), self.y + self.height + 23))
                window.blit(boost_duration_counter, (self.x + boost_duration_counter.get_width()//2,
                                                     self.y + self.height + 30))
            else:
                window.blit(boost_ready_label, (self.x - 10 - boost_ready_label.get_width(), self.y + self.height + 23))
        else:
            window.blit(boost_label, (self.x - 10 - boost_label.get_width(), self.y + self.height + 23))
            window.blit(boost_cd_counter, (self.x + boost_cd_counter.get_width()//2, self.y + self.height + 30))

    def draw(self, window):
        super().draw(window)
        self.boost_bar(window)

    def move_lasers(self, vel, objs):
        self.cooldown_count()
        self.boost()
        for laser in self.lasers:
            laser.move(vel)
            if laser.is_offscreen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if collision(obj, laser):
                        if obj.alive:
                            obj.health -= 10
                            if obj.health == 0:
                                obj.ship_img = obj.exploded()
                                exploded = mixer.Sound('assets/explosion.wav')
                                exploded.play()
                            # print("Collision!")
                            if laser in self.lasers:
                                self.lasers.remove(laser)
                                self.number_hit += 1

    def shoot(self):
        if self.cooldown == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown = 1
            self.total_shots += 1
            laser = mixer.Sound('assets/laser.wav')
            laser.play()


class Enemy(Ship):
    alive = True
    dead_timer = 60

    colors = {
        "red": (RED_SHIP, RED_LASER),
        "green": (GREEN_SHIP, BLUE_LASER),
        "blue": (BLUE_SHIP, GREEN_LASER)
    }

    def __init__(self, x: int, y: int, color: str):
        super().__init__(x, y)
        self.health = 20 if color == "blue" else 10
        self.ship_img, self.laser_img = self.colors[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = self.health

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cooldown == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown = 1


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def is_offscreen(self, height):
        return not(0 <= self.y <= height)

    def is_colliding(self, obj):
        return collision(self, obj)


class LostFont:
    def __init__(self, font_size):
        self.font_size = font_size

    def render(self):
        lost_font = pygame.font.SysFont("arial", self.font_size, bold=True)
        lost_text = lost_font.render("YOU DIED!!", True, (255, 0, 0))
        WIN.blit(lost_text, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 - lost_text.get_height()//2))
