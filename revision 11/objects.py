import pygame


class UnderwaterObject:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, offset, light_position, lighting):
        screen_x = self.x - offset[0]
        screen_y = self.y - offset[1]

        dx = self.x - light_position[0]
        dy = self.y - light_position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        visibility = lighting.calculate_visibility(distance)

        visible_color = (*self.color[:3], int(visibility)) 

        object_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        object_surface.fill(visible_color)
        screen.blit(object_surface, (screen_x, screen_y))
