import random
import json
from classes import *
import pygame
from pygame import mixer

pygame.init()
mixer.init()
pygame.font.init()
clock = pygame.time.Clock()

with open("sav_data.json") as sav:
    data = json.load(sav)


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
