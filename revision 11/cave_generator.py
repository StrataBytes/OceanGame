import random
import pygame

class CaveGenerator:
    def __init__(self, width, height, fill_percentage, smooth_iterations):
        self.width = width
        self.height = height
        self.fill_percentage = fill_percentage
        self.smooth_iterations = smooth_iterations
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def initialize_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                #walls at edges
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    self.grid[y][x] = 1
                else:
                    self.grid[y][x] = 1 if random.randint(0, 100) < self.fill_percentage else 0

    def smooth_cave(self):
        for _ in range(self.smooth_iterations):
            new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
            for y in range(self.height):
                for x in range(self.width):
                    wall_count = self.count_neighbors(x, y)
                    #wall
                    if self.grid[y][x] == 1:
                        new_grid[y][x] = 1 if wall_count >= 4 else 0
                    else:
                        #space
                        new_grid[y][x] = 1 if wall_count >= 5 else 0
            self.grid = new_grid

    def count_neighbors(self, x, y):
        #num of wall neighbor
        count = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= self.width or ny >= self.height:
                    count += 1 
                elif self.grid[ny][nx] == 1:
                    count += 1
        return count

    def draw(self, screen, cell_size, offset=(0, 0)):
        for y in range(self.height):
            for x in range(self.width):
                world_x = x + offset[0]
                world_y = y + offset[1]
                color = (50, 50, 50) if self.grid[y][x] == 1 else (200, 200, 200)
                pygame.draw.rect(screen, color, (world_x * cell_size, world_y * cell_size, cell_size, cell_size))
