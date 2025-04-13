import math
import random
import pgzero
import pgzrun

WIDTH = 816
HEIGHT = 624
TOTAL_ENEMY_NUMBER = 12

game_state = "menu"
music_state = "on"
buttons = {
    "Start": Rect((298, 200), (200, 50)),
    "Music on/off": Rect((298, 300), (200, 50)),
    "Exit": Rect((298, 400), (200, 50)),
}

class player:

    def __init__(self):
        self.actor = Actor("character/idle/down/frame_0", (WIDTH/2, HEIGHT/2))

        self.state = "idle"

        self.direction = "down"

        self.lives = 3

    def change_state(self, new_state):
        self.state = new_state

    def move(self):

        if keyboard.left and self.actor.left > 32:

            self.change_state("run")
            self.direction = "left"
            self.actor.left -=4

        elif keyboard.right and self.actor.right < 784:
            self.change_state("run")
            self.direction = "right"
            self.actor.right +=4

        elif keyboard.up and self.actor.top > 32:
            self.change_state("run")
            self.direction = "up"
            self.actor.top -=4

        elif keyboard.down and self.actor.bottom < 594:
            self.change_state("run")
            self.direction = "down"
            self.actor.bottom +=4

        else:
            self.change_state("idle")

        if keyboard.space:
            check_hit(p1, enemies)
            sounds.hit.play()


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
            self.actor.x -= math.copysign(self.speed, (self.actor.x - target_x)) + random.randint(0, int(self.speed/2))
            self.actor.y -= math.copysign(self.speed, (self.actor.y - target_y)) + random.randint(0, int(self.speed/2))
  

def check_collision(player, enemy_list):

    for i in range(len(enemy_list)):
        if (player.actor.colliderect(enemy_list[i].actor) and enemy_list[i].state == 0):           
           player.lives -=1
           enemy_list[i].state = 1

def check_hit(player, enemy_list):

    hit_range = 24
    
    for i in range(len(enemy_list)):

        if p1.direction == "down":
            hit_point = (player.actor.x, player.actor.y + hit_range)
            if (enemy_list[i].actor.collidepoint(hit_point) and enemy_list[i].state == 0):
                enemy_list[i].state = 1
                
        
        if p1.direction == "right":
            hit_point = (player.actor.x + hit_range, player.actor.y)
            if (enemy_list[i].actor.collidepoint(hit_point) and enemy_list[i].state == 0):
                enemy_list[i].state = 1
        
        if p1.direction == "up":
            hit_point = (player.actor.x, player.actor.y - hit_range)
            if (enemy_list[i].actor.collidepoint(hit_point) and enemy_list[i].state == 0):
                enemy_list[i].state = 1
        
        if p1.direction == "left":
            hit_point = (player.actor.x - hit_range, player.actor.y)
            if (enemy_list[i].actor.collidepoint(hit_point) and enemy_list[i].state == 0):
                enemy_list[i].state = 1


def change_game_state(new_state):
    global game_state 
    game_state = new_state

#main
p1 = player()

enemy_entry_positions = [(0, HEIGHT/2), (WIDTH/2, 0), (WIDTH/2, HEIGHT), (WIDTH, HEIGHT/2)]
enemy_types = ["flame", "bamboo"]
enemies = []
enemy_count = 0

def spawn_enemy():
    global enemy_count
    if enemy_count < TOTAL_ENEMY_NUMBER:
        enemies.append(Enemy(random.choice(enemy_types), random.choice(enemy_entry_positions) , 2))
        enemy_count += 1
        clock.schedule_unique(spawn_enemy, random.randint(1, 5))

player_current_frame = 0
frame_timer = 0
frame_delay = 8 
sounds.theme.play(-1)

def update():
    global player_current_frame, frame_timer, game_state

    if game_state == "game":
        frame_timer += 1
        if frame_timer >= frame_delay:
            frame_timer = 0
            player_current_frame = (player_current_frame + 1) % 4
            p1.animate(player_current_frame)

            for i in range(len(enemies)):
                enemies[i].animate(player_current_frame)

        random.seed(player_current_frame)
        p1.move()

        for i in range(len(enemies)):
            enemies[i].move(p1.actor.x, p1.actor.y)
            pass

        check_collision(p1, enemies)

        if p1.lives == 0:
            draw_game_screen()
            game_state = "lose"

        if enemy_count == 12:
            draw_game_screen()
            game_state = "win"


def draw_game_screen():
    screen.clear()
    screen.blit('map', (0, 0))
    p1.actor.draw()
    
    for i in range(len(enemies)):
        if enemies[i].state == 0:
            enemies[i].actor.draw()
    
    screen.draw.text(f"Lives : {p1.lives}", (50, 70), fontsize=50)
    screen.draw.text(f"Monsters left : {12 - enemy_count}", (500, 70), fontsize=50)
    

def draw_menu_screen():
    screen.fill((27, 166, 154))
    screen.draw.text("THE GAME", center=(WIDTH // 2, 100), fontsize=80)

    for name, rect in buttons.items():
        screen.draw.filled_rect(rect, "gray")
        screen.draw.text(name, center=rect.center, fontsize=30, color="white")

def lose_screen():
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT/2), fontsize=80)

def draw():

    if game_state == "menu":
        draw_menu_screen()

    elif game_state == "game":
        draw_game_screen()
    
    elif game_state == "lose":
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT/2), fontsize=80)
    
    elif game_state == "win":
        screen.draw.text("You won", center=(WIDTH // 2, HEIGHT/2), fontsize=80)


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