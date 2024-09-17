
"""
The tilemap stores tiles in a dictionary. Tilemap structure:

    {"layer": {"on_grid": {}, "off_grid": [], "render_number": 0, "parallax": 1}}

    
The on_grid key stores tiles at grid positions. On_grid structure:

    {"tile_x;tile_y": {"type": "grass", "variant": 0, "position": "x;y"}}


The off_grid key stores tiles at a position. Off_grid structure:

    [{"type": "grass", "variant": 0, "position": "x;y"}]

"""

import pygame
from typing import List, Tuple

from .utils.file import save_json_data, load_json_data, save_as_json_data, load_json_data_from_file_explorer
from .layer_manager import Layer_Manager


class Tilemap:
    def __init__(self, tile_size: int) -> None:
        self.tile_size = tile_size

        self.layer_manager = Layer_Manager()
        self.tile_map = self.layer_manager.layers_data

        print(type(self.tile_map))

        try:
            self.tile_map_data_path = load_json_data("./caches/tile_map_data.json")["tile_map_data_path"]
            tile_map_data = load_json_data(self.tile_map_data_path)
            if tile_map_data: 
                self.layer_manager.layers_data = tile_map_data
                self.tile_map = self.layer_manager.layers_data 
        except:
            self.tile_map_data_path = None
    
    def _save_data(self) -> None:
        if self.tile_map_data_path:
            save_json_data(self.tile_map, self.tile_map_data_path)
        else:
            file_path = save_as_json_data(self.tile_map)
            self.tile_map_data_path = file_path if file_path else self.tile_map_data_path
            save_json_data({"tile_map_data_path": self.tile_map_data_path}, "./caches/tile_map_data")

    def _open_data(self) -> None:
        self.tile_map = load_json_data_from_file_explorer()
    
    def create_layer(self, layer_number: int) -> None:
        self.tile_map[str(layer_number)]
    
    def get_parallax_position(self, position: List[int | Tuple[int]], parallax: float | int) -> Tuple[int]:
        return (int(position[0] * parallax), int(position[1] * parallax))
    
    def get_selected_layer_parallax(self) -> float | None:
        if not self.layer_manager.get_layers_data(): return
        if not self.layer_manager.selected_layer: return
        return self.tile_map[self.layer_manager.get_selected_layer()]["parallax"]

    def get_grid_position(self, position: List[int | float] | Tuple[int | float]) -> Tuple[int]:
        return (position[0] // self.tile_size, position[1] // self.tile_size)

    def format_position(self, position: List[int | float] | Tuple[int | float]) -> str | None:
        if not isinstance(position, (list, tuple)): return

        return f"{int(position[0])};{int(position[1])}"
    
    def unformat_position(self, formatted_position: str) -> tuple | None:
        if not isinstance(formatted_position, str): return

        split_string = formatted_position.split(";")
        return (int(split_string[0]), int(split_string[1]))
    
    def add_tile(self, t_type: str, variant: str, position: List[int] | Tuple[int], image: pygame.Surface, alpha_image: pygame.Surface, on_grid: bool = True, world_offset: List[int] | Tuple[int] = (0,0)) -> None:
        layer = self.layer_manager.get_selected_layer()
        if not self.tile_map: return
        if layer not in self.tile_map: return

        image = pygame.transform.scale(image, (self.tile_size, self.tile_size)) # HAVE TO CHANGE THIS!!!
        alpha_image = pygame.transform.scale(alpha_image, (self.tile_size, self.tile_size)) # HAVE TO CHANGE THIS!!!

        layer_parallax = self.tile_map[layer]["parallax"]
        parallax_adjusted_position = (position[0] + (world_offset[0] * layer_parallax), position[1] + (world_offset[1] * layer_parallax))

        if on_grid:
            tile_grid_position = self.get_grid_position(parallax_adjusted_position)
            formatted_tile_position = self.format_position(tile_grid_position)
            if formatted_tile_position in self.tile_map[layer]["on_grid"]:
                del self.tile_map[layer]["on_grid"][formatted_tile_position]
            self.tile_map[layer]["on_grid"][formatted_tile_position] = {"type": t_type, "variant": variant, "position": tile_grid_position, "images": {"normal": image, "alpha": alpha_image}}
        else:
            for offgrid_tile in self.tile_map[layer]["off_grid"]:
                if offgrid_tile["position"] == parallax_adjusted_position: return
            self.tile_map[layer]["off_grid"].append({"type": t_type, "variant": variant, "position": parallax_adjusted_position, "images": {"normal": image, "alpha": alpha_image}})
    
    def remove_tile(self, position: List[int] | Tuple[int], on_grid: bool = True, world_offset: List[int] | Tuple[int] = (0,0), delete_overlapping_objects: bool = False) -> None:
        layer = self.layer_manager.get_selected_layer()
        if not self.tile_map: return
        if layer not in self.tile_map: return

        layer_parallax = self.tile_map[layer]["parallax"]
        parallax_adjusted_position = (position[0] + (world_offset[0] * layer_parallax), position[1] + (world_offset[1] * layer_parallax))

        if on_grid:
            tile_grid_position = self.get_grid_position(parallax_adjusted_position)
            formatted_tile_position = self.format_position(tile_grid_position)
            if formatted_tile_position in self.tile_map[layer]["on_grid"]:
                del self.tile_map[layer]["on_grid"][formatted_tile_position]
        else:
            pass
    
    def render_tilemap(self, render_surface: pygame.Surface, offset: List[int] | Tuple[int] = (0,0)) -> None:
        layers_render_order = self.layer_manager.get_layers_render_order()[::-1]
        selected_layer = self.layer_manager.get_selected_layer()
        
        for layer in layers_render_order:
            layer_parallax = self.tile_map[layer]["parallax"]
            render_offset = self.get_parallax_position(offset, layer_parallax)

            # off grid
            for tile in self.tile_map[layer]["off_grid"]:
                image = tile["images"]["normal" if layer == selected_layer else "alpha"]
                position = tile["position"]
                render_surface.blit(image, (position[0] - offset[0], position[1] - offset[1]))

            # on grid
            for x in range(render_offset[0] // self.tile_size, (render_offset[0] + render_surface.get_width()) // self.tile_size + 1):
                for y in range(render_offset[1] // self.tile_size, (render_offset[1] + render_surface.get_height()) // self.tile_size + 1):
                    tile_key = self.format_position((x, y))
                    layer_on_grid = self.tile_map[layer]["on_grid"]
                    if tile_key in layer_on_grid:
                        image = layer_on_grid[tile_key]["images"]["normal" if layer == selected_layer else "alpha"]
                        position = layer_on_grid[tile_key]["position"]
                        render_surface.blit(image, (position[0] * self.tile_size - render_offset[0], position[1] * self.tile_size - render_offset[1]))
            
    def process_event(self, event: pygame.Event) -> None:
        self.layer_manager.process_event(event)
    
    # def update(self) -> None:
    #     self.render_tilemap(pygame.Surface((1000, 1000)), (50, 50))
    #     #print(self.tile_map)
    #     print(self.layer_manager.layers_render_order)
