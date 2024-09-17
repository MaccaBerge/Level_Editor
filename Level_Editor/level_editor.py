import pygame
import pygame_gui
from sys import exit
from typing import List, Tuple

from scripts.components.file_manager_panel import File_Manager_Panel
from scripts.components.tile_selection_panel import Tile_Selection_Panel
from scripts.components.handy_bar_panel import Handy_Bar_Panel
from scripts.components.map_panel import Map_Panel
from scripts.windows import New_Tileset_Window
from scripts.tileset import Tileset, tileset_decoder
from scripts.utils.file import load_json_data_from_file_explorer
from scripts.tilemap import Tilemap

class Level_Editor:
    def __init__(self) -> None:
        self.screen_background_color = (39,48,54)#(33, 40, 45)
        self.screen_size = (1300, 750)
        self.screen_min_size = (1300, 750)
        self.screen_max_size = (2560, 1440)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE, vsync=1)
        pygame.display.set_caption("Level... Da Fuckin Editor")

        self.clock = pygame.time.Clock()
        self.target_fps = 60

        self.pygame_gui_manager = pygame_gui.UIManager(self.screen.get_size(), "styles/default.json")

        self.selected_drawing_tile_id = None

        self.deleting_tile = False

        self.tilesets = {}
        self.selected_tileset = None

        self.tile_size = 64
 
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        self.handy_bar_panel = Handy_Bar_Panel(
            manager=self.pygame_gui_manager, 
            relative_rect=pygame.Rect(0,0,self.screen.get_width(),50),
            callback=self._handy_bar_callback
        )
                
        self.file_manager_panel = File_Manager_Panel(
            manager=self.pygame_gui_manager, 
            position=(0, 50), 
            size=(300, self.screen.get_height() // 3.75),
            callback=self._file_manager_callback
            )
        
        self.tile_selection_panel = Tile_Selection_Panel(
            manager=self.pygame_gui_manager, 
            position=(0, self.screen.get_height() // 3), 
            size=(300, self.screen.get_height() - (self.screen.get_height() // 3)),
            callback=self._set_selected_drawing_tile_id
            )

        self.map_panel = Map_Panel(
            position=(302, 52),
            size=(self.screen.get_width() - 300-4, self.screen.get_height() - 50-4),
            border_width=0,
            color=pygame.Color(39,48,54),
            tile_size=self.tile_size
        )
    
    def _handy_bar_callback(self, button_text: str) -> None:
        match button_text:
            case "New Tileset":
                self.launch_new_tileset_window()
            case "Open Tileset":
                self.open_tileset()
            case "Open Image":
                print("Open Image")
            case "Open Layer Manager":
                self.launch_layer_manager_window()
    
    def _file_manager_callback(self, data: dict) -> None:
        if not isinstance(data, dict): return

        if "option_selected" in data:
            self._set_selected_tileset(data["option_selected"])
        if "option_deleted" in data:
            tileset_id = data["option_deleted"]
            self.tilesets.pop(tileset_id)
            self.tile_selection_panel.remove_tileset_images()
            self._set_selected_drawing_tile_id(None)
    
    def _set_selected_drawing_tile_id(self, tile_id: str | None) -> None:
        if self.selected_drawing_tile_id == tile_id: return
        self.selected_drawing_tile_id = tile_id
    
    def _set_selected_tileset(self, tileset_name: str) -> None:
        if tileset_name not in self.tilesets: return
        if self.tilesets[tileset_name] is self.selected_tileset: return
        
        self.selected_tileset: Tileset = self.tilesets[tileset_name]
        self.tile_selection_panel.set_tileset_images(self.selected_tileset.tiles) 
    
    def _hovering_window(self) -> bool:
        mouse_position = pygame.mouse.get_pos()
        for window in self.pygame_gui_manager.get_window_stack().get_full_stack():
            if window.rect.inflate(-30, -30).collidepoint(mouse_position):
                return True
        return False
    
    def _handle_new_screen_size(self, event: pygame.Event) -> None:
        new_size = max(min(event.x, self.screen_max_size[0]), self.screen_min_size[0]), max(min(event.y, self.screen_max_size[1]), self.screen_min_size[1])
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        self.pygame_gui_manager.set_window_resolution(new_size)
        
        self.tile_selection_panel.set_dimensions((self.tile_selection_panel.rect.width, new_size[1] - self.tile_selection_panel.rect.y))
        self.handy_bar_panel.set_dimensions((new_size[0], self.handy_bar_panel.relative_rect.height))
        self.map_panel.set_dimensions((new_size[0] - 300-4, new_size[1] - 50-4))
    
    def _handle_map_click(self, mouse_position: List[int] | Tuple[int]) -> None:
        if not self.deleting_tile:
            self.map_panel.add_tile({"type": self.selected_tileset.type, "variant": self.selected_drawing_tile_id, "image": self.get_current_drawing_tile()}, mouse_position)
        else:
            self.map_panel.remove_tile(mouse_position)
    
    def get_current_drawing_tile(self) -> pygame.Surface | None:
        if not self.selected_tileset: return
        if not self.selected_drawing_tile_id and self.selected_drawing_tile_id is not 0: return
        return self.selected_tileset.tiles[self.selected_drawing_tile_id]

    def launch_new_tileset_window(self) -> None:
        self.new_tileset_window = New_Tileset_Window(
            manager=self.pygame_gui_manager, 
            rect=pygame.Rect(self.screen.get_width() / 2 - 250, self.screen.get_height() / 2 - 200, 500, 400),
            tilesets=self.tilesets, 
            callback=self.add_tileset
        )
        self.new_tileset_window.set_blocking(True)
    
    def launch_layer_manager_window(self) -> None:
        self.map_panel.tilemap.layer_manager.launch_layer_manager_window(
            manager=self.pygame_gui_manager,
            rect=pygame.Rect(self.screen.get_width() / 2 - 250, self.screen.get_height() / 2 - 200, 500, 400),
            blocking=False
        )
    
    def open_tileset(self) -> None:
        tileset_object_data = load_json_data_from_file_explorer()

        if not tileset_object_data: return

        tileset_data = tileset_object_data["tileset_object"]
        
        tileset = tileset_decoder(tileset_data)
        self.add_tileset(tileset)
    
    def add_tileset(self, tileset: Tileset) -> None: # might add some error
        if not isinstance(tileset, Tileset): return

        self.tilesets[tileset.name] = tileset
        self.file_manager_panel.add_option(tileset.name)
   
    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.target_fps) / 1000

            self.screen.fill(self.screen_background_color)

            hovering_window = self._hovering_window()

            mouse_buttons = pygame.mouse.get_pressed()
            mouse_position = pygame.mouse.get_pos()

            if mouse_buttons[0] and self.map_panel.rect.collidepoint(mouse_position) and self.selected_drawing_tile_id is not None and not hovering_window:
                self._handle_map_click(mouse_position)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.WINDOWSIZECHANGED:
                    self._handle_new_screen_size(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.deleting_tile = not self.deleting_tile
                        
                self.map_panel.process_event(event)
                self.pygame_gui_manager.process_events(event)
            
            if self.map_panel.tilemap.layer_manager.layer_manager_window is not None:
                if self.map_panel.tilemap.layer_manager.layer_manager_window.alive(): self.handy_bar_panel.layers_button.disable()
                else: self.handy_bar_panel.layers_button.enable()

            self.map_panel.update(dt, deleting=self.deleting_tile, drawing_image=self.get_current_drawing_tile(), layer_selected=self.map_panel.tilemap.layer_manager.selected_layer)
            self.map_panel.render_map(self.screen)
        
            self.pygame_gui_manager.update(dt)
            self.pygame_gui_manager.draw_ui(self.screen)

            pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    level_editor = Level_Editor()
    level_editor.run()