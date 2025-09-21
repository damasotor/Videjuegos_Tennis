# engine/game_object.py
import pygame


class GameObject(pygame.sprite.Sprite):
    """
    Clase base mejorada que maneja imágenes estáticas y animaciones nombradas.
    Compatible con spritesheets con duración por frame.
    """

    def __init__(self, x, y, animations, default_anim=None):
        super().__init__()

        # animations: dict { anim_name: [ (Surface, duration_ms), ... ] }
        self.animations = animations
        self.current_anim = default_anim or list(animations.keys())[0]

        self.current_frame = 0
        self.image, self.frame_duration = self.animations[self.current_anim][self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))

        self.anim_timer = 0  # acumulador en ms

        # Movimiento
        self.vx = 0
        self.vy = 0
                
        # Nuevo: control de espejo
        self.flip_x = False 

    def play(self, anim_name):
        """Cambia de animación si es distinta a la actual."""
        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.current_frame = 0
            self.anim_timer = 0
            self.image, self.frame_duration = self.animations[self.current_anim][self.current_frame]

    def update(self, dt):
        """
        dt en segundos (float). 
        Maneja animación y movimiento.
        """
        # Actualizar animación
        frames = self.animations[self.current_anim]
        self.anim_timer += dt * 1000  # dt a ms
        if self.anim_timer >= self.frame_duration:
            self.anim_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image, self.frame_duration = frames[self.current_frame]

        # Detectar dirección horizontal para flip
        if self.vx < 0:
            self.flip_x = True
        elif self.vx > 0:
            self.flip_x = False

        # Actualizar posición
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)

    def draw(self, surface):
    # Dibujo espejado si flip_x es True
        img = pygame.transform.flip(self.image, self.flip_x, False) if self.flip_x else self.image
        surface.blit(img, self.rect)

