import pygame
import pygame_gui
from typing import List

from .windows import Layer_Manager_Window

class Layer_Manager:
    def __init__(self) -> None:
        self.layers_render_order = []
        self.layers_data = {}

        self.selected_layer = None

        self.layer_manager_window = None
    
    def _layer_manager_window_callback(self, data: dict) -> None:

        if "add_layer" in data: self.add_layer(data["add_layer"])
        if "remove_layer" in data: self.remove_layer(data["remove_layer"]["name"])
        if "reorder_layers" in data: self.reorder_layers()
        if "selected_layer" in data: self.selected_layer = data["selected_layer"]["name"]

        print(data)
    
    def get_layer_render_number(self, layer_name: str) -> int | None:
        if layer_name not in self.layers_render_order: return
        return self.layers_render_order.index(layer_name)
    
    def get_layers_data(self) -> None:
        return self.layers_data.copy()
    
    def get_layers_render_order(self) -> List[str]:
        return self.layers_render_order
    
    def get_selected_layer(self) -> str | None:
        return self.selected_layer
    
    def add_layer(self, data: dict) -> None:
        name = data["name"]
        parallax = data["parallax"]
        self.layers_render_order.append(name)
        self.layers_data[name] = {"name": name, "on_grid": {}, "off_grid": [], "parallax": parallax, "render_number": self.get_layer_render_number(name)}
    
    def remove_layer(self, layer_name: str) -> None:
        if layer_name == self.selected_layer: self.selected_layer = None
        self.layers_render_order.remove(layer_name)
        del self.layers_data[layer_name]
    
    def reorder_layers(self) -> None:
        self.layers_render_order = self.layer_manager_window.get_order_list()

        for layer in self.layers_data:
            new_layer_render_number = self.layers_render_order.index(layer)
            self.layers_data[layer]["render_number"] = new_layer_render_number
    
    def launch_layer_manager_window(self, manager: pygame_gui.UIManager, rect: pygame.Rect, blocking: bool = True, *args, **kwargs) -> None:
        self.layer_manager_window = Layer_Manager_Window(manager=manager, rect=rect, starting_buttons=self.layers_render_order, starting_selected_button_text=self.selected_layer, callback=self._layer_manager_window_callback, *args, **kwargs)
        self.layer_manager_window.set_blocking(blocking)
    
    def process_event(self, event: pygame.Event) -> None:
        if self.layer_manager_window: self.layer_manager_window.custom_process_event(event) 