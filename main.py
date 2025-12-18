# main.py FINAL
import os
import sys
import pygame
from engine.game import Game

if __name__ == "__main__":
    try:
        # Fijar el directorio de trabajo (para rutas de assets)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_dir)
    except (NameError, FileNotFoundError):
        pass # Manejar ejecución no estándar

    # Ya no es necesario llamar pygame.init() aquí si GameLoop.__init__() lo hace, 
    # pero no hace daño dejarlo. Lo quitamos para mayor limpieza.
    
    try:
        game = Game()
        game.game_loop() # o game.run() si usas el método original
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        raise
    finally:
        pygame.quit()
