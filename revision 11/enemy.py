import pygame
import math
import random

class Enemy:
    def __init__(self, x, y, width, height, speed=2, chase_radius=200, damage = 10):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.chase_radius = chase_radius
        self.patrol_radius = 100
        self.start_pos = (x, y)
        self.target_pos = None
        self.damage = damage

    def chase(self, player):
        distance = math.sqrt((player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2)

        if distance < self.chase_radius:
            if player.rect.x > self.rect.x:
                self.rect.x += self.speed
            elif player.rect.x < self.rect.x:
                self.rect.x -= self.speed

            if player.rect.y > self.rect.y:
                self.rect.y += self.speed
            elif player.rect.y < self.rect.y:
                self.rect.y -= self.speed
        else:
            #if not chasing, return to patrol or idle
            self.patrol()

    def patrol(self):
        if self.target_pos is None or self.rect.collidepoint(self.target_pos):
            #random target position within the patrol radius
            self.target_pos = (
                random.randint(self.start_pos[0] - self.patrol_radius, self.start_pos[0] + self.patrol_radius),
                random.randint(self.start_pos[1] - self.patrol_radius, self.start_pos[1] + self.patrol_radius)
            )
        
        #move to target pos
        if self.target_pos[0] > self.rect.x:
            self.rect.x += self.speed // 2
        elif self.target_pos[0] < self.rect.x:
            self.rect.x -= self.speed // 2

        if self.target_pos[1] > self.rect.y:
            self.rect.y += self.speed // 2
        elif self.target_pos[1] < self.rect.y:
            self.rect.y -= self.speed // 2

    # #needs to be changed for sprite.collide
    def check_collision(self, player):
        if self.rect.colliderect(player.rect):
            player.take_damage(self.damage)


    def draw(self, screen, offset):
        screen_x = self.rect.x - offset[0]
        screen_y = self.rect.y - offset[1]
        pygame.draw.rect(screen, (201, 6, 6), (screen_x, screen_y, self.rect.width, self.rect.height))

    def update(self, player, offset):
        self.chase(player)
