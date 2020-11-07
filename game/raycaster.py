import pygame
from game.config import *
from game.map import WORLD_MAP, WORLD_WIDTH, WORLD_HEIGHT
from numba import njit


@njit(fastmath=True, cache=True)
def mapping(a, b):
    return int((a // TILE) * TILE), int((b // TILE) * TILE)

@njit(fastmath=True, cache=True)
def ray_casting(player_pos, player_angle, world_map):
    casted_walls = []
    ox, oy = player_pos
    xm, ym = mapping(ox, oy)
    current_angle = player_angle - HALF_FOV
    texture_v, texture_h = 1, 1
    for ray in range(NUM_RAYS):
        sin_a = math.sin(current_angle)
        cos_a = math.cos(current_angle)

        # verticals
        x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1)
        for i in range(0, WORLD_WIDTH, TILE):
            depth_v = (x - ox) / cos_a
            yv = oy + depth_v * sin_a
            tile_v = mapping(x + dx, yv)
            if tile_v in world_map:
                texture_v = world_map[tile_v]
                break
            x += dx * TILE

        # horizontals
        y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1)
        for i in range(0, WORLD_HEIGHT, TILE):
            depth_h = (y - oy) / sin_a
            xh = ox + depth_h * cos_a
            tile_h = mapping(xh, y + dy)
            if tile_h in world_map:
                texture_h = world_map[tile_h]
                break
            y += dy * TILE

        # projection
        depth, offset, texture = (depth_v, yv, texture_v) if depth_v < depth_h else (depth_h, xh, texture_h)
        offset = int(offset) % TILE
        depth *= math.cos(player_angle - current_angle)
        depth = max(depth, 0.00001)
        projection_height = int(PROJECTION_COEFFICIENT / depth)

        # wall casting
        casted_walls.append((depth, offset, projection_height, texture))
        current_angle += DELTA_ANGLE
        
    return casted_walls


def ray_casting_walls(player, textures):
    walls = []
    casted_walls = ray_casting(player.position, player.angle, WORLD_MAP)
    wall_shot = casted_walls[CENTER_RAY][0], casted_walls[CENTER_RAY][2]
    
    for ray, casted_values in enumerate(casted_walls):
        depth, offset, projection_height, texture = casted_values
        if projection_height > HEIGHT:
            texture_height = TEXTURE_HEIGHT / (projection_height / HEIGHT)
            wall_column = textures[texture].subsurface(offset * TEXTURE_SCALE,
                                                       HALF_TEXTURE_HEIGHT - texture_height // 2,
                                                       TEXTURE_SCALE, texture_height)
            wall_column = pygame.transform.scale(wall_column, (SCALE, HEIGHT))
            wall_position = (ray * SCALE, 0)
        else:
            wall_column = textures[texture].subsurface(offset * TEXTURE_SCALE, 0, TEXTURE_SCALE, TEXTURE_HEIGHT)
            wall_column = pygame.transform.scale(wall_column, (SCALE, projection_height))
            wall_position = (ray * SCALE, HALF_HEIGHT - projection_height // 2)

        walls.append((depth, wall_column, wall_position))
    return walls, wall_shot