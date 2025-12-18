# engine/game.py

import os
import sys
import pygame
from engine.asset_manager import AssetManager
from engine.game_loop import GameLoop
from engine.game_object import GameObject
from engine.sprite_sheet import Spritesheet as EngineSpritesheet 

# --- Clase Spritesheet Adaptadora ---
class Spritesheet:
    def __init__(self, json_path):
        self._engine_sheet = EngineSpritesheet(json_path)

    def get_sprite(self, name):
        return self._engine_sheet.get_frame(name)

    def get_animation_frames(self, anim_name):
        return self._engine_sheet.get_animation_frames(anim_name)

# --- Clase Game (Lógica Principal del Juego) ---
class Game(GameLoop):
    
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480
    TITLE = "Tor TENNIS"
    FPS = 60

    def __init__(self):
        super().__init__(screen_width=self.SCREEN_WIDTH,
                         screen_height=self.SCREEN_HEIGHT,
                         title=self.TITLE,
                         fps=self.FPS)

        self.asset_manager = AssetManager()
        self.load_assets()
        self._setup_scene()

    def game_loop(self):
        self.run()

    def load_assets(self):
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")
        base = os.path.normpath(base)
        
        # 1. Cargar Jugadores
        json_path = os.path.join(base, "sprites.json")
        try:
            self.asset_manager.load_spritesheet("player", json_path)
        except Exception as e:
            print("Error cargando spritesheet:", e)
            raise

        # 2. CARGAR PELOTA (Manual: pelota.png tiene 2 frames de 32x32)
        ball_path = os.path.join(base, "pelota.png")
        if os.path.exists(ball_path):
            ball_sheet = pygame.image.load(ball_path).convert_alpha()
            # Cortamos los dos cuadros de 32x32
            f1 = ball_sheet.subsurface(pygame.Rect(0, 0, 32, 32))
            f2 = ball_sheet.subsurface(pygame.Rect(32, 0, 32, 32))
            # Creamos el diccionario de animación para la pelota
            self.ball_animations = {"girar": [(f1, 100), (f2, 100)]}
        else:
            print(f"Error: No se encontró {ball_path}")
            self.ball_animations = None

        # 3. Carga de fondos
        self.estadio = self.asset_manager.load_image("estadio", os.path.join(base, "estadio.png"))
        self.cancha = self.asset_manager.load_image("cancha", os.path.join(base, "cancha.png"))
        self.red = self.asset_manager.load_image("red", os.path.join(base, "red.png"))
        
    def _setup_scene(self):
        ss = self.asset_manager.spritesheets["player"]
        def build_anim(tag):
            return ss.get_animation_frames(tag, with_duration=True) 

        animations = {
            "EnemyIdle": build_anim("EnemyIdle"), "EnemyWalk": build_anim("EnemyWalk"),
            "EnemyGolpeB": build_anim("EnemyGolpeB"), "EnemySaque": build_anim("EnemySaque"),
            "PlayerIdle": build_anim("PlayerIdle"), "PlayerWalk": build_anim("PlayerWalk"),
            "PlayerGolpeB": build_anim("PlayerGolpeB"), "PlayerSaque": build_anim("PlayerSaque"),
        }

        self.player1 = GameObject(320, 420, animations, default_anim="PlayerIdle")
        self.player2 = GameObject(320, 100, animations, default_anim="EnemyIdle")
        
        # INSTANCIAR PELOTA
        if self.ball_animations:
            self.ball = GameObject(320, 240, self.ball_animations, default_anim="girar")

            self.ball.vx = 120    # Velocidad horizontal
            self.ball.vy = 140    # Velocidad de profundidad (hacia el fondo/frente)
            self.ball.vz = 400    # Velocidad inicial de salto (hacia arriba)
            self.ball.z = 0       # Altura inicial (en el suelo)
            self.GRAVITY = -500   # Fuerza de gravedad (píxeles/s^2)
            self.BOUNCE = -0.7    # Elasticidad (pierde 30% de fuerza al rebotar)
        
        self.all_sprites = pygame.sprite.Group(self.player1, self.player2, self.ball)

    def handle_specific_events(self, event):
        if event.type == pygame.KEYDOWN:
            # Salir con ESC
            if event.key == pygame.K_ESCAPE:
                self.running = False
            
            # Reiniciar con F2
            if event.key == pygame.K_F2:
                self.reset_game()

    def reset_game(self):
        """Reinicia la posición de los jugadores y la pelota"""
        # Reposicionar Jugadores
        self.player1.rect.center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 60)
        self.player2.rect.center = (self.SCREEN_WIDTH // 2, 80)
        
        # Resetear Pelota
        self.ball.rect.center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
        self.ball.vx = 0
        self.ball.vy = -100
        self.ball.vz = 50
        self.ball.z = 150
        
        # Desbloquear animaciones por si acaso
        self.player1.locked = False
        self.player2.locked = False
        self.player1.play("PlayerIdle", reset=True)
        self.player2.play("EnemyIdle", reset=True)
        
        print("Juego Reiniciado")
        
    def _check_ball_collision(self, player, threshold):
        """Verifica el impacto en el punto medio del jugador"""
        # 1. Distancia Horizontal (X): Usamos los centros
        dist_x = abs(player.rect.centerx - self.ball.rect.centerx)
    
        # 2. Distancia de Profundidad (Y): 
        # El jugador y la pelota deben estar casi en la misma línea de 'suelo'
        dist_y = abs(player.rect.centery - self.ball.rect.centery)
    
        # 3. Validación de Altura (Z):
        # Definimos que la raqueta golpea entre la cintura y la cabeza (ej: entre 20 y 70px de altura)
        altura_minima = 15
        altura_maxima = 75
        esta_en_altura_raqueta = altura_minima <= self.ball.z <= altura_maxima
        
        # Solo hay golpe si está cerca en X, en Y, y a la altura correcta
        # Bajamos el margen de Y a 15 para que sea más preciso
        return dist_x < threshold and dist_y < 15 and esta_en_altura_raqueta

    def update_game_logic(self, dt):
        keys = pygame.key.get_pressed()
        dist_umbral = 45  # Ajusta según prefieras la sensibilidad del golpe
        
        # --- LÓGICA DE JUGADOR 1 ---
        self.player1.vx = 0
        self.player1.vy = 0
        is_moving_p1 = False
        
        # Movimiento básico
        if keys[pygame.K_LEFT]: self.player1.vx = -150; is_moving_p1 = True
        elif keys[pygame.K_RIGHT]: self.player1.vx = 150; is_moving_p1 = True
        if keys[pygame.K_UP]: self.player1.vy = -150; is_moving_p1 = True
        elif keys[pygame.K_DOWN]: self.player1.vy = 150; is_moving_p1 = True

        # GOLPES Y ANIMACIONES
        # Prioridad 1: Si presiona 'o' (Saque/Alto)
        if keys[pygame.K_o]:
            self.player1.play("PlayerSaque", reset=False, lock=True)
            # Física del golpe
            if self._check_ball_collision(self.player1, dist_umbral):
                self.ball.vy = -250  # Hacia el fondo
                self.ball.vz = 400   # Salto alto
                self.ball.vx = (self.ball.rect.centerx - self.player1.rect.centerx) * 4

        # Prioridad 2: Si presiona 'p' (Golpe Bajo)
        elif keys[pygame.K_p]:
            self.player1.play("PlayerGolpeB", reset=False, lock=True)
            # Física del golpe
            if self._check_ball_collision(self.player1, dist_umbral):
                self.ball.vy = -300  # Más rápido hacia el fondo
                self.ball.vz = 200   # Salto bajo/tenso
                self.ball.vx = (self.ball.rect.centerx - self.player1.rect.centerx) * 4

        # Prioridad 3: Estados de movimiento (Solo si no está ejecutando un golpe)
        elif not self.player1.locked:
            if is_moving_p1:
                if self.player1.current_anim != "PlayerWalk":
                    self.player1.play("PlayerWalk", reset=True, lock=False)
            else:
                if self.player1.current_anim != "PlayerIdle":
                    self.player1.play("PlayerIdle", reset=True, lock=False)

        # --- Lógica de Jugador 2 ---
        self.player2.vx = 0
        self.player2.vy = 0
        is_moving_p2 = False
        
        # MOVIMIENTO JUGADOR 2 (W, A, S, D)
        if keys[pygame.K_a]: self.player2.vx = -150; is_moving_p2 = True
        elif keys[pygame.K_d]: self.player2.vx = 150; is_moving_p2 = True
        if keys[pygame.K_w]: self.player2.vy = -150; is_moving_p2 = True
        elif keys[pygame.K_s]: self.player2.vy = 150; is_moving_p2 = True
        
        # GOLPES Y ANIMACIONES
        # Prioridad 1: Si presiona 'y' (Saque/Alto)
        if keys[pygame.K_y]:
            self.player2.play("EnemySaque", reset=False, lock=True)
            # Física del golpe
            if self._check_ball_collision(self.player2, dist_umbral):
                self.ball.vy = -250  # Hacia el fondo
                self.ball.vz = -400   # Salto alto
                self.ball.vx = (self.ball.rect.centerx - self.player2.rect.centerx) * 4

        # Prioridad 2: Si presiona 'u' (Golpe Bajo)
        elif keys[pygame.K_u]:
            self.player2.play("EnemyGolpeB", reset=False, lock=True)
            # Física del golpe
            if self._check_ball_collision(self.player2, dist_umbral):
                self.ball.vy = -300  # Más rápido hacia el fondo
                self.ball.vz = -200   # Salto bajo/tenso
                self.ball.vx = (self.ball.rect.centerx - self.player2.rect.centerx) * 4

        # Prioridad 3: Estados de movimiento (Solo si no está ejecutando un golpe)
        elif not self.player2.locked:
            if is_moving_p2:
                if self.player2.current_anim != "EnemyWalk":
                    self.player2.play("EnemyWalk", reset=True, lock=False)
            else:
                if self.player2.current_anim != "EnemyIdle":
                    self.player2.play("EnemyIdle", reset=True, lock=False)

        
        # Para choque de pelota con red
        y_antes = self.ball.rect.centery
        # Actualizar todos (Moverá la pelota y jugadores)
        self.all_sprites.update(dt)

        # --- FÍSICA Y PERSPECTIVA DE LA PELOTA ---
        w, h = self.screen.get_size()
        
        # Cambio altura de la pelota
        self.ball.vz += self.GRAVITY * dt
        self.ball.z += self.ball.vz * dt
        
        # --- LÓGICA DE COLISIÓN CON LA RED ---
        if self.cancha:
            screen_rect = self.screen.get_rect()
            cancha_rect = self.cancha.get_rect(center=screen_rect.center)
            
            # La red está físicamente en el centro vertical de la cancha
            net_y_floor = cancha_rect.centery 
            net_height = 55  # Esta es la altura en píxeles de tu sprite de red
            
            y_ahora = self.ball.rect.centery

            # Comprobar si la pelota cruzó la línea de la red en este frame
            # (Si antes estaba arriba y ahora abajo, o viceversa)
            if (y_antes < net_y_floor <= y_ahora) or (y_ahora <= net_y_floor < y_antes):
                if 100 < self.ball.rect.centerx < 540:
                # Si cruza la línea, comprobamos si su altura (Z) es menor a la red
                    if self.ball.z < net_height:
                        # ¡CHOQUE! 
                        # 1. Detenemos avance horizontal y de profundidad
                        self.ball.vx = 0
                        self.ball.vy = 0
                    
                        # 2. Posicionamos la pelota justo al lado del choque para que no traspase
                        if y_antes < net_y_floor:
                            self.ball.rect.bottom = net_y_floor - 1
                        else:
                            self.ball.rect.top = net_y_floor + 1
                    
                        # 3. Opcional: Un pequeño rebote hacia atrás para que no se quede pegada
                        # self.ball.vy = -20 if y_ahora > net_y_floor else 20
        
        # 3. Rebote
        if self.ball.z <= 0:
            self.ball.z = 0
            if abs(self.ball.vz) > 20:
                self.ball.vz *= self.BOUNCE
            else:
                self.ball.vz = 0
        
        # 1. Rebotes simples contra las paredes
        if self.ball.rect.left < 60 or self.ball.rect.right > w - 60:
            self.ball.vx *= -1
        if self.ball.rect.top < 30 or self.ball.rect.bottom > h - 30:
            self.ball.vy *= -1

        # 2. EFECTO PERSPECTIVA: Escala según la posición Y
        # y=20 (fondo) -> escala 0.4 | y=460 (frente) -> escala 1.2
        min_y, max_y = 20, 460
        rango_y = max_y - min_y
        porcentaje_y = (self.ball.rect.centery - min_y) / rango_y
        porcentaje_y = max(0, min(1, porcentaje_y)) # Asegurar que esté entre 0 y 1
        
        self.ball.scale_factor = 0.2 + (porcentaje_y * 0.2)

        # --- Límites de los Jugadores (Tu código original) ---
        if self.cancha:
            screen_rect = self.screen.get_rect()
            estadio_rect = self.estadio.get_rect(center=screen_rect.center) if self.estadio else screen_rect
            red_rect = self.red.get_rect(center=screen_rect.center) if self.red else screen_rect

            if self.player1.rect.top < (red_rect.bottom - 130): self.player1.rect.top = red_rect.bottom - 130
            if self.player2.rect.bottom > (red_rect.top -10): self.player2.rect.bottom = red_rect.top - 10
            
            # Perspectiva Player 2
            max_w_p2, min_w_p2 = w * 0.4, w * 0.2
            red_y, top_y = estadio_rect.centery - 55, estadio_rect.top
            f = max(0, min(1, (red_y - self.player2.rect.centery) / (red_y - top_y)))
            allowed_w = min_w_p2 + (max_w_p2 - min_w_p2) * (1 - f)
            if self.player2.rect.left < estadio_rect.centerx - allowed_w: self.player2.rect.left = estadio_rect.centerx - allowed_w
            if self.player2.rect.right > estadio_rect.centerx + allowed_w: self.player2.rect.right = estadio_rect.centerx + allowed_w

        # Límites generales
        for p in [self.player1, self.player2]:
            if p.rect.left < 0: p.rect.left = 0
            if p.rect.right > w: p.rect.right = w 
            if p.rect.top < -15: p.rect.top = -15
            if p.rect.bottom > (h - 20): p.rect.bottom = h - 20

    def draw_game_elements(self):
        screen_rect = self.screen.get_rect()

        if self.estadio: self.screen.blit(self.estadio, self.estadio.get_rect(center=screen_rect.center).topleft)
        else:
            self.screen.fill((30, 30, 40)) 

        if self.cancha: self.screen.blit(self.cancha, self.cancha.get_rect(center=screen_rect.center).topleft)
        
        # Dibujamos la sombra (usamos getattr por seguridad)
        z_actual = getattr(self.ball, 'z', 0)
        
        # Dibujamos la sombra siempre que la pelota no esté "bajo tierra"
        if z_actual >= 0:
            # La sombra se hace un poco más pequeña si la pelota sube mucho
            factor_sombra = self.ball.scale_factor * (1 - min(0.5, z_actual / 500))
            shadow_w = int(20 * factor_sombra)
            shadow_h = int(10 * factor_sombra)
            
            # Crear superficie de sombra con transparencia
            shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect())
            
            # IMPORTANTE: La sombra se dibuja en la posición real (el suelo)
            self.screen.blit(shadow_surf, shadow_surf.get_rect(center=self.ball.rect.center))

        # DIBUJAR EN ORDEN DE PROFUNDIDAD
        self.player2.draw(self.screen) # Jugador al fondo
        
        # Dibujar Pelota (la lógica de escala debe estar en el draw de GameObject)
        self.ball.draw(self.screen)

        if self.red and self.cancha:
            cancha_rect = self.cancha.get_rect(center=screen_rect.center)
            red_rect = self.red.get_rect(midtop=(cancha_rect.centerx, cancha_rect.centery - 55))
            self.screen.blit(self.red, red_rect.topleft)

        self.player1.draw(self.screen) # Jugador al frente

        # FPS
        font = pygame.font.SysFont(None, 20)
        fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))
        self.screen.blit(fps_text, (5, 5))
