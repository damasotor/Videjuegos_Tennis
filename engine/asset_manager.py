import os
from .sprite_sheet import Spritesheet

class AssetManager:
    def __init__(self):
        self.spritesheets = {}  # name -> Spritesheet instance
        self.images = {}        # name -> pygame.Surface
        self.sounds = {}        # name -> Sound (if se usa)

    def load_spritesheet(self, name, json_path):
        """
        Carga un spritesheet (JSON + image) y lo guarda bajo la clave name.
        json_path: ruta al archivo json del spritesheet (puede contener ruta absoluta en meta.image)
        """
        if name in self.spritesheets:
            return self.spritesheets[name]
        sheet = Spritesheet(json_path)
        self.spritesheets[name] = sheet
        return sheet

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
        """
        Obtiene lista de Surfaces para una animación.
        anim_name puede ser un prefijo (p. ej. 'Sprites') que coincida con 'Sprites 0.ase', etc.
        """
        sheet = self.spritesheets.get(sheet_name)
        if not sheet:
            return []
        # intentamos por nombre exacto de animación dentro del json meta.frameTags si existiera
        frames = sheet.get_animation_frames(anim_name)
        if frames:
            return frames
        # fallback: buscar por prefijo en nombres de frames
        return sheet.get_animation_frames_by_prefix(anim_name)

    def get_image(self, name):
        return self.images.get(name)

