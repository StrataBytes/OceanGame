import pygame
import sys
from settings import *
from player import Submarine
from lighting import Lighting
from debug_menu import DebugMenu
from seabed_generator import SeabedGenerator
from objects import UnderwaterObject
from hud import HUD
from cave_generator import CaveGenerator
from skybox import SkyBox
from enemy import Enemy
from underwater_terrain import UnderwaterTerrain
from menus import main_menu

class SurfaceOverlay:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        self.overlay = None

    def generate_overlay(self):
        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.overlay.fill(self.color)

    def draw(self, screen, y_offset):
        if self.overlay is None:
            self.generate_overlay()
        screen.blit(self.overlay, (0, -y_offset))


def get_overlay_alpha(depth, min_depth=400, max_depth=1500):
    if depth <= min_depth:
        return 0
    elif depth >= max_depth:
        return 255
    else:
        ratio = (depth - min_depth) / (max_depth - min_depth)
        return int(255 * ratio)


def game_loop(actual_screen):
    clock = pygame.time.Clock()

    render_surface = pygame.Surface((WIDTH, HEIGHT))
    submarine = Submarine(0, 0)
    hud = HUD(submarine, HUD_CONFIG, HEIGHT)
    debug_menu = DebugMenu()

    #init terrain
    terrain = UnderwaterTerrain(
        scale=1000,
        threshold=0.4,
        amplitude=150,
        chunk_size=800,
        grid_size=5,
        seed=42
    )

    seabed = SeabedGenerator(scale=600, amplitude=1000, base_level=3000)
    seabed.points = [(x, seabed.get_height(x)) for x in range(0, WIDTH)]
    surface_overlay = SurfaceOverlay(WIDTH, 5, (135, 206, 250))
    light = Lighting(300, darkness_factor=2.0)

    skybox = SkyBox("assets/images/bg.PNG", WIDTH, 400)

    objects = [
        UnderwaterObject(300, 300, 50, 50, (100, 100, 100)),
        UnderwaterObject(800, 600, 60, 40, (120, 80, 60)),
        UnderwaterObject(-200, 500, 70, 70, (50, 150, 200)),
    ]

    enemies = [
        Enemy(400, 500, 40, 40, speed=2, chase_radius=300),
        Enemy(700, 200, 40, 40, speed=3, chase_radius=250)
    ]

    settings = {"lighting": True, "speed": SUB_SPEED}

    window_width, window_height = actual_screen.get_size()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                window_width, window_height = event.w, event.h
                actual_screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F8:
                    debug_menu.toggle()
                elif event.key == pygame.K_F9:
                    result = main_menu(render_surface)
                    if result == "quit":
                        pygame.quit()
                        sys.exit()
                debug_menu.handle_event(event, submarine, settings, seabed, light)

        seabed_depth = max([height for _, height in seabed.points])
        submarine.speed = settings["speed"]
        submarine.update(seabed_depth)

        #camera position is based on the submarine
        camera_x = submarine.x
        camera_y = submarine.y
        camera_offset = (camera_x - WIDTH // 2, camera_y - HEIGHT // 2)

        #update chunks based on the camera position
        terrain.update_chunks((camera_x, camera_y))

        #draw everything to the fixed-size render surface
        render_surface.fill(BG_COLOR)
        skybox.draw(render_surface, camera_offset, submarine.y)
        terrain.draw(render_surface, camera_offset)
        seabed.draw(render_surface, camera_offset, cell_size=8)
        submarine.draw(render_surface, camera_offset)
        surface_overlay.draw(render_surface, camera_offset[1])

        for enemy in enemies:
            enemy.update(submarine, camera_offset)
            enemy.draw(render_surface, camera_offset)

        for obj in objects:
            obj.draw(
                render_surface,
                camera_offset,
                (submarine.x + submarine.width // 2, submarine.y + submarine.height // 2),
                light
            )

        if settings["lighting"]:
            light_x = submarine.x + submarine.width // 2
            light_y = submarine.y + submarine.height // 2
            screen_light_x = light_x - camera_offset[0]
            screen_light_y = light_y - camera_offset[1]
            overlay_alpha = get_overlay_alpha(submarine.y, min_depth=400, max_depth=1500)
            light.draw(render_surface, (screen_light_x, screen_light_y), overlay_alpha=overlay_alpha)

        for enemy in enemies:
            enemy.check_collision(submarine)

        hud.draw(render_surface)
        debug_menu.draw(render_surface, submarine, settings, light)

        #scale render surface while keeping aspect ratio
        scale = min(window_width / WIDTH, window_height / HEIGHT)
        scaled_width = int(WIDTH * scale)
        scaled_height = int(HEIGHT * scale)
        scaled_surface = pygame.transform.scale(render_surface, (scaled_width, scaled_height))

        #center the scaled surface on the actual screen
        x_offset = (window_width - scaled_width) // 2
        y_offset = (window_height - scaled_height) // 2

        #fill the screen with black, then draw centered scaled surface
        actual_screen.fill((0, 0, 0))
        actual_screen.blit(scaled_surface, (x_offset, y_offset))

        pygame.display.flip()
        clock.tick(FPS)




if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    pygame.display.set_caption("Ocean Game")

    while True:
        result = main_menu(screen)
        if result == "start":
            game_loop(screen)
        elif result == "quit":
            pygame.quit()
            sys.exit()
