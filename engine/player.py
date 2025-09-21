# engine/player.py
from engine.game_object import GameObject


class Player(GameObject):
    def __init__(self, x, y, animations):
        """
        animations: dict con nombre de animación -> lista de frames (Surfaces)
        """
        self.animations = animations
        self.current_anim = "idle"

        # Inicia con la animación "idle"
        frames = self.animations[self.current_anim]
        super().__init__(x, y, frames)

        # Velocidades
        self.vx = 0
        self.vy = 0

    def update(self, *args, **kwargs):
        # Cambiar animación según movimiento
        if self.vx != 0 or self.vy != 0:
            if self.current_anim != "walk":
                self.current_anim = "walk"
                self.frames = self.animations[self.current_anim]
                self.current_frame = 0
        else:
            if self.current_anim != "idle":
                self.current_anim = "idle"
                self.frames = self.animations[self.current_anim]
                self.current_frame = 0

        # Llamar a la actualización de GameObject (animación)
        super().update()

        # Actualizar posición
        self.rect.x += self.vx
        self.rect.y += self.vy

