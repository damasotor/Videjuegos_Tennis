
from .sprite_sheet import Spritesheet

class AssetManager:
    def __init__(self):
        self.spritesheets = {}  # name -> Spritesheet instance
        self.images = {}        # name -> pygame.Surface
        self.sounds = {}        # name -> Sound (if se usa)

    def load_spritesheet(self, name, json_path):
        """Carga un spritesheet desde un JSON y lo guarda con un nombre clave."""
        try:
            self.spritesheets[name] = Spritesheet(json_path)
            print(f"Spritesheet '{name}' cargado desde '{json_path}'")
        except Exception as e:
            print(f"Error al cargar el spritesheet '{name}': {e}")
            raise

    def load_image(self, name, image_path):
        """
        Carga una imagen estática y la guarda por nombre.
        """
        import pygame
        if name in self.images:
            return self.images[name]
        surf = pygame.image.load(image_path).convert_alpha()
        self.images[name] = surf
        return surf

    def get_sprite(self, sheet_name, sprite_name):
        """
        Obtiene una Surface con el sprite individual.
        """
        sheet = self.spritesheets.get(sheet_name)
        if not sheet:
            raise KeyError(f"Spritesheet '{sheet_name}' no cargado")
        return sheet.get_frame(sprite_name)

    def get_animation(self, sheet_name, anim_name):
        """Obtiene los frames de una animación de un spritesheet ya cargado."""
        if sheet_name not in self.spritesheets:
            raise KeyError(f"No se ha cargado un spritesheet con el nombre '{sheet_name}'")
        return self.spritesheets[sheet_name].get_animation_frames(anim_name)

    def get_image(self, name):
        """Obtiene una imagen suelta ya cargada."""
        if name not in self.images:
            raise KeyError(f"No se ha cargado una imagen con el nombre '{name}'")
        return self.images[name]

