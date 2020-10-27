import pygame
from math import pi, cos, sin, atan2

pygame.init()

# Steps measure
STEP = 4
# Define some colours
# Colours are defined using RGB values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BRIGHT_GREEN = (0, 255, 0)
BRIGHT_RED = (255, 0, 0)
RED = (200, 0, 0)
BACKGROUND = (0, 255, 255)

# Open a new window
# The window is defined as (width, height), measured in pixels
WIDTH = 1000
HEIGHT = 500

# Game loop
GAME_RUN = True
GAME_OVER = False
GAME_STATE_INIT = 1
GAME_STATE_RUNNING = 2
GAME_STATE_FINISH = 3

wall1 = pygame.image.load("./wall1.png")
wall2 = pygame.image.load("./wall2.png")
wall3 = pygame.image.load("./wall3.png")
wall4 = pygame.image.load("./wall4.png")
wall5 = pygame.image.load("./wall5.png")

textures = {
    "1": wall1,
    "2": wall2,
    "3": wall3,
    "4": wall4,
    "5": wall5,
}

hand = pygame.image.load('./player.png')

enemies = [
    {"x": 100, "y": 200, "texture": pygame.image.load("./sprite2.png")},
    {"x": 280, "y": 190, "texture": pygame.image.load("./sprite3.png")},
    {"x": 225, "y": 50, "texture": pygame.image.load("./sprite4.png")},
    {"x": 220, "y": 425, "texture": pygame.image.load("./sprite1.png")},
    {"x": 320, "y": 420, "texture": pygame.image.load("./sprite2.png")},
]


class Raycaster(object):
    def __init__(self, screen):
        _, _, self.width, self.height = screen.get_rect()
        self.screen = screen
        self.blocksize = 50
        self.player = {
            "x": self.blocksize + 20,
            "y": self.blocksize + 20,
            "a": pi / 3,
            "fov": pi / 3,
        }
        self.map = []
        self.zbuffer = [-float("inf") for z in range(0, 500)]
        # self.clear()

    def clear(self):
        for x in range(self.width):
            for y in range(self.height):
                r = int((x / self.width) * 255) if x / self.width < 1 else 1
                g = int((y / self.height) * 255) if y / self.height < 1 else 1
                b = 0
                color = (r, g, b)
                self.point(x, y, color)

    def point(self, x, y, c=None):
        screen.set_at((x, y), c)

    def draw_rectangle(self, x, y, texture):
        for cx in range(x, x + 50):
            for cy in range(y, y + 50):
                tx = int((cx - x) * 128 / 50)
                ty = int((cy - y) * 128 / 50)
                c = texture.get_at((tx, ty))
                self.point(cx, cy, c)

    def draw_player(self, xi, yi, w = 256, h = 256):
        for x in range(xi, xi + w):
            for y in range(yi, yi + h):
                tx = int((x - xi) * 32/w)
                ty = int((y - yi) * 32/h)
                c = hand.get_at((tx, ty))
                if c != (152, 0, 136, 255):
                    self.point(x, y, c)

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def cast_ray(self, a):
        d = 0
        while True:
            x = self.player["x"] + d * cos(a)
            y = self.player["y"] + d * sin(a)

            i = int(x / 50)
            j = int(y / 50)

            if self.map[j][i] != " ":
                hitx = x - i * 50
                hity = y - j * 50

                if 1 < hitx < 49:
                    maxhit = hitx
                else:
                    maxhit = hity

                tx = int(maxhit * 128 / 50)

                return d, self.map[j][i], tx

            self.point(int(x), int(y), (255, 255, 255))

            d += 1

    def draw_stake(self, x, h, texture, tx):
        start = int(250 - h / 2)
        end = int(250 + h / 2)
        for y in range(start, end):
            ty = int(((y - start) * 128) / (end - start))
            c = texture.get_at((tx, ty))
            self.point(x, y, c)

    def draw_sprite(self, sprite):
        sprite_a = atan2(
            sprite["y"] - self.player["y"], sprite["x"] - self.player["x"]
        )  # why atan2? https://stackoverflow.com/a/12011762

        sprite_d = (
            (self.player["x"] - sprite["x"]) ** 2
            + (self.player["y"] - sprite["y"]) ** 2
        ) ** 0.5
        sprite_size = (500 / sprite_d) * 70

        sprite_x = (
            500
            + (sprite_a - self.player["a"]) * 500 / self.player["fov"]
            + 250
            - sprite_size / 2
        )
        sprite_y = 250 - sprite_size / 2

        sprite_x = int(sprite_x)
        sprite_y = int(sprite_y)
        sprite_size = int(sprite_size)

        for x in range(sprite_x, sprite_x + sprite_size):
            for y in range(sprite_y, sprite_y + sprite_size):
                if 500 < x < 1000 and self.zbuffer[x - 500] >= sprite_d:
                    tx = int((x - sprite_x) * 128 / sprite_size)
                    ty = int((y - sprite_y) * 128 / sprite_size)
                    c = sprite["texture"].get_at((tx, ty))
                    if c != (152, 0, 136, 255):
                        self.point(x, y, c)
                        self.zbuffer[x - 500] = sprite_d

    def render(self):
        for x in range(0, 500, 50):
            for y in range(0, 500, 50):
                i = int(x / 50)
                j = int(y / 50)
                if self.map[j][i] != " ":
                    self.draw_rectangle(x, y, textures[self.map[j][i]])

        self.point(self.player["x"], self.player["y"], (255, 255, 255))

        for i in range(0, 500):
            self.point(500, i, (0, 0, 0))
            self.point(501, i, (0, 0, 0))
            self.point(499, i, (0, 0, 0))

        for i in range(0, 500):
            a = self.player["a"] - self.player["fov"] / 2 + self.player["fov"] * i / 500
            d, c, tx = self.cast_ray(a)
            x = 500 + i
            h = 500 / (d * cos(a - self.player["a"])) * 70
            self.draw_stake(x, h, textures[c], tx)
            self.zbuffer[i] = d

        for enemy in enemies:
            self.point(enemy["x"], enemy["y"], (0, 0, 0))
            self.draw_sprite(enemy)

        self.draw_player(1000 - 256 - 128, 500 - 256)


# Main window
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)

# screen.set_alpha(None)
# pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
font = pygame.font.SysFont(pygame.font.get_default_font(), 20)

# Define text for title of game
font_title = pygame.font.Font('freesansbold.ttf', 32)
text_surface_title = font_title.render('Game: Aim at The Führer', True, BLACK) 
text_rect_title = text_surface_title.get_rect()
text_rect_title.center = (500, 150)   # place the centre of the text

# Define text for title of game on exit
font_exit_title = pygame.font.Font('freesansbold.ttf', 32)
text_surface_exit_title = font_exit_title.render('Yes! You killed The Führer', True, BLACK) 
text_rect_exit_title = text_surface_exit_title.get_rect()
text_rect_exit_title.center = (500, 150)   # place the centre of the text


# Define text for subtitle of game
font_subtitle = pygame.font.Font('freesansbold.ttf', 16)
text_surface_subtitle = font_subtitle.render('Press the button', True, BLACK) 
text_rect_subtitle = text_surface_subtitle.get_rect()
text_rect_subtitle.center = (500, 200)   # place the centre of the text


# Raycaster
r = Raycaster(screen)
r.load_map("./level.txt")

# Game
is_running_game = GAME_RUN
game_state = GAME_STATE_INIT

while is_running_game == GAME_RUN:

    if game_state == GAME_STATE_INIT:
        for event in pygame.event.get(): # Player did something
            if event.type == pygame.QUIT: # Player clicked close button
                is_running_game = GAME_OVER
                
        # Get mouse location
        mouse = pygame.mouse.get_pos()
        # Check if mouse is pressed
        click = pygame.mouse.get_pressed()
        # Clear the screen to white
        screen.fill(WHITE)

        # Queue shapes to be drawn        
        # Buttons
        # Green button
        if WIDTH/2-50 < mouse[0] < WIDTH/2+50 and HEIGHT/2 < mouse[1] < HEIGHT/2 + 50:
            pygame.draw.rect(screen, BRIGHT_GREEN, (int(WIDTH/2-50), int(HEIGHT/2), 100, 50))
            game_state = GAME_STATE_RUNNING
        else:
            pygame.draw.rect(screen, GREEN, (int(WIDTH/2-50), int(HEIGHT/2), 100, 50))
            
        # Text
        screen.blit(text_surface_title, text_rect_title)
        screen.blit(text_surface_subtitle, text_rect_subtitle)
        clock.tick(60)

    elif game_state == GAME_STATE_RUNNING:
        clock.tick(60)
        screen.fill((50, 50, 50))
        r.render()

        print(r.player["x"], r.player["y"])

        if r.player["y"] > 375 and r.player["y"] < 500 and r.player["x"] > 250 and r.player["x"] < 350:
            game_state = GAME_STATE_FINISH

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (
                e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE
            ):
                exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a:
                    r.player["a"] -= pi / 10
                elif e.key == pygame.K_d:
                    r.player["a"] += pi / 10

                elif e.key == pygame.K_w:
                    try:
                        r.player["y"] += int(STEP * sin(r.player["a"]) * 10)
                        r.player["x"] += int(STEP * cos(r.player["a"]) * 10)
                    except:
                        r.player["y"] -= int(STEP * sin(r.player["a"]) * 1)
                        r.player["x"] -= int(STEP * cos(r.player["a"]) * 1)

                elif e.key == pygame.K_s:
                    try:
                        r.player["y"] -= int(STEP * sin(r.player["a"]) * 10)
                        r.player["x"] -= int(STEP * cos(r.player["a"]) * 10)
                    except:
                        r.player["y"] += int(STEP * sin(r.player["a"]) * 1)
                        r.player["x"] += int(STEP * cos(r.player["a"]) * 1)

                if e.key == pygame.K_f:
                    if screen.get_flags() and pygame.FULLSCREEN:
                        pygame.display.set_mode((1000, 500))
                    else:
                        pygame.display.set_mode(
                            (1000, 500),
                            pygame.DOUBLEBUF | pygame.HWACCEL | pygame.FULLSCREEN,
                        )

        # FPS count
        frame_time = (
            float(clock.get_time()) / 1000.0
        )  # frame_time is the time this frame has taken, in seconds
        text = font.render("FPS: " + str(clock.get_fps()), False, (255, 255, 0))
        screen.blit(text, text.get_rect(), text.get_rect())
    
        pygame.display.flip()
        clock.tick(60)
    else:
        for event in pygame.event.get(): # Player did something
            if event.type == pygame.QUIT: # Player clicked close button
                is_running_game = GAME_OVER
                
        # Get mouse location
        mouse = pygame.mouse.get_pos()
        # Check if mouse is pressed
        click = pygame.mouse.get_pressed()
        # Clear the screen to white
        screen.fill(WHITE)

        # Queue shapes to be drawn        
        # Buttons
        # Exit button
        if WIDTH/2-50 < mouse[0] < WIDTH/2+50 and HEIGHT/2 < mouse[1] < HEIGHT/2 + 50:
            pygame.draw.rect(screen, BRIGHT_RED, (int(WIDTH/2-50), int(HEIGHT/2), 100, 50))
            is_running_game = GAME_OVER
            game_state = GAME_STATE_FINISH
        else:
            pygame.draw.rect(screen, RED, (int(WIDTH/2-50), int(HEIGHT/2), 100, 50))
       
        # Text
        screen.blit(text_surface_exit_title, text_rect_exit_title)
        screen.blit(text_surface_subtitle, text_rect_subtitle)
        clock.tick(60)

    pygame.display.flip()

pygame.quit()
