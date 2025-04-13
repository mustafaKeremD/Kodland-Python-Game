import math
import random
import pgzero
import pgzrun

WIDTH = 816
HEIGHT = 624
TOTAL_ENEMY_NUMBER = 6

# Global variables needed in more than one function across the code
game_state = "menu"
music_state = "on"
buttons = {
    "Start": Rect((298, 270), (200, 50)),
    "Music on/off": Rect((298, 370), (200, 50)),
    "Exit": Rect((298, 470), (200, 50)),
}


enemy_entry_positions = [(0, HEIGHT / 2), (WIDTH / 2, 0),
                         (WIDTH / 2, HEIGHT), (WIDTH, HEIGHT / 2)]
enemy_types = ["flame", "bamboo"]
enemies = []
enemy_count = 0

is_attacking = False
attack_frame = 0
attack_timer = 0
attack_frame_duration = 0.1
attack_frames = [f"character/slash/frame_{i}" for i in range(4)]

monsters_left = TOTAL_ENEMY_NUMBER

player_current_frame = 0
frame_timer = 0
frame_delay = 8
sounds.theme.play(-1)


class Player:

    def __init__(self):
        self.actor = Actor("character/idle/down/frame_0",
                           (WIDTH / 2, HEIGHT / 2))

        self.state = "idle"

        self.direction = "down"

        self.lives = 3

        self.attack_pos = (0, 0)

    def change_state(self, new_state):
        self.state = new_state

    def move(self):
        global is_attacking, attack_frame, attack_timer

        if keyboard.left and self.actor.left > 32:

            self.change_state("run")
            self.direction = "left"
            self.actor.left -= 4

        elif keyboard.right and self.actor.right < 784:
            self.change_state("run")
            self.direction = "right"
            self.actor.right += 4

        elif keyboard.up and self.actor.top > 32:
            self.change_state("run")
            self.direction = "up"
            self.actor.top -= 4

        elif keyboard.down and self.actor.bottom < 594:
            self.change_state("run")
            self.direction = "down"
            self.actor.bottom += 4

        else:
            self.change_state("idle")

        if keyboard.space and not is_attacking:
            self.attack_pos = check_hit(player, enemies)
            sounds.slash.play()

            is_attacking = True
            attack_frame = 0
            attack_timer = 0

    def animate(self, current_frame):

        self.actor.image = f"character/{self.state}/{self.direction}/frame_{current_frame}"


class Enemy:

    # 0 for live, 1 for dead
    state = 0
    def __init__(self, kind, position, speed):
        self.animation_sprite = [f"enemies/{kind}/frame_{i}" for i in range(4)]
        self.actor = Actor(self.animation_sprite[0], position)
        self.speed = speed

    def animate(self, current_frame):
        self.actor.image = self.animation_sprite[current_frame]

    def move(self, target_x, target_y):
        if self.state == 0:
            self.actor.x -= (math.copysign(self.speed, (self.actor.x - target_x)) +
                             random.randint(0, int(self.speed/2)))

            self.actor.y -= (math.copysign(self.speed, (self.actor.y - target_y)) +
                             random.randint(0, int(self.speed/2)))


def check_collision(player, enemy_list):
    global monsters_left

    #Check for if player actor collides with any enemy actor
    for i in range(len(enemy_list)):
        if (player.actor.colliderect(enemy_list[i].actor)
                and enemy_list[i].state == 0):
            player.lives -= 1
            enemy_list[i].state = 1
            monsters_left -= 1
            sounds.damage.play()


def check_hit(player, enemy_list):

    global monsters_left

    hit_range = 32
    x, y = player.actor.center

    if player.direction == "down":
        hit_point = (x, y + hit_range)

    if player.direction == "right":
        hit_point = (x + hit_range, y)

    if player.direction == "up":
        hit_point = (x, y - hit_range)

    if player.direction == "left":
        hit_point = (x - hit_range, y)

    for i in range(len(enemy_list)):

        if (enemy_list[i].actor.collidepoint(hit_point)
                and enemy_list[i].state == 0):
            enemy_list[i].state = 1
            sounds.hit.play()
            monsters_left -= 1

    return hit_point


def change_game_state(new_state):
    global game_state
    game_state = new_state


def spawn_enemy():
    global enemy_count
    #Appends a member of Enemy class with randomized type and spawn point
    #There is 4 possible spawn point declared in enemy_entry_positions
    if enemy_count < TOTAL_ENEMY_NUMBER:
        enemies.append(
            Enemy(
                random.choice(enemy_types),
                random.choice(enemy_entry_positions),
                2))
        enemy_count += 1
        clock.schedule_unique(spawn_enemy, random.randint(1, 5))


player = Player()


def update(dt):
    global player_current_frame, frame_timer, game_state
    global attack_timer, attack_frame, is_attacking

    if game_state == "game":
        frame_timer += 1
        if frame_timer >= frame_delay:
            frame_timer = 0
            player_current_frame = (player_current_frame + 1) % 4
            player.animate(player_current_frame)

            for i in range(len(enemies)):
                enemies[i].animate(player_current_frame)

        random.seed(player_current_frame)
        player.move()

        for i in range(len(enemies)):
            enemies[i].move(player.actor.x, player.actor.y)

        check_collision(player, enemies)

        if player.lives == 0:
            draw_game_screen()
            sounds.theme.stop()
            sounds.game_over.play()
            game_state = "lose"

        if monsters_left == 0 and player.lives != 0:
            draw_game_screen()
            sounds.theme.stop()
            sounds.win.play()
            game_state = "win"

        #Calculate and animate attack animation only 
        if is_attacking:
            attack_timer += dt
            if attack_timer >= attack_frame_duration:
                attack_timer = 0
                attack_frame += 1
                if attack_frame >= len(attack_frames):
                    is_attacking = False


def draw_game_screen():
    global monsters_left

    screen.clear()
    screen.blit('map', (0, 0))
    player.actor.draw()

    for i in range(len(enemies)):
        if enemies[i].state == 0:
            enemies[i].actor.draw()

    screen.draw.text(f"Lives : {player.lives}", (50, 70), fontsize=50)
    screen.draw.text(
        f"Monsters left : {monsters_left}", (500, 70), fontsize=50)

    if is_attacking:

        screen.blit(
            attack_frames[attack_frame],
            (player.attack_pos[0] - 32,
             player.attack_pos[1] - 32))


def draw_menu_screen():
    screen.fill((27, 166, 154))
    screen.draw.text("THE GAME", center=(WIDTH // 2, 100), fontsize=80)
    screen.draw.text(
        "\"Arrow keys to move\"",
        center=(
            WIDTH // 2,
            180),
        fontsize=50)
    screen.draw.text(
        "\"Space to attack\"",
        center=(
            WIDTH // 2,
            230),
        fontsize=50)

    for name, rect in buttons.items():
        screen.draw.filled_rect(rect, "gray")
        screen.draw.text(name, center=rect.center, fontsize=30, color="white")


def lose_screen():
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT / 2), fontsize=80)


def draw():


    if game_state == "menu":
        draw_menu_screen()

    elif game_state == "game":
        draw_game_screen()

    elif game_state == "lose":
        screen.draw.text(
            "GAME OVER",
            center=(
                WIDTH // 2,
                HEIGHT / 2),
            fontsize=80)

    elif game_state == "win":
        screen.draw.text(
            "You won",
            center=(
                WIDTH // 2,
                HEIGHT / 2),
            fontsize=80)


def on_mouse_down(pos):

    global game_state, music_state

    if game_state == "menu":

        for name, rect in buttons.items():

            if rect.collidepoint(pos):

                if name == "Start":
                    change_game_state("game")
                    spawn_enemy()

                elif name == "Music on/off":

                    if music_state == "on":
                        sounds.theme.stop()
                        music_state = "off"

                    elif music_state == "off":
                        sounds.theme.play(-1)
                        music_state = "on"

                elif name == "Exit":
                    exit()


pgzrun.go()
