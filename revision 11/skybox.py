# skybox.py

import pygame

class SkyBox:

    #placeholder skybox that renders above waterline
    #for reference, waterline is at world_y = 0


    def __init__(self, image_path, width, height):

        # param image_path: path to sky image (yos)
        # param width: width to scale the sky to match screen / scene
        # param height: height to scale the sky to
 
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.width = width
        self.height = height

    def draw(self, screen, camera_offset, submarine_y):

        #renders the sky image above the waterline (y 0)
        # param screen: the game screen
        # param camera_offset: (offset_x, offset_y) for the camera
        # param submarine_y: the sub's y pos in world coords (to know how high/low camera is)

        offset_x, offset_y = camera_offset

        # sky is drawn in "world space" at y < 0
        # draw sky so its bottom is @ y=0 (the waterline)
        # if camera_offset moves the screen up/down, shift the sky 
        
        sky_screen_x = -offset_x  #align left with camera
        sky_screen_y = -offset_y - self.height  #put bottom of the sky @ world_y=0

        #if i want parallax thing, i could add a fraction of offset_y (code below - remember)
        
        #sky_screen_y = -0.5 * offset_y - self.height

        screen.blit(self.image, (sky_screen_x, sky_screen_y))
