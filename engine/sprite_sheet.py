import pygame
import json
import os

class Spritesheet:
    def __init__(self, json_path):
        with open(json_path, "r") as f:
            self.data = json.load(f)

        # carga la imagen que figura en el JSON
        image_path = self.data["meta"]["image"]
        if not os.path.isabs(image_path):
            image_path = os.path.join(os.path.dirname(json_path), image_path)
        self.image = pygame.image.load(image_path).convert_alpha()

    def get_frame(self, frame_name):
        frame = self.data["frames"][frame_name]["frame"]
        rect = pygame.Rect(frame["x"], frame["y"], frame["w"], frame["h"])
        surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        surf.blit(self.image, (0, 0), rect)
        return surf

    def get_animation_frames(self, anim_name, with_duration=False):
        """
        Devuelve una lista de frames de la animación.
        Si with_duration=True, devuelve [(Surface, duration_ms), ...]
        Caso contrario, solo [Surface, ...]
        """
        frames = []
        if "frameTags" in self.data["meta"]:
            for tag in self.data["meta"]["frameTags"]:
                if tag["name"] == anim_name:
                    for i in range(tag["from"], tag["to"] + 1):
                        frame_name = f"Sprites {i}.ase"
                        frame_info = self.data["frames"][frame_name]
                        duration = frame_info["duration"]
                        surf = self.get_frame(frame_name)
                        if with_duration:
                            frames.append((surf, duration))
                        else:
                            frames.append(surf)
                    return frames

        # fallback por prefijo si no existe el tag
        for fname, frame_info in self.data["frames"].items():
            if fname.startswith(anim_name):
                duration = frame_info["duration"]
                surf = self.get_frame(fname)
                if with_duration:
                    frames.append((surf, duration))
                else:
                    frames.append(surf)
        return frames

