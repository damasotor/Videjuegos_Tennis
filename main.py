import os
import sys
import pygame
from engine.asset_manager import AssetManager
from engine.game_loop import GameLoop
from engine.sprite_sheet import Spritesheet as EngineSpritesheet
from engine.game_object import GameObject
from engine.player import Player


class Spritesheet:
    def __init__(self, json_path):
        self._engine_sheet = EngineSpritesheet(json_path)

    def get_sprite(self, name):
        return self._engine_sheet.get_frame(name)

    def get_animation_frames(self, anim_name):
        return self._engine_sheet.get_animation_frames(anim_name)


def main():
    pygame.init()
    pygame.display.set_caption("TENNIS")
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    FPS = 60

    game = Game(screen, clock, fps=FPS)
    game.run()


class Game(GameLoop):
    def __init__(self, screen, clock, fps=60):
        super().__init__(screen_width=screen.get_width(),
                         screen_height=screen.get_height(),
                         title="Tor TENNIS",
                         fps=fps)
        # Guardamos los que se pasan desde main()
        self.screen = screen
        self.clock = clock
        
        # Almacenamos el último tiempo para calcular dt
        self.last_tick = pygame.time.get_ticks()

        self.asset_manager = AssetManager()
        self.load_assets()
        self._setup_scene()

    def load_assets(self):
        base = os.path.join(os.path.dirname(__file__), "assets", "sprites")
        base = os.path.normpath(base)
        json_path = os.path.join(base, "sprites.json")
        try:
            self.asset_manager.load_spritesheet("player", json_path)
        except Exception as e:
            print("Error cargando spritesheet:", e)
            raise

        
        # Fondo detrás (estadio)
        estadio_path = os.path.join(base, "estadio.png")
        if os.path.exists(estadio_path):
            self.estadio = self.asset_manager.load_image("estadio", estadio_path)
        else:
            self.estadio = None

        # Fondo principal (cancha)
        cancha_path = os.path.join(base, "cancha.png")
        if os.path.exists(cancha_path):
            self.cancha = self.asset_manager.load_image("cancha", cancha_path)
        else:
            self.cancha = None
        
        # Red
        red_path = os.path.join(base, "red.png")
        if os.path.exists(red_path):
            self.red = self.asset_manager.load_image("red", red_path)
        else:
            self.red = None
        
    def _setup_scene(self):
        ss = self.asset_manager.spritesheets["player"]

        # Crear animaciones con duration del JSON
        def build_anim(tag):
            frames = ss.get_animation_frames(tag, with_duration=True)
            return frames

        animations = {
            "EnemyIdle": build_anim("EnemyIdle"),
            "EnemyWalk": build_anim("EnemyWalk"),
            "PlayerIdle": build_anim("PlayerIdle"),
            "PlayerWalk": build_anim("PlayerWalk"),

        }

        # Jugadores
        self.player1 = Player(40, 400, animations, default_anim="PlayerIdle")
        self.player2 = Player(450, 40, animations, default_anim="EnemyIdle")

        self.all_sprites = pygame.sprite.Group(self.player1, self.player2)

    def handle_specific_events(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def update_game_logic(self):
        # Calcular dt dentro de la función, ya que no se pasa como argumento
        now = pygame.time.get_ticks()
        dt = (now - self.last_tick) / 1000.0  # Convertir a segundos
        self.last_tick = now

        keys = pygame.key.get_pressed()
        
        if self.cancha:
            screen_rect = self.screen.get_rect()
            estadio_rect = self.estadio.get_rect(center=screen_rect.center)

        # --- Jugador 1 (flechas) ---
        self.player1.vx = 0
        self.player1.vy = 0
        if keys[pygame.K_LEFT]:
            self.player1.vx = -150
        elif keys[pygame.K_RIGHT]:
            self.player1.vx = 150
        if keys[pygame.K_UP]:
            self.player1.vy = -150
        elif keys[pygame.K_DOWN]:
            self.player1.vy = 150

        if self.player1.vx != 0 or self.player1.vy != 0:
            self.player1.play("PlayerWalk")
        else:
            self.player1.play("PlayerIdle")

        # --- Jugador 2 (z,c,s,x) ---
        self.player2.vx = 0
        self.player2.vy = 0
        if keys[pygame.K_z]:
            self.player2.vx = -150
        elif keys[pygame.K_c]:
            self.player2.vx = 150
        if keys[pygame.K_s]:
            self.player2.vy = -150
        elif keys[pygame.K_x]:
            self.player2.vy = 150

        if self.player2.vx != 0 or self.player2.vy != 0:
            self.player2.play("EnemyWalk")
        else:
            self.player2.play("EnemyIdle")

        # Actualizar animaciones y movimiento
        self.all_sprites.update(dt)

        # --- Cálculo del rect de la red ---
        if self.red:
            red_rect = self.red.get_rect(center=self.screen.get_rect().center)

        # Mantener dentro de pantalla
        w, h = self.screen.get_size()

        # Player1 -> siempre debajo de la red
        if self.player1.rect.top < (red_rect.bottom - 130):
            self.player1.rect.top = red_rect.bottom - 130

        # Player2 -> siempre encima de la red
        if self.player2.rect.bottom > (red_rect.top -10):
            self.player2.rect.bottom = red_rect.top - 10

        # --- Restricción horizontal con perspectiva para Player2 ---
        max_width = w * 0.4   # ancho casi total (abajo)
        min_width = w * 0.2   # ancho mínimo (arriba)

        red_y = estadio_rect.centery - 55
        top_y = estadio_rect.top

        # Factor proporcional según altura de player2
        factor = (red_y - self.player2.rect.centery) / (red_y - top_y)
        factor = max(0, min(1, factor))  # clamp 0..1

        allowed_width = min_width + (max_width - min_width) * (1 - factor)

        left_limit = estadio_rect.centerx - allowed_width
        right_limit = estadio_rect.centerx + allowed_width

        if self.player2.rect.left < left_limit:
            self.player2.rect.left = left_limit
        if self.player2.rect.right > right_limit:
            self.player2.rect.right = right_limit

        for player in [self.player1, self.player2]:
            if player.rect.left < 0: player.rect.left = 0
            if player.rect.right > w: player.rect.right = w           
            if player.rect.top < -15: player.rect.top = -15
            if player.rect.bottom > (h - 20): player.rect.bottom = h - 20

    def draw_game_elements(self):
        screen_rect = self.screen.get_rect()

        # 1. Dibuja el estadio, el fondo más lejano.
        if self.estadio:
            estadio_rect = self.estadio.get_rect(center=screen_rect.center)
            self.screen.blit(self.estadio, estadio_rect.topleft)
        else:
            self.screen.fill((30, 30, 40))  # fondo gris si no hay estadio

        # 2. Dibuja la cancha, por encima del estadio.
        if self.cancha:
            cancha_rect = self.cancha.get_rect(center=screen_rect.center)
            self.screen.blit(self.cancha, cancha_rect.topleft)

        # 3. Dibuja al Jugador 2 (Enemy), para que aparezca detrás de la red.
        self.player2.draw(self.screen)

        # 4. Dibuja la red, en el medio de la cancha, por encima del Jugador 2.
        if self.red and self.cancha:
            cancha_rect = self.cancha.get_rect(center=screen_rect.center)
            red_rect = self.red.get_rect(midtop=(cancha_rect.centerx, cancha_rect.centery - 55))
            self.screen.blit(self.red, red_rect.topleft)

        # 5. Dibuja al Jugador 1 (Player), para que aparezca delante de la red.
        self.player1.draw(self.screen)

        # 6. Dibuja el contador de FPS.
        font = pygame.font.SysFont(None, 20)
        fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))
        self.screen.blit(fps_text, (5, 5))

if __name__ == "__main__":
    main()
