# engine/game_loop.py
import pygame


class GameLoop:
    """
    Clase base que gestiona el bucle principal, eventos, actualizaciones y dibujado.
    Los juegos específicos deben heredar de esta clase.
    """

    def __init__(self, screen_width, screen_height, title, fps):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = False

    def _handle_events(self):
        """Maneja eventos globales como cerrar la ventana."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Pasa los eventos a la clase hija para manejo específico
            self.handle_specific_events(event)

    def _update(self):
        """Llama al método de actualización de la clase hija."""
        self.update_game_logic()

    def _draw(self):
        """Llama al método de dibujado de la clase hija."""
        self.draw_game_elements()
        pygame.display.flip()

    def run(self):
        """El bucle principal del juego."""
        self.running = True
        while self.running:
            self.clock.tick(self.fps)
            self._handle_events()
            self._update()
            self._draw()
        pygame.quit()

    # --- Métodos para ser sobreescritos por las clases hijas ---
    def handle_specific_events(self, event):
        pass

    def update_game_logic(self):
        """Actualiza la lógica específica del juego."""
        pass

    def draw_game_elements(self):
        pass

