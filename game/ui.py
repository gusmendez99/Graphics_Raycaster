import pygame
import sys
from collections import deque
from random import randrange

from game.config import *
from game.map import MINIMAP


class UI:
    def __init__(self, screen, screen_map, player, clock):
        self.screen = screen
        self.screen_map = screen_map
        self.player = player
        self.clock = clock
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_win = pygame.font.Font("./game/font/main-font.ttf", 144)
        self.textures = {
            1: pygame.image.load("./game/textures/wall1.png").convert(),
            2: pygame.image.load("./game/textures/wall2.png").convert(),
            3: pygame.image.load("./game/textures/wall3.png").convert(),
            4: pygame.image.load("./game/textures/wall4.png").convert(),
            "S": pygame.image.load("./game/textures/sky.png").convert(),
        }

        # hud
        self.hud = pygame.image.load("./game/textures/hud.png").convert_alpha()
        # menu
        self.menu_trigger = True
        self.menu_picture = pygame.image.load(
            "./game/textures/background.jpg"
        ).convert()
        # weapon parameters
        self.weapon_base_sprite = pygame.image.load(
            "./game/sprites/weapons/shotgun/base/0.png"
        ).convert_alpha()
        self.weapon_shot_animation = deque(
            [
                pygame.image.load(
                    f"./game/sprites/weapons/shotgun/shot/{i}.png"
                ).convert_alpha()
                for i in range(20)
            ]
        )
        self.weapon_rect = self.weapon_base_sprite.get_rect()
        self.weapon_pos = (
            HALF_WIDTH - self.weapon_rect.width // 2,
            HEIGHT - self.weapon_rect.height,
        )
        self.shot_length = len(self.weapon_shot_animation)
        self.shot_length_count = 0
        self.shot_animation_trigger = True
        self.shot_animation_speed = 3
        self.shot_animation_count = 0
        self.shot_sound = pygame.mixer.Sound("./game/sound/shotgun.wav")
        # shot SFX
        self.sfx = deque(
            [
                pygame.image.load(f"./game/sprites/weapons/sfx/{i}.png").convert_alpha()
                for i in range(9)
            ]
        )
        self.sfx_length_count = 0
        self.sfx_length = len(self.sfx)

    def background(self):
        sky_offset = -10 * math.degrees(self.player.angle) % WIDTH
        self.screen.blit(self.textures["S"], (sky_offset, 0))
        self.screen.blit(self.textures["S"], (sky_offset - WIDTH, 0))
        self.screen.blit(self.textures["S"], (sky_offset + WIDTH, 0))
        pygame.draw.rect(self.screen, DARKGRAY, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    def world(self, world_objects):
        for obj in sorted(world_objects, key=lambda n: n[0], reverse=True):
            if obj[0]:
                _, object, object_pos = obj
                self.screen.blit(object, object_pos)

    def fps(self, clock):
        display_fps = "FPS:" + str(int(clock.get_fps()))
        render = self.font.render(display_fps, 0, DARKORANGE)
        self.screen.blit(render, FPS_POSITION)

    def play_music(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.mixer.music.load("./game/sound/theme.wav")
        pygame.mixer.music.play(10)

    def win(self):
        render = self.font_win.render("YOU WIN!!!", 1, (randrange(40, 120), 0, 0))
        rect = pygame.Rect(0, 0, 1000, 300)
        rect.center = HALF_WIDTH, HALF_HEIGHT
        pygame.draw.rect(self.screen, BLACK, rect, border_radius=50)
        self.screen.blit(render, (rect.centerx - 430, rect.centery - 140))
        pygame.display.flip()
        self.clock.tick(15)

    def mini_map(self):
        self.screen_map.fill(BLACK)
        map_x, map_y = self.player.x // MAP_SCALE, self.player.y // MAP_SCALE
        pygame.draw.line(
            self.screen_map,
            YELLOW,
            (map_x, map_y),
            (
                map_x + 8 * math.cos(self.player.angle),
                map_y + 8 * math.sin(self.player.angle),
            ),
            2,
        )
        pygame.draw.circle(self.screen_map, RED, (int(map_x), int(map_y)), 4)
        for x, y in MINIMAP:
            pygame.draw.rect(self.screen_map, DARKBROWN, (x, y, MAP_TILE, MAP_TILE))
        self.screen.blit(self.screen_map, MAP_POSITION)

    def player_weapon(self, shot_projections):
        if self.player.shot:
            if not self.shot_length_count:
                self.shot_sound.play()
            self.shot_projection = min(shot_projections)[1] // 2
            self.bullet_sfx()
            shot_sprite = self.weapon_shot_animation[0]
            self.screen.blit(shot_sprite, self.weapon_pos)
            self.shot_animation_count += 1
            if self.shot_animation_count == self.shot_animation_speed:
                self.weapon_shot_animation.rotate(-1)
                self.shot_animation_count = 0
                self.shot_length_count += 1
                self.shot_animation_trigger = False
            if self.shot_length_count == self.shot_length:
                self.player.shot = False
                # self.shot_animation_count = 0
                self.shot_length_count = 0
                self.sfx_length_count = 0
                self.shot_animation_trigger = True
        else:
            self.screen.blit(self.weapon_base_sprite, self.weapon_pos)

        # hud
        self.screen.blit(self.hud, HUD_POSITION)

    def bullet_sfx(self):
        if self.sfx_length_count < self.sfx_length:
            sfx = pygame.transform.scale(
                self.sfx[0], (self.shot_projection, self.shot_projection)
            )
            sfx_rect = sfx.get_rect()
            self.screen.blit(
                sfx,
                (HALF_WIDTH - sfx_rect.width // 2, HALF_HEIGHT - sfx_rect.height // 2),
            )
            self.sfx_length_count += 1
            self.sfx.rotate(-1)

    def menu(self):
        x = 0
        pygame.mixer.music.load("./game/sound/win.wav")
        pygame.mixer.music.play()
        button_font = pygame.font.Font("./game/font/main-font.ttf", 72)
        label_font = pygame.font.Font("./game/font/secondary-font.otf", 400)
        start = button_font.render("START", 1, pygame.Color("lightgray"))
        button_start = pygame.Rect(0, 0, 400, 150)
        button_start.center = HALF_WIDTH, HALF_HEIGHT
        exit = button_font.render("EXIT", 1, pygame.Color("lightgray"))
        button_exit = pygame.Rect(0, 0, 400, 150)
        button_exit.center = HALF_WIDTH, HALF_HEIGHT + 200

        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.blit(
                self.menu_picture, (0, 0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT)
            )
            x += 1

            pygame.draw.rect(
                self.screen, BLACK, button_start, border_radius=25, width=10
            )
            self.screen.blit(
                start, (button_start.centerx - 130, button_start.centery - 70)
            )

            pygame.draw.rect(
                self.screen, BLACK, button_exit, border_radius=25, width=10
            )
            self.screen.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))

            color = randrange(40)
            label = label_font.render("DOOM", 1, (color, color, color))
            self.screen.blit(label, (60, -30))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if button_start.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_start, border_radius=25)
                self.screen.blit(
                    start, (button_start.centerx - 130, button_start.centery - 70)
                )
                if mouse_click[0]:
                    self.menu_trigger = False
            elif button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_exit, border_radius=25)
                self.screen.blit(
                    exit, (button_exit.centerx - 85, button_exit.centery - 70)
                )
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            self.clock.tick(20)
