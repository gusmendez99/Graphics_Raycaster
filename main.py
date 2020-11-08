from game.player import Player
from game.sprite import *
from game.raycaster import ray_casting_walls
from game.ui import UI
from game.logic import Logic

# initializing game
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
clock = pygame.time.Clock()

# game objects
screen_map = pygame.Surface(MAP_RESOLUTION)
sprites = SpriteSet()
player = Player(sprites)
ui = UI(screen, screen_map, player, clock)
logic = Logic(player, sprites, ui)

# displaying initial screen
ui.menu()
pygame.mouse.set_visible(False)
ui.play_music()

while True:
    player.movement()
    ui.background()
    walls, wall_shot = ray_casting_walls(player, ui.textures)

    # UI items
    ui.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])
    ui.fps(clock)
    ui.mini_map()
    ui.player_weapon([wall_shot, sprites.sprite_shot])
    # Game Logic
    logic.interaction_objects()
    logic.enemy_action()
    logic.clear_world()
    logic.check_win()

    # Screen refresh
    pygame.display.flip()
    clock.tick()
