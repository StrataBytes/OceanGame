import pygame
from settings import SUB_SPEED, SUB_COLOR, SUB_SIZE

life = 100

class Submarine:
    def __init__(self, x, y):
        #world position
        self.x = x
        self.y = y
        self.width, self.height = SUB_SIZE
        self.speed = SUB_SPEED

        self.oxygen = 100
        self.power = 100
        self.hull = 100

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        #invincibility
        self.invincible = False
        self.invincible_timer = 0  #tracks end time of invincibility in ms
        self.invincible_duration = 1000  #duration in ms

    def update(self, seabed_height):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.consume_power(0.01)
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.consume_power(0.01)
        if keys[pygame.K_UP]:
            self.y -= self.speed
            self.consume_power(0.01)
        if keys[pygame.K_DOWN]:
            self.y += self.speed
            self.consume_power(0.01)

        self.consume_oxygen(0.005)

        #clamp pos. to between surface and seabed
        self.y = max(0, min(self.y, seabed_height - self.height))
        self.rect.topleft = (self.x, self.y)

        #update invince timer
        if self.invincible and pygame.time.get_ticks() > self.invincible_timer:
            self.invincible = False

    def draw(self, screen, offset):
        #adj position based on camera offset
        screen_x = self.x - offset[0]
        screen_y = self.y - offset[1]
        submarine_color = SUB_COLOR if not self.invincible else (252, 94, 3)  #flash orange when invinve
        pygame.draw.rect(screen, submarine_color, (screen_x, screen_y, self.width, self.height))

    def consume_power(self, amount):
        self.power = max(0, self.power - amount)

    def consume_oxygen(self, amount):
        self.oxygen = max(0, self.oxygen - amount)

    def take_damage(self, amount):
        if not self.invincible:
            self.hull = max(0, self.hull - amount)
            self.invincible = True
            #invinc timer to current time plus duration
            self.invincible_timer = pygame.time.get_ticks() + self.invincible_duration