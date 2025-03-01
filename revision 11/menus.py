import pygame
import random
import sys
from settings import WIDTH, HEIGHT, FPS

# Define colors
DARK_BLUE = (10, 25, 50)
LIGHT_BLUE = (80, 180, 255)
GLOW_BLUE = (30, 144, 255)
WHITE = (255, 255, 255)

# Animation settings
GLOW_INCREMENT = 2
GLOW_MIN = 100
GLOW_MAX = 200
BREATHING_SPEED = 1  # Controls the speed of the breathing effect

menu_option = ["Start Game", "Options", "Quit"]


def render_with_letterbox(render_surface, actual_screen, target_resolution):
    """Scale and center the render_surface within actual_screen while preserving aspect ratio."""
    window_width, window_height = actual_screen.get_size()
    scale = min(window_width / target_resolution[0], window_height / target_resolution[1])
    scaled_width = int(target_resolution[0] * scale)
    scaled_height = int(target_resolution[1] * scale)
    scaled_surface = pygame.transform.smoothscale(render_surface, (scaled_width, scaled_height))  # Use smooth scaling
    x_offset = (window_width - scaled_width) // 2
    y_offset = (window_height - scaled_height) // 2

    # Fill screen with black and blit the scaled surface
    actual_screen.fill((0, 0, 0))
    actual_screen.blit(scaled_surface, (x_offset, y_offset))
    pygame.display.flip()



def map_mouse_to_surface(mouse_pos, actual_screen, render_surface):
    """Map the mouse position from the actual screen to the render_surface."""
    window_width, window_height = actual_screen.get_size()
    scale = min(window_width / WIDTH, window_height / HEIGHT)
    scaled_width = int(WIDTH * scale)
    scaled_height = int(HEIGHT * scale)
    x_offset = (window_width - scaled_width) // 2
    y_offset = (window_height - scaled_height) // 2

    # Convert mouse position to render_surface coordinates
    mapped_x = (mouse_pos[0] - x_offset) / scale
    mapped_y = (mouse_pos[1] - y_offset) / scale
    return mapped_x, mapped_y



class Button:
    def __init__(self, text, x, y, width, height, font, color, hover_color, glow_color):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.glow_color = glow_color
        self.hovered = False
        self.glow_opacity = 0
        self.breathing_in = True  # Tracks breathing direction
        self.text_surface = self.font.render(self.text, True, WHITE)
        self.text_rect = self.text_surface.get_rect(center=(x + width // 2, y + height // 2))

    def draw(self, screen):
        # Breathing effect when hovered
        if self.hovered:
            if self.breathing_in:
                self.glow_opacity += BREATHING_SPEED
                if self.glow_opacity >= GLOW_MAX:
                    self.glow_opacity = GLOW_MAX
                    self.breathing_in = False
            else:
                self.glow_opacity -= BREATHING_SPEED
                if self.glow_opacity <= GLOW_MIN:
                    self.glow_opacity = GLOW_MIN
                    self.breathing_in = True
        else:
            # Smooth fade-out
            self.glow_opacity = max(self.glow_opacity - GLOW_INCREMENT, 0)

        # Draw glowing border
        if self.glow_opacity > 0:
            glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            glow_rect = glow_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            pygame.draw.rect(glow_surface, (*self.glow_color, int(self.glow_opacity)), 
                             glow_surface.get_rect(), border_radius=15, width=10)
            screen.blit(glow_surface, glow_rect.topleft)

        # Draw button
        pygame.draw.rect(screen, self.hover_color if self.hovered else self.color,
                         (self.x, self.y, self.width, self.height), border_radius=15)
        screen.blit(self.text_surface, self.text_rect)

    def check_hover(self, mouse_pos):
        was_hovered = self.hovered
        self.hovered = self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height
        if not was_hovered and self.hovered:
            # Reset breathing state when hover starts
            self.breathing_in = True

    def is_clicked(self, mouse_pos):
        return self.hovered and pygame.mouse.get_pressed()[0]



class FloatingParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(1, 3)
        self.speed = random.uniform(0.1, 0.5)
        self.opacity = random.randint(50, 150)

    def update(self):
        self.y -= self.speed
        if self.y < 0:
            self.y = HEIGHT
            self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (255, 255, 255, self.opacity), (int(self.size), int(self.size)), int(self.size))
        screen.blit(particle_surface, (self.x - self.size, self.y - self.size))
def draw_gradient_background(screen, color1, color2):
    """Draw a vertical gradient background."""
    for y in range(HEIGHT):
        blend_factor = y / HEIGHT
        r = int(color1[0] * (1 - blend_factor) + color2[0] * blend_factor)
        g = int(color1[1] * (1 - blend_factor) + color2[1] * blend_factor)
        b = int(color1[2] * (1 - blend_factor) + color2[2] * blend_factor)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))


class LightRayOverlay:
    def __init__(self):
        self.image = pygame.image.load("assets/images/light_rays.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.opacity = 40  # Set transparency level (0-255)

    def draw(self, screen):
        # Create a surface with adjusted transparency
        light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x in range(0, WIDTH, self.image.get_width()):
            for y in range(0, HEIGHT, self.image.get_height()):
                light_surface.blit(self.image, (x, y))

        # Manually apply transparency
        light_surface.fill((255, 255, 255, self.opacity), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(light_surface, (0, 0))


class Bubble:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + random.randint(0, 200)
        self.radius = random.randint(2, 6)
        self.speed = random.uniform(0.5, 2.0)
        self.opacity = 255

    def update(self):
        self.y -= self.speed
        self.opacity -= self.speed * 2  # Fade out as it rises

    def draw(self, screen):
        if self.opacity > 0:
            bubble_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(bubble_surface, (255, 255, 255, int(self.opacity)),
                               (self.radius, self.radius), self.radius)
            screen.blit(bubble_surface, (self.x - self.radius, self.y - self.radius))


def draw_menu(screen, buttons, bubbles, particles, light_rays):
    # Draw gradient background
    draw_gradient_background(screen, (30, 60, 120), (5, 10, 30))  # Adjusted gradient colors

    # Draw light rays
    light_rays.draw(screen)

    # Update and draw particles
    for particle in particles:
        particle.update()
        particle.draw(screen)

    # Update and draw bubbles
    for bubble in bubbles:
        bubble.update()
        bubble.draw(screen)

    # Remove bubbles that are fully faded or off-screen
    bubbles[:] = [bubble for bubble in bubbles if bubble.opacity > 0 and bubble.y > -bubble.radius]

    # Draw logo
    logo = pygame.image.load("assets/images/logo.png")
    logo_width, logo_height = 400, 300
    logo = pygame.transform.scale(logo, (logo_width, logo_height))
    logo_x = WIDTH // 2 - logo_width // 2
    logo_y = HEIGHT // 4 - logo_height // 2
    screen.blit(logo, (logo_x, logo_y))

    # Draw buttons
    for button in buttons:
        button.draw(screen)

    pygame.display.flip()


def main_menu(actual_screen):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    # Use high-resolution rendering
    target_resolution = actual_screen.get_size()
    render_surface = pygame.Surface(target_resolution)

    # Create buttons
    button_width, button_height = 300, 70
    button_spacing = 20
    starting_y = HEIGHT // 2
    buttons = [
        Button(
            text=menu_option[i],
            x=WIDTH // 2 - button_width // 2,
            y=starting_y + i * (button_height + button_spacing),
            width=button_width,
            height=button_height,
            font=font,
            color=(20, 40, 80),
            hover_color=(40, 80, 160),
            glow_color=GLOW_BLUE
        ) for i in range(len(menu_option))
    ]

    # Create bubble particles
    bubbles = [Bubble() for _ in range(50)]  # Initial set of bubbles

    # Create floating particles
    particles = [FloatingParticle() for _ in range(100)]  # Floating particles for atmosphere

    # Create light ray overlay
    light_rays = LightRayOverlay()


    while True:
        mouse_pos = map_mouse_to_surface(pygame.mouse.get_pos(), actual_screen, render_surface)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for index, button in enumerate(buttons):
                    if button.is_clicked(mouse_pos):
                        if index == 0:
                            return "start"
                        elif index == 1:
                            options_menu(actual_screen)
                        elif index == 2:
                            return "quit"

        # Update button hover states
        for button in buttons:
            button.check_hover(mouse_pos)

        # Periodically add new bubbles
        if random.random() < 0.05:
            bubbles.append(Bubble())

        # Draw everything to the render surface
        draw_menu(render_surface, buttons, bubbles, particles, light_rays)

        # Apply letterboxing and smooth scaling
        render_with_letterbox(render_surface, actual_screen, target_resolution)

        clock.tick(FPS)



def options_menu(actual_screen):
    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()

    # Use high-resolution rendering
    target_resolution = actual_screen.get_size()
    render_surface = pygame.Surface(target_resolution)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        # Draw to the high-resolution render surface
        render_surface.fill(DARK_BLUE)
        text = font.render("Options Menu (Press ESC to return)", True, WHITE)
        text_rect = text.get_rect(center=(target_resolution[0] // 2, target_resolution[1] // 2))
        render_surface.blit(text, text_rect)

        # Apply letterboxing and smooth scaling
        render_with_letterbox(render_surface, actual_screen, target_resolution)

        clock.tick(FPS)
