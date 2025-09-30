# engine/player.py
import pygame
from engine.game_object import GameObject

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, animations, default_anim):
        super().__init__()
        self.animations = animations
        self.current_anim = default_anim
        self.frames = self.animations[self.current_anim]
        self.current_frame = 0
        self.anim_timer = 0
        self.image = self.frames[self.current_frame][0]  # Get the first image
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = 0
        self.vy = 0

    def update(self, dt):
        # Update animation based on delta time (dt)
        self.anim_timer += self.frames[self.current_frame][1]
        if self.anim_timer >= 1000: # Assuming duration is in milliseconds
            self.anim_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame][0]

        # Update position
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

    def play(self, anim_name):
        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.frames = self.animations[self.current_anim]
            self.current_frame = 0
            self.anim_timer = 0
            self.image = self.frames[self.current_frame][0]

    def draw(self, surface):
        surface.blit(self.image, self.rect)
