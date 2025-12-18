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
                
        # Control de espejo
        self.flip_x = False

        # 🔒 control de bloqueo de animación
        self.locked = False 

    def play(self, anim_name, reset=False, lock=False):
        if anim_name in self.animations:
            # si está bloqueado no se puede interrumpir
            if self.locked and not reset:
                return  

            if reset or anim_name != self.current_anim:
                self.current_anim = anim_name
                self.current_frame = 0
                self.anim_timer = 0
                self.image, self.frame_duration = self.animations[self.current_anim][self.current_frame]

                if lock:
                    self.locked = True  # 🔒 bloquear hasta terminar

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
            self.current_frame += 1

            # Si se pasó del último frame
            if self.current_frame >= len(frames):
                self.current_frame = 0
                # 🔓 desbloquear al terminar animación
                self.locked = False  

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
        # 1. Aplicamos el espejado (tu lógica original)
        img = pygame.transform.flip(self.image, self.flip_x, False) if self.flip_x else self.image
        
        # 2. Aplicamos la perspectiva (solo si el objeto tiene scale_factor y es distinto de 1)
        # hasattr evita errores si otros objetos no usan escala
        if hasattr(self, 'scale_factor') and self.scale_factor != 1.0:
            original_size = img.get_size()
            new_size = (int(original_size[0] * self.scale_factor), 
                        int(original_size[1] * self.scale_factor))
            img = pygame.transform.scale(img, new_size)

        # 3. Calculamos el nuevo rect para que la imagen se dibuje centrada 
        # La 'z' eleva la imagen visualmente, pero el rect.center sigue en el suelo
        altura = getattr(self, 'z', 0)
        pos_visual = (self.rect.centerx, self.rect.centery - altura)
        
        new_rect = img.get_rect(center=pos_visual)
        
        surface.blit(img, new_rect)
