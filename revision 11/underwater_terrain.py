import pygame
from noise import snoise2
import threading
from queue import Queue
import math
import random

class UnderwaterTerrain:
    def __init__(self, scale, threshold, amplitude, chunk_size, grid_size, seed=None):
        self.scale = scale
        self.threshold = threshold
        self.amplitude = amplitude
        self.chunk_size = chunk_size
        #num of chunks in each direction
        self.grid_size = grid_size  
        self.seed = seed if seed else 42

        # grid of chunks
        self.chunk_grid = {}
        #queue for threaded chunk generation
        self.chunk_queue = Queue() 
        self.generate_thread = threading.Thread(target=self._process_chunk_queue, daemon=True)
        self.generate_thread.start()

        #init the grid
        self.initialize_chunk_grid()

    def initialize_chunk_grid(self):
    #grid around 0,0    
        print("Initializing chunk grid...")
        half_grid = self.grid_size // 2
        for gx in range(-half_grid, half_grid + 1):
            for gy in range(-half_grid, half_grid + 1):
                chunk_key = (gx * self.chunk_size, gy * self.chunk_size)
                #empty chunk at firstm then add to generation queue
                self.chunk_grid[chunk_key] = []  
                self.chunk_queue.put(chunk_key)  

    def _process_chunk_queue(self):
    #constantly process chunk gen in a different thread
        while True:
            chunk_key = self.chunk_queue.get()
            self.chunk_grid[chunk_key] = self.generate_chunk(chunk_key)
            self.chunk_queue.task_done()

    def generate_chunk(self, chunk_key):

        #gen features for a single chunk based on key (world pos)
        #no features are gen. above y 250
        #pre-bakes overlapping 'fringe' circl for smoothing terrain

        features = []
        chunk_x, chunk_y = chunk_key
        #offset to keep coordinates positive, bc simplex flips tf out if negative
        noise_offset = 10_000_000 

        for x in range(chunk_x, chunk_x + self.chunk_size, 20):
            for y in range(chunk_y, chunk_y + self.chunk_size, 20):
                #skip feature above y 250
                if y < 250:
                    continue

                nx = (x + noise_offset) / self.scale
                ny = (y + noise_offset) / self.scale
                noise_value = snoise2(nx, ny, octaves=4, base=self.seed)

                if noise_value > self.threshold:
                    #pre-bake overlapping frnge circles
                    main_radius = self.amplitude // 10
                    fringe_circles = []
                    #every 30 degrees - place fringe circles
                    for angle in range(0, 360, 30):
                        #close range
                        distance = random.uniform(main_radius * 0.7, main_radius * 1.2)
                        fringe_radius = random.randint(main_radius // 2, main_radius * 3 // 4)
                        offset_x = int(distance * math.cos(math.radians(angle)))
                        offset_y = int(distance * math.sin(math.radians(angle)))
                        fringe_circles.append((x + offset_x, y + offset_y, fringe_radius))

                    features.append({"main": (x, y, main_radius), "fringe": fringe_circles})

        return features



    def update_chunks(self, camera_pos):

        #re-pos and regen. chunks based on the players pos

        camera_x, camera_y = camera_pos
        half_grid = self.grid_size // 2

        #calc the center chunk based on the camera pos
        center_chunk_x = (camera_x // self.chunk_size) * self.chunk_size
        center_chunk_y = (camera_y // self.chunk_size) * self.chunk_size

        #reuse chunks in grid
        new_chunk_grid = {}
        for gx in range(-half_grid, half_grid + 1):
            for gy in range(-half_grid, half_grid + 1):
                target_chunk = (center_chunk_x + gx * self.chunk_size, center_chunk_y + gy * self.chunk_size)

                if target_chunk in self.chunk_grid:
                    #keep the existing chunk
                    new_chunk_grid[target_chunk] = self.chunk_grid[target_chunk]
                else:
                    #gen a new chunk, keep new_chunk_grid empty on start
                    new_chunk_grid[target_chunk] = []
                    self.chunk_queue.put(target_chunk)

        self.chunk_grid = new_chunk_grid





    def draw(self, screen, offset):
 
        #draw all visible chunks on the screen, 2 make sure circles are partially rendered if partially on-screen cuz they were disapearing
        #using pre-baked fringe circles w/ solid colors for terrain smoothing

        screen_rect = pygame.Rect(0, 0, screen.get_width(), screen.get_height())

        for chunk_key, features in self.chunk_grid.items():
            for feature in features:
                #draw main circ
                main_x, main_y, main_radius = feature["main"]
                screen_x = main_x - offset[0]
                screen_y = main_y - offset[1]
                circle_rect = pygame.Rect(
                    screen_x - main_radius,
                    screen_y - main_radius,
                    main_radius * 2,
                    main_radius * 2,
                )

                #main circ overlaps screen?
                if screen_rect.colliderect(circle_rect):
                    pygame.draw.circle(screen, (100, 80, 50), (screen_x, screen_y), main_radius)

                    #dra pre-baked fringe circ
                    for fringe_x, fringe_y, fringe_radius in feature["fringe"]:
                        screen_fringe_x = fringe_x - offset[0]
                        screen_fringe_y = fringe_y - offset[1]
                        fringe_circle_rect = pygame.Rect(
                            screen_fringe_x - fringe_radius,
                            screen_fringe_y - fringe_radius,
                            fringe_radius * 2,
                            fringe_radius * 2,
                        )
                        if screen_rect.colliderect(fringe_circle_rect):
                            #draw em on scrn
                            pygame.draw.circle(screen, (100, 80, 50), (screen_fringe_x, screen_fringe_y), fringe_radius)
