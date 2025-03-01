import pygame
import noise
from settings import WIDTH, HEIGHT
from cave_generator import CaveGenerator
import random


class SeabedGenerator:
    def __init__(self, scale, amplitude, base_level=None, seed=None):
        self.scale = scale
        self.amplitude = amplitude
        self.base_level = base_level if base_level is not None else 3000#min depthj
        self.seed = seed if seed is not None else 42
        self.caves = []
        self.points = []


    # def get_height(self, x):
    #     nx = x / self.scale
    #     height = noise.pnoise1(nx, octaves=4, persistence=0.5, lacunarity=2.0, base=self.seed)
    #     height = height * self.amplitude + self.base_level
    #     return int(height)


    def get_height(self, x):
        nx = x / self.scale
        # Generate height using noise
        height = noise.pnoise1(nx, octaves=4, persistence=0.5, lacunarity=2.0, base=self.seed)
        height = height * self.amplitude + self.base_level
        return int(height)



    def generate_caves(self, chance, cave_width, cave_height):
        #make caves at low points
        self.caves = []

        #find low points
        low_points = self.find_low_points(check_range=10, depth_threshold=10)

        # low_points = self.find_low_points(check_range=10, depth_threshold=50)
        print(f"Found {len(low_points)} low points.")


        for x, height in low_points:
            if random.randint(0, 100) < chance:
                print(f"Generating cave at low point ({x}, {height})")
                cave = CaveGenerator(cave_width, cave_height, fill_percentage=45, smooth_iterations=3)
                cave.initialize_grid()
                cave.smooth_cave()
                self.caves.append((x, height, cave))



    def find_low_points(self, check_range=10, depth_threshold=50):
        #find low points in the seabed by comparing each point to its neighbors

        low_points = []

        for x in range(check_range, WIDTH - check_range, check_range):
            #get the height @ the current point
            current_height = self.get_height(x)

            #average height of neighboring points
            neighbor_heights = [
                self.get_height(x + offset) for offset in range(-check_range, check_range + 1) if offset != 0
            ]
            avg_neighbor_height = sum(neighbor_heights) / len(neighbor_heights)

            #if current height is significantly lower than neighbors, mark it as a low point
            if avg_neighbor_height - current_height > depth_threshold:
                low_points.append((x, current_height))

        return low_points



    def draw(self, screen, offset, cell_size):
        start_x = int(offset[0])
        end_x = start_x + WIDTH

        screen_points = []
        self.points = []
        for world_x in range(start_x, end_x):
            height = self.get_height(world_x)
            self.points.append((world_x, height))
            screen_x = world_x - offset[0]
            screen_y = height - offset[1]
            screen_points.append((screen_x, screen_y))

        if screen_points:
            seabed_fill_polygon = screen_points.copy()
            seabed_fill_polygon.append((WIDTH, HEIGHT))
            seabed_fill_polygon.append((0, HEIGHT))
            pygame.draw.polygon(screen, (50, 100, 200), seabed_fill_polygon)

        for cave_x, cave_y, cave in self.caves:
            cave_offset_x = (cave_x - offset[0]) // cell_size
            cave_offset_y = (cave_y - offset[1]) // cell_size
            cave.draw(screen, cell_size, offset=(cave_offset_x, cave_offset_y))

        low_points = self.find_low_points()
        for x, height in low_points:
            screen_x = x - offset[0]
            screen_y = height - offset[1]
            pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), 5)
