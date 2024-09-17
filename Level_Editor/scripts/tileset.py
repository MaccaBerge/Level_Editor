import pygame
import pygame.surface
import json
from typing import Any

from .utils.image import load_image

class Tileset:
    def __init__(self, name: str, t_type: str, image_path: str, tile_width: int, tile_height: int, margin: int = 0, spacing: int = 0, colorkey: pygame.Color | None = None) -> None:
        self.name = name
        self.type = t_type
        self.image_path = image_path
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.margin = margin
        self.spacing = spacing
        self.colorkey: pygame.Color = colorkey

        self.image: pygame.Surface = load_image(self.image_path)

        self.image_size = self.image.get_size()
        self.tiles_per_row = self.image_size[0] // self.tile_width
        self.tiles_per_column = self.image_size[1] // self.tile_height

        self.tiles = {}
        self._extract_tileset_tiles()
    
    def _extract_tileset_tiles(self):
        # have to add error handeling, if the usbsurface is outside of the bounds of the surface
        if self.tile_width > self.image_size[0] or self.tile_height > self.image_size[1]: 
            print("Didnt find subsurface of that size.")
            return

        tile_id = 0

        for row in range(self.tiles_per_column):
            for col in range(self.tiles_per_row):
                x = col * (self.tile_width + self.spacing) + self.margin
                y = row * (self.tile_height + self.spacing) + self.margin
                tile = self.image.subsurface(pygame.Rect(x, y, self.tile_width, self.tile_height))
                if self.colorkey: tile.set_colorkey(self.colorkey)
                self.tiles[tile_id] = tile
                tile_id += 1
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "image_path": self.image_path,
            "tile_width": self.tile_width,
            "tile_height": self.tile_height,
            "margin": self.margin,
            "spacing": self.spacing,
            "colorkey": (None if not self.colorkey else tuple(self.colorkey))
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Tileset":
        return Tileset(
            name=data["name"],
            t_type=data["type"],
            image_path=data["image_path"],
            tile_width=data["tile_width"],
            tile_height=data["tile_height"],
            margin=data["margin"],
            spacing=data["spacing"],
            colorkey=data["colorkey"]
        )
    
class Tileset_Encoder(json.JSONEncoder):
    def default(self, obj) -> dict | Any:
        if isinstance(obj, Tileset):
            return obj.to_dict()
        return super().default(obj)

def tileset_decoder(data: Any) -> Tileset:
    return Tileset.from_dict(data)
