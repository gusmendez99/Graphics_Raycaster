import math
import pygame

# Acceleration
from numba import njit

from game.config import *
from game.map import WORLD_MAP
from game.raycaster import mapping


class Logic:
    def __init__(self, player, sprites, ui):
        self.player = player
        self.sprites = sprites
        self.ui = ui
        self.pain_sound = pygame.mixer.Sound("./game/sound/pain.wav")

    def interaction_objects(self):
        if self.player.shot and self.ui.shot_animation_trigger:
            for obj in sorted(
                self.sprites.list_of_objects, key=lambda obj: obj.distance_to_sprite
            ):
                if obj.is_on_fire[1]:
                    if obj.is_dead != "immortal" and not obj.is_dead:
                        if ray_casting_enemy_player(
                            obj.x,
                            obj.y,
                            self.sprites.blocked_doors,
                            WORLD_MAP,
                            self.player.position,
                        ):
                            if obj.flag == "enemy":
                                self.pain_sound.play()
                            obj.is_dead = True
                            obj.blocked = None
                            self.ui.shot_animation_trigger = False
                    if (
                        obj.flag == "door_h" or obj.flag == "door_v"
                    ) and obj.distance_to_sprite < TILE:
                        obj.door_open_trigger = True
                        obj.blocked = None
                    break

    def enemy_action(self):
        for obj in self.sprites.list_of_objects:
            if obj.flag == "enemy" and not obj.is_dead:
                if ray_casting_enemy_player(
                    obj.x,
                    obj.y,
                    self.sprites.blocked_doors,
                    WORLD_MAP,
                    self.player.position,
                ):
                    obj.enemy_action_trigger = True
                    self.enemy_move(obj)
                else:
                    obj.enemy_action_trigger = False

    def enemy_move(self, obj):
        if abs(obj.distance_to_sprite) > TILE:
            dx = obj.x - self.player.position[0]
            dy = obj.y - self.player.position[1]
            obj.x = obj.x + 1 if dx < 0 else obj.x - 1
            obj.y = obj.y + 1 if dy < 0 else obj.y - 1

    def clear_world(self):
        deleted_objects = self.sprites.list_of_objects[:]
        [
            self.sprites.list_of_objects.remove(obj)
            for obj in deleted_objects
            if obj.delete
        ]

    def check_win(self):
        if not len(
            [
                obj
                for obj in self.sprites.list_of_objects
                if obj.flag == "enemy" and not obj.is_dead
            ]
        ):
            pygame.mixer.music.stop()
            pygame.mixer.music.load("./game/sound/win.wav")
            pygame.mixer.music.play()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                self.ui.win()


@njit(fastmath=True, cache=True)
def ray_casting_enemy_player(
    enemy_x, enemy_y, blocked_doors, world_map, player_position
):
    ox, oy = player_position
    xm, ym = mapping(ox, oy)
    delta_x, delta_y = ox - enemy_x, oy - enemy_y
    angle = math.atan2(delta_y, delta_x)
    angle += math.pi

    # ray casting
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)

    # verticals
    x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1)
    for i in range(int(abs(delta_x) // TILE)):
        depth_v = (x - ox) / cos_a
        yv = oy + depth_v * sin_a
        tile_v = mapping(x + dx, yv)
        if tile_v in world_map or tile_v in blocked_doors:
            return False
        x += dx * TILE

    # horizontals
    y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1)
    for i in range(int(abs(delta_y) // TILE)):
        depth_h = (y - oy) / sin_a
        xh = ox + depth_h * cos_a
        tile_h = mapping(xh, y + dy)
        if tile_h in world_map or tile_h in blocked_doors:
            return False
        y += dy * TILE

    return True
