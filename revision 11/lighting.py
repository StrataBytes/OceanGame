import pygame

class Lighting:
    def __init__(self, radius, darkness_factor=1.0):

        # param radius: base radius of the spotlight
        # param darkness_factor: ctrls both the fade steepness and spotlight width

        self.base_radius = radius
        self.darkness_factor = darkness_factor
        self.overlay = None
        self.current_radius = radius

    def generate_overlay(self):
        #gen a new radial gradient overlay.
        #adj spotlight radius based on darkness_factor
        self.current_radius = int(self.base_radius * (1 + (self.darkness_factor - 1) * 0.5))

        gradient = pygame.Surface((self.current_radius * 2, self.current_radius * 2), pygame.SRCALPHA)
        center = (self.current_radius, self.current_radius)

        for r in range(self.current_radius, 0, -1):
            #calc alpha value based on distance and darkness factor
            alpha = int(255 * ((self.current_radius - r) / self.current_radius) ** self.darkness_factor)
            pygame.draw.circle(gradient, (0, 0, 0, alpha), center, r)

        self.overlay = gradient

    def draw(self, screen, light_position, overlay_alpha=255):

        #draw lighting overlay with a spotlight effect, faded by overlay_alpha.
        # param screen: The main game screen.
        # param light_position: (x,y) center of the light in screen coordinates.
        # param overlay_alpha: Overall opacity of the entire overlay [0..255].

        #if alpha is 0 or less, skip drawing lol
        if overlay_alpha <= 0:
            return

        #regen overlay if needed
        expected_radius = self.base_radius * (1 + (self.darkness_factor - 1) * 0.5)
        if self.overlay is None or self.current_radius != int(expected_radius):
            self.generate_overlay()

        #create shadow surface covering entire screen
        shadow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        #fill it with black using overlay_alpha as overall opacity
        shadow_surface.fill((0, 0, 0, overlay_alpha))

        #'punch out' the radial spotlight using BLEND_RGBA_SUB
        shadow_surface.blit(
            self.overlay,
            (light_position[0] - self.current_radius, light_position[1] - self.current_radius),
            special_flags=pygame.BLEND_RGBA_SUB
        )

        #blend the shadow surface onto the main screen
        screen.blit(shadow_surface, (0, 0))

    def calculate_visibility(self, distance):

        #calculate visibility (0..255) based on distance from the light source
        #this is used by objects to modulate their own alpha (refer to docs if u forgor wth that means)

        if distance > self.current_radius:
            return 0  #fully dark if beyond the spotlight
        visibility = max(0, 255 * ((self.current_radius - distance) / self.current_radius) ** self.darkness_factor)
        return visibility
