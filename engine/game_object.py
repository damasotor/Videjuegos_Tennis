# engine/game_object.py
import pygame


class GameObject(pygame.sprite.Sprite):
    """
    Clase base mejorada que maneja imágenes estáticas y animaciones.
    """

    def __init__(self, x, y, frames):
        super().__init__()

        # frames puede ser una sola Surface o una lista de Surfaces
        if isinstance(frames, list):
            self.frames = frames
            self.is_animated = True
            self.current_frame = 0
            self.image = self.frames[self.current_frame]
            self.anim_speed = 0.1  # Velocidad de animación (frames por tick)
            self.anim_timer = 0
        else:
            self.frames = [frames]
            self.is_animated = False
            self.image = frames

        self.rect = self.image.get_rect(center=(x, y))

    def update_animation(self):
        """Actualiza el frame de la animación si es necesario."""
        if not self.is_animated or len(self.frames) < 2:
            return

        self.anim_timer += self.anim_speed
        if self.anim_timer >= 1:
            self.anim_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def update(self, *args, **kwargs):
        """El método update ahora también se encarga de la animación."""
        self.update_animation()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
