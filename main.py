import pygame
from pygame import mixer
import os
import random
import json

pygame.init()
mixer.init()
pygame.font.init()
clock = pygame.time.Clock()

with open("sav_data.json") as sav:
    data = json.load(sav)


def hello_from_git():
    pass


WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooters")

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
                window.blit(boost_cd_label, (self.x - 10 - boost_cd_label.get_width(), self.y + self.height + 23))
                window.blit(boost_duration_counter, (self.x + boost_duration_counter.get_width() + 10, self.y + self.height + 30))
            else:
                window.blit(boost_ready_label, (self.x - 10 - boost_ready_label.get_width(), self.y + self.height + 23))
        else:
            window.blit(boost_label, (self.x - 10 - boost_label.get_width(), self.y + self.height + 23))
            window.blit(boost_cd_counter, (self.x + boost_cd_counter.get_width() + 10, self.y + self.height + 30))

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


# Function to determine if two surfaces are overlapping each other (colliding)
def collision(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def write_data(player, player_name):
    player_acc = float(f"{(player.number_hit/player.total_shots * 100):.2f}")
    if data['players'][player_name]['accuracy'] < player_acc and\
            player.get_number_hit > data['players'][player_name]['high_score']:
        data['players'][player_name]['accuracy'] = player_acc
    if data['players'][player_name]['high_score'] < player.number_hit:
        data['players'][player_name]['high_score'] = player.number_hit
    if data['players'][player_name]['highest_level'] < player.highest_level:
        data['players'][player_name]['highest_level'] = player.highest_level
    with open("sav_data.json", 'w') as updated:
        json.dump(data, updated, indent=2)


def create_data(player_name):
    data['players'][player_name] = {}
    data['players'][player_name]['accuracy'] = 0.00
    data['players'][player_name]['high_score'] = 0
    data['players'][player_name]['highest_level'] = 1
    with open("sav_data.json", 'w') as updated:
        json.dump(data, updated, indent=2)


def clear_name(name):
    if name in data['players']:
        del data['players'][name]
        with open("sav_data.json", 'w') as updated:
            json.dump(data, updated, indent=2)
        print(f"{name} got removed successfully")
    else:
        print(f"Player {name} does not exist")


def leaderboard():
    run = True
    menu_font = pygame.font.SysFont("firacodenerdfontcompletemono", 40)
    quit_font = pygame.font.SysFont("firacodenerdfontcompletemono", 25)
    while run:
        WIN.blit(BG, (0, 0))
        offset = 0
        for player in data['players']:
            title = menu_font.render(f"{player.title()} high score: {data['players'][player]['high_score']}",
                                     True, (255, 255, 255))
            WIN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4 + offset))
            offset += title.get_height() + 100
        quit_title = quit_font.render("**Press e to return to main menu**", True, (255, 255, 255))
        remove_name = quit_font.render("**Press c to remove name from leaderboard**", True, (255, 255, 255))
        WIN.blit(quit_title, (WIDTH//2 - quit_title.get_width()//2, HEIGHT//4 + offset))
        offset += quit_title.get_height()
        WIN.blit(remove_name, (WIDTH//2 - remove_name.get_width()//2, HEIGHT//4 + offset))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            run = False
        if keys[pygame.K_c]:
            name = input("Who would you like to remove? ")
            clear_name(name)


def menu():
    run = True
    menu_font = pygame.font.SysFont("firacodenerdfontcompletemono", 40)
    while run:
        WIN.blit(BG, (0, 0))
        first = menu_font.render("Press 1 to play", True, (255, 255, 255))
        second = menu_font.render("Press 2 for leaderboard", True, (255, 255, 255))
        third = menu_font.render("Press 3 or q to quit", True, (255, 255, 255))
        options = [first, second, third]
        offset = 0
        for option in options:
            WIN.blit(option, (WIDTH//2 - option.get_width()//2, HEIGHT//4 + offset))
            offset += option.get_height() + 100
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            main()
        if keys[pygame.K_2]:
            leaderboard()
        if keys[pygame.K_3] or keys[pygame.K_q]:
            quit()


def pause():
    mixer.music.pause()
    paused = True
    pause_font = pygame.font.SysFont("arial", 100, True)
    keys_font = pygame.font.SysFont("arial", 20, True)
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_m:
                    menu()
        WIN.blit(BG, (0, 0))
        pause_msg = pause_font.render("GAME PAUSED", True, (255, 0, 0))
        keys_msg = keys_font.render("Press ESC to continue or q to quit or m to return to main menu", True, (255, 0, 0))
        WIN.blit(pause_msg, (WIDTH//2 - pause_msg.get_width()//2, HEIGHT//2 - pause_msg.get_height()//2))
        WIN.blit(keys_msg, (WIDTH//2 - keys_msg.get_width()//2, HEIGHT//2 + pause_msg.get_height() * 2
                            + keys_msg.get_height()//2 + 15))
        pygame.display.update()
        clock.tick(5)


def test_branch():
    print("hello git")


def main():
    player_name = input("What's your name? ").lower().strip()
    if player_name not in data['players']:
        create_data(player_name)
    run = True
    fps = 60
    level = 0
    lives = 5
    player_vel = 5

    enemies = []
    wave_len = 0
    enemy_vel = 2
    laser_vel = 5

    lost = False
    lost_count = 0

    player = Player(WIDTH//2 - 70, HEIGHT - 170)
    lost_text = LostFont(20)

    # Background Music
    mixer.music.load('assets/background.wav')
    mixer.music.set_volume(0.7)
    mixer.music.play(-1)

    # function to draw images onto the window
    def redraw_window():
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", True, (255, 0, 127))
        level_label = main_font.render(f"Level: {level}", True, (255, 0, 127))
        # render the lives and level labels
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        test_label = main_font.render(f"Enemies = {len(enemies)}", True, (255, 255, 255))
        WIN.blit(test_label, (10, HEIGHT - test_label.get_height() - 10))
        number_hit = main_font.render(f"Hit = {player.get_number_hit}", True, (255, 255, 255))
        WIN.blit(number_hit, (WIDTH - number_hit.get_width() - 10, HEIGHT - test_label.get_height() - 10))
        health_label = main_font.render(f"Health: {player.health}", True, (255, 255, 255))
        WIN.blit(health_label, (WIDTH//2 - health_label.get_width()//2, 10))
        acc_label = main_font.render(f"Acc: {(player.number_hit/player.total_shots * 100):.2f}%", True, (255, 255, 255))
        WIN.blit(acc_label, (WIDTH//2 - acc_label.get_width()//2, HEIGHT - acc_label.get_height() - 10))
        high_score_label = main_font.render(f"Highest acc: {data['players'][player_name]['accuracy']}%",
                                            True, (255, 255, 255))
        WIN.blit(high_score_label, (10, lives_label.get_height() + 20))
        highest_hit_label = main_font.render(f"Highest hit: {data['players'][player_name]['high_score']}",
                                             True, (255, 255, 255))
        WIN.blit(highest_hit_label, (WIDTH - highest_hit_label.get_width() - 10, lives_label.get_height() + 10))
        laser_vel_label = main_font.render(f"Laser Vel: {player.laser_vel}", True, (255, 255, 255))
        WIN.blit(laser_vel_label, (10, HEIGHT//2 - acc_label.get_height() - 10))

        if lost:
            if lost_text.font_size < 150:
                lost_text.font_size += 1
            lost_text.render()

        for en in enemies:
            en.draw(WIN)

        player.draw(WIN)

        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            mixer.music.stop()
            ded = mixer.Sound('assets/ded.wav')
            ded.set_volume(1.0)
            ded.play()
            lost_count += 1

        if lost:
            if lost_count >= fps * 5.5:
                write_data(player, player_name)
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            player.highest_level += 1
            if level == 1:
                wave_len = 3
            else:
                wave_len += level - 1
            for i in range(wave_len):
                enemy = Enemy(random.randrange(50, WIDTH - 100, 20),
                              random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x > 0:
            player.x -= player.player_vel
        if keys[pygame.K_w] and player.y > 150:
            player.y -= player.player_vel
        if keys[pygame.K_d] and player.x < WIDTH - player.width:
            player.x += player.player_vel
        if keys[pygame.K_s] and player.y < HEIGHT - player.height - 30:
            player.y += player.player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_r] and player.enable_boost:
            boost_sfx = mixer.Sound('assets/powerup.wav')
            boost_sfx.set_volume(0.2)
            boost_sfx.play()
            print("Boost triggered!")
            player.boost_triggered = True
        if keys[pygame.K_ESCAPE]:
            pause()
            mixer.music.unpause()

        for enemy in enemies[:]:
            enemy.move_lasers(laser_vel, player)
            if enemy.health == 0:
                enemy.alive = False
            if enemy.alive:
                enemy.move(enemy_vel)
                if random.randrange(0, fps * 3) == 1:
                    enemy.shoot()
                if collision(enemy, player):
                    if player.health - 20 > 0:
                        player.health -= 20
                    else:
                        player.health = 0
                    explosion = mixer.Sound('assets/explosion.wav')
                    explosion.play()
                    enemies.remove(enemy)
                elif enemy.y > HEIGHT - enemy.height:
                    if lives > 0:
                        lives -= 1
                    enemies.remove(enemy)
            else:
                if enemy.dead_timer <= 0:
                    enemies.remove(enemy)
                else:
                    enemy.dead_timer -= 1

        player.move_lasers(-player.laser_vel, enemies)


if __name__ == '__main__':
    menu()
