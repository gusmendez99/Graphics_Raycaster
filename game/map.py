# For accelerated math calculations via numba
from numba.core import types
from numba.typed import Dict
from numba import int32

from game.configuration import *
import pygame

MATRIX_MAP = []
MINIMAP = set()
WORLD_WALLS = []

with open(MAP_FILENAME) as file:
    for line in file.readlines():
        MATRIX_MAP.append([int32(x) if x != ' ' else False for x in list(line.replace("\n", ""))])

WORLD_WIDTH, WORLD_HEIGHT = max([len(i) for i in MATRIX_MAP]) * TILE, len(MATRIX_MAP) * TILE
WORLD_MAP = Dict.empty(key_type=types.UniTuple(int32, 2), value_type=int32)

for y, row in enumerate(MATRIX_MAP):
    for x, char in enumerate(row):
        if char:
            MINIMAP.add((x * MAP_TILE, y * MAP_TILE))
            WORLD_WALLS.append(pygame.Rect(y * TILE, y * TILE, TILE, TILE))
            if char == 1:
                WORLD_MAP[(x * TILE, y * TILE)] = 1
            elif char == 2:
                WORLD_MAP[(x * TILE, y * TILE)] = 2
            elif char == 3:
                WORLD_MAP[(x * TILE, y * TILE)] = 3
            elif char == 4:
                WORLD_MAP[(x * TILE, y * TILE)] = 4