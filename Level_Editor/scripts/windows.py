import pygame
import pygame_gui
import os
from typing import Any, Callable, Dict, List

from .widgets.changing_color_button import Changing_Color_Button
from .widgets.order_list import Order_List
from .tileset import Tileset
from .utils.file import get_save_path_from_file_explorer, save_json_data
from .utils.image import load_image_from_file_explorer
from .utils.other import throw_error_window
from .utils.other import string_is_float

class Custom_Window(pygame_gui.elements.UIWindow):
    def __init__(self, manager, rect, *args, **kwargs) -> None:
        super().__init__(manager=manager, rect=rect, *args, **kwargs)

        self.last_position = self.rect.center
        current_position = self.rect.center
        self.relative_position_to_screen = (current_position[0] / pygame.display.get_surface().get_width(), current_position[1] / pygame.display.get_surface().get_height())

        self.window_closed = False
    
    def on_close_window_button_pressed(self):
        self.window_closed = True
        #self.kill()
        return super().on_close_window_button_pressed()
    
    def custom_process_evnets(self, event: pygame.Event) -> None:
        if event.type == pygame.WINDOWSIZECHANGED:
            self.set_position((self.relative_position_to_screen[0] * event.x - (self.rect.width / 2), self.relative_position_to_screen[1] * event.y - (self.rect.height / 2)))
    
    def process_event(self, event: pygame.Event) -> bool:
        self.custom_process_evnets(event)
        return super().process_event(event)
    
    def update(self, time_delta: float):
        super().update(time_delta)

        current_position = self.rect.center

        if self.last_position != current_position:
            self.relative_position_to_screen = (current_position[0] / pygame.display.get_surface().get_width(), current_position[1] / pygame.display.get_surface().get_height())
        
        self.last_position = current_position

        screen_size = pygame.display.get_surface().get_size()
        if self.rect.right > screen_size[0]+10:
            self.set_position((screen_size[0]-self.rect.width+10, self.rect.y))
        if self.rect.left < 0-10:
            self.set_position((0-10, self.rect.y))

        if self.rect.bottom > screen_size[1]+10:
            self.set_position((self.rect.x, screen_size[1] - self.rect.height+10))
        if self.rect.top < 0-10:
            self.set_position((self.rect.x, 0-10))


class New_Tileset_Window(Custom_Window): 
    def __init__(self, manager: pygame_gui.UIManager, rect: pygame.Rect, tilesets: Dict[str, Tileset], callback: Callable[[Any], Any] | None = None, *args, **kwargs) -> None:
        super().__init__(manager=manager, rect=rect, window_display_title="New Tileset", *args, **kwargs)
        self.manager = manager
        self.given_rect = rect
        self.tilesets = tilesets
        
        self.callback = callback
        self.screen = pygame.display.get_surface()

        self.create_widgets()

        self.default_colorkey_color = (0,0,0)
        self.colorkey_color = self.default_colorkey_color
    
    def create_widgets(self) -> None:
            # tileset
        tileset_panel_rect = pygame.Rect(10, 50-20, self.given_rect.width - 20, 55+40)
        self.tileset_panel = pygame_gui.elements.UIPanel(
            relative_rect=tileset_panel_rect,
            manager=self.ui_manager,
            container=self,
            object_id="#panel_in_window"
        )

        tileset_panel_text_rect = pygame.Rect(tileset_panel_rect.left + 1, tileset_panel_rect.top - 23, -1, -1)
        self.tileset_panel_text = pygame_gui.elements.UILabel(
            relative_rect=tileset_panel_text_rect,
            manager=self.ui_manager,
            container=self,
            text="Tileset",
        )

        name_entry_text_rect = pygame.Rect(15, 14, -1, -1)
        self.name_entry_text = pygame_gui.elements.UILabel(
            relative_rect=name_entry_text_rect,
            manager=self.ui_manager,
            container=self.tileset_panel,
            text="Name:"
        )

        name_entry_rect = pygame.Rect(70, 10, tileset_panel_rect.width - 79, -1)
        self.name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=name_entry_rect, 
            manager=self.ui_manager, 
            container=self.tileset_panel,
            object_id="#entry_in_window"
        )

        type_entry_text_rect = pygame.Rect(15, 14+40, -1, -1)
        self.type_entry_text = pygame_gui.elements.UILabel(
            relative_rect=type_entry_text_rect,
            manager=self.ui_manager,
            container=self.tileset_panel,
            text="Type:"
        )

        type_entry_rect = pygame.Rect(70, 50, tileset_panel_rect.width - 79, -1)
        self.type_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=type_entry_rect, 
            manager=self.ui_manager, 
            container=self.tileset_panel,
            object_id="#entry_in_window"
        )

        # image
        image_panel_rect = pygame.Rect(10, tileset_panel_rect.bottom + 50-20, self.given_rect.width - 20, 175)
        self.image_panel = pygame_gui.elements.UIPanel(
            relative_rect=image_panel_rect,
            manager=self.ui_manager,
            container=self,
            object_id="#panel_in_window"
        )
        
        image_panel_text_rect = pygame.Rect(image_panel_rect.left + 1, image_panel_rect.top - 23, -1, -1)
        self.image_panel_text = pygame_gui.elements.UILabel(
            relative_rect=image_panel_text_rect,
            manager=self.ui_manager,
            container=self,
            text="Image",
        )

            # source
        source_entry_text_rect = pygame.Rect(15, 14, -1, -1)
        self.source_entry_text = pygame_gui.elements.UILabel(
            relative_rect=source_entry_text_rect,
            manager=self.ui_manager,
            container=self.image_panel,
            text="Source:"
        )

        source_entry_rect = pygame.Rect(70+10, 10, tileset_panel_rect.width - 151-10, -1)
        self.source_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=source_entry_rect, 
            manager=self.ui_manager, 
            container=self.image_panel,
            object_id="#entry_in_window"
        )

        brows_button_rect = pygame.Rect(source_entry_rect.right + 3, source_entry_rect.top, 69, 31)
        self.brows_button = pygame_gui.elements.UIButton(
            relative_rect=brows_button_rect,
            manager=self.ui_manager,
            container=self.image_panel,
            text="Brows..."
        )

        # colorkey
        colorkey_dropdown_menu_text_rect = pygame.Rect(15, 14+38, -1, -1)
        self.colorkey_dropdown_menu_text = pygame_gui.elements.UILabel(
            relative_rect=colorkey_dropdown_menu_text_rect,
            manager=self.ui_manager,
            container=self.image_panel,
            text="Colorkey:"
        )

        colorkey_dropdown_menu_rect = pygame.Rect(70+10, source_entry_rect.top + 40, 150, 30)
        self.colorkey_dropdown_menu = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(colorkey_dropdown_menu_rect),
            manager=self.ui_manager,
            container=self.image_panel,
            options_list=[("Colorkey off", "0"), ("Colorkey on", "1")],
            starting_option=("Colorkey off", "0"),
        )

        colorkey_color_button_rect = pygame.Rect(colorkey_dropdown_menu_rect.right + 3, colorkey_dropdown_menu_rect.top, 50, colorkey_dropdown_menu_rect.height)
        self.colorkey_color_button = Changing_Color_Button(
            relative_rect=colorkey_color_button_rect,
            manager=self.ui_manager,
            container=self.image_panel,
            text=""
        )
        self.colorkey_color_button.disable()

        tile_width_text_rect = pygame.Rect(15, source_entry_rect.top + 92, -1, -1)
        self.tile_width_text = pygame_gui.elements.UILabel(
            relative_rect=tile_width_text_rect,
            manager=self.ui_manager,
            container=self.image_panel,
            text="Tile width:"
        )

        # tile spesifications
        tile_width_entry_rect = pygame.Rect(70+25, source_entry_rect.top + 90, 60, 30)
        self.tile_width_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=tile_width_entry_rect, 
            manager=self.ui_manager, 
            container=self.image_panel,
            object_id="#entry_in_window",
            initial_text="32"
        )

        tile_height_text_rect = pygame.Rect(15, source_entry_rect.top + 127, -1, -1)
        self.colorkey_dropdown_menu_text = pygame_gui.elements.UILabel(
            relative_rect=tile_height_text_rect,
            manager=self.ui_manager,
            container=self.image_panel,
            text="Tile height:"
        )

        tile_height_entry_rect = pygame.Rect(70+25, source_entry_rect.top + 125, 60, 30)
        self.tile_height_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=tile_height_entry_rect, 
            manager=self.ui_manager, 
            container=self.image_panel,
            object_id="#entry_in_window",
            initial_text="32"
        )

        margin_text_rect = pygame.Rect(15 + 170, source_entry_rect.top + 92, -1, -1)
        self.margin_text = pygame_gui.elements.UILabel(
            relative_rect=margin_text_rect,
            manager=self.ui_manager,
            container=self.image_panel,
            text="Margin:"
        )

        margin_entry_rect = pygame.Rect(70+25+ 150+2, source_entry_rect.top + 90, 60, 30)
        self.margin_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=margin_entry_rect, 
            manager=self.ui_manager, 
            container=self.image_panel,
            object_id="#entry_in_window",
            initial_text="0"
        )

        
        spacing_text_rect = pygame.Rect(15 + 170, source_entry_rect.top + 127, -1, -1)
        self.spacing_text = pygame_gui.elements.UILabel(
            relative_rect=spacing_text_rect,
            manager=self.ui_manager,
            container=self.image_panel,
            text="Spacing:"
        )

        spacing_entry_rect = pygame.Rect(70+25 + 150+2, source_entry_rect.top + 125, 60, 30)
        self.spacing_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=spacing_entry_rect, 
            manager=self.ui_manager, 
            container=self.image_panel,
            object_id="#entry_in_window",
            initial_text="0"
        )

        # decition buttons
        cancel_button_rect = pygame.Rect(image_panel_rect.right - 100, image_panel_rect.bottom + 5, 100, 30)
        self.cancel_button = pygame_gui.elements.UIButton(
            relative_rect=cancel_button_rect,
            manager=self.ui_manager,
            container=self,
            text="Cancel"
        )

        save_as_button_rect = pygame.Rect(image_panel_rect.right - 205, image_panel_rect.bottom + 5, 100, 30)
        self.save_as_button = pygame_gui.elements.UIButton(
            relative_rect=save_as_button_rect,
            manager=self.ui_manager,
            container=self,
            text="Save As..."
        )
    
    def _can_save(self) -> bool:
        name_entry_text = self.name_entry.get_text()
        type_entry_text = self.type_entry.get_text()
        source_entry_text = self.source_entry.get_text()
        tile_width_entry_text = self.tile_width_entry.get_text()
        tile_height_entry_text = self.tile_height_entry.get_text()
        margin_entry_text = self.margin_entry.get_text()
        spacing_entry_text = self.spacing_entry.get_text()

        if (name_entry_text.isspace() or name_entry_text == "" or name_entry_text in self.tilesets): return False
        if (source_entry_text.isspace() or source_entry_text == ""): return False
        if (type_entry_text.isspace() or type_entry_text == ""): return False
        if (tile_width_entry_text.isspace() or tile_width_entry_text == "" or (not tile_width_entry_text.isnumeric())): return False
        if (tile_height_entry_text.isspace() or tile_height_entry_text == "" or (not tile_height_entry_text.isnumeric())): return False
        if (not margin_entry_text.isnumeric()): return False
        if (not spacing_entry_text.isnumeric()): return False

        return True

    def create_color_picker(self) -> pygame_gui.windows.UIColourPickerDialog: 
        width = 390
        height = 390
        centerx = self.screen.get_width() / 2 - (width / 2)
        centery = self.screen.get_height() / 2 - (height / 2)
        rect=pygame.Rect(centerx, centery, width, height)
        self.color_picker = pygame_gui.windows.UIColourPickerDialog(
            rect=rect,
            window_title="Color Picker",
        )
        self.color_picker.set_blocking(True)

    def create_and_save_tileset(self) -> Tileset:
        source_entry_text = self.source_entry.get_text()
        if not os.path.exists(source_entry_text):
            throw_error_window(f"Failed to load tileset image '{source_entry_text}'", self.manager, pygame.Rect(200, 200, 400, 400))
            return
        
        save_directory_path = get_save_path_from_file_explorer()

        if not save_directory_path: return

        tileset = Tileset(name=self.name_entry.get_text(), t_type=self.type_entry.get_text(), image_path=source_entry_text, tile_width=int(self.tile_width_entry.get_text()), tile_height=int(self.tile_height_entry.get_text()), 
                          margin=int(self.margin_entry.get_text()), spacing=int(self.spacing_entry.get_text()), colorkey=self.colorkey_color if self.colorkey_dropdown_menu.selected_option == ("Colorkey on", "1") else None)
        
        # have to save the tileset object to its directory
        save_json_data({"tileset_object": tileset}, os.path.join(save_directory_path, tileset.name))
        
        return tileset
        
    def process_event(self, event: pygame.Event) -> bool:
        consumed_event = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.brows_button:
                image, path = load_image_from_file_explorer()
                if path: self.source_entry.set_text(path)
            if event.ui_element == self.colorkey_color_button:
                self.create_color_picker()
            if event.ui_element == self.cancel_button:
                self.kill()
            if event.ui_element == self.save_as_button:
                tileset = self.create_and_save_tileset()
                if tileset: 
                    if self.callback: self.callback(tileset)
                    self.kill()
            
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.colorkey_dropdown_menu:
                if event.selected_option_id == "0":
                    self.colorkey_color_button.disable()
                elif event.selected_option_id == "1":
                    self.colorkey_color_button.enable()
        
        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            color = event.colour
            if color: self.colorkey_color_button.set_color(color)
        
        return consumed_event
    
    def update(self, time_delta: float) -> None:
        super().update(time_delta)

        if hasattr(self, "color_picker"):
            new_color = self.color_picker.get_colour()
            self.colorkey_color_button.set_color(new_color)
            self.colorkey_color = new_color
        
        if self._can_save():
            self.save_as_button.enable()
        else:
            self.save_as_button.disable()

class Layer_Manager_Window(Custom_Window):
    def __init__(self, manager: pygame_gui.UIManager, rect: pygame.Rect, starting_buttons: List[str] = None, starting_selected_button_text: str | None = None, 
                 callback: Callable[[dict], Any] = None, *args, **kwargs) -> None:
        super().__init__(manager=manager, rect=rect, window_display_title="Layer Manager", *args, **kwargs)
        self.callback = callback
        self.starting_buttons = starting_buttons
        self.starting_selected_button_text = starting_selected_button_text
        self._create_widgets()

    def _create_widgets(self) -> None:
        self.order_list = Order_List(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(10, 60, self.rect.width-52, self.rect.height-130),
            container=self,
            callback=self._order_list_callback,
            starting_buttons=self.starting_buttons,
            starting_selected_button_text=self.starting_selected_button_text
        )

        self.create_layer_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(10,30, -1, 30),
            text="New Layer",
            container=self
        )
        self.new_layer_window = None
    
    def _trigger_callback(self, data: dict) -> None:
        if not isinstance(data, dict): return

        self.callback(data)
    
    def _new_layer_window_callback(self, data: Dict) -> None:
        if not isinstance(data, dict): return

        layer_name = data["name"]
        layer_parallax = data["parallax"]

        self.add_layer(layer_name, layer_parallax)

    def _order_list_callback(self, data: dict) -> None:
        if not isinstance(data, dict): return

        if "remove_layer" in data: self._trigger_callback({"remove_layer": {"name": data["remove_layer"]["name"]}})
        if "reorder_layers" in data: self._trigger_callback({"reorder_layers": None})
        if "selected_layer" in data: self._trigger_callback({"selected_layer": {"name": data["selected_layer"]["name"]}})
    
    def add_layer(self, name: str, parallax: str) -> None:
        self.order_list.add_button(name)
        self._trigger_callback({"add_layer": {"name": name, "parallax": parallax}})
        
    def get_order_list(self) -> None:
        return self.order_list.get_order_list()
    
    def launch_new_layer_window(self) -> None:
        self.new_layer_window = New_Layer_Window(
            manager=self.ui_manager, 
            rect=pygame.Rect(pygame.display.get_surface().get_width() / 2 - 250, pygame.display.get_surface().get_height() / 2 - 85, 500, 170),
            callback=self._new_layer_window_callback,
            exclude_words=[button.text for button in self.order_list.buttons]
            )
        self.new_layer_window.set_blocking(True)
        self.new_layer_window.change_layer(30)
    
    def custom_process_event(self, event: pygame.Event) -> None:
        if self.window_closed: return
        
        if not self.new_layer_window:
            self.order_list.handle_event(event)
        elif not self.new_layer_window.groups():
            self.order_list.handle_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.create_layer_button:
                self.launch_new_layer_window()

class New_Layer_Window(Custom_Window):
    def __init__(self, manager: pygame_gui.UIManager, rect, exclude_words: list = [], callback: Callable[[dict], None] = None, *args, **kwargs) -> None:
        super().__init__(manager=manager, rect=rect,  window_display_title="New Layer", *args, **kwargs)
        self.given_rect = rect
        self.exclude_words = exclude_words
        self.callback = callback

        self._create_widgets()

    def _create_widgets(self) -> None:
        layer_panel_rect = pygame.Rect(9, 11, self.given_rect.width - 20, 90)
        self.layer_panel = pygame_gui.elements.UIPanel(
            relative_rect=layer_panel_rect,
            manager=self.ui_manager,
            container=self,
            object_id="#panel_in_window"
        )

        name_entry_text_rect = pygame.Rect(15, 14, -1, -1)
        self.name_entry_text = pygame_gui.elements.UILabel(
            relative_rect=name_entry_text_rect,
            manager=self.ui_manager,
            container=self.layer_panel,
            text="Name:"
        )

        name_entry_rect = pygame.Rect(70+10, 10, layer_panel_rect.width - 79-10, -1)
        self.name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=name_entry_rect, 
            manager=self.ui_manager, 
            container=self.layer_panel,
            object_id="#entry_in_window"
        )

        parallax_entry_rect = pygame.Rect(80, 50, 60, 30)
        self.parallax_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=parallax_entry_rect, 
            manager=self.ui_manager, 
            container=self.layer_panel,
            object_id="#entry_in_window",
            initial_text="1"
        )

        parallax_entry_text_rect = pygame.Rect(15, 52, -1, -1)
        self.parallax_entry_text = pygame_gui.elements.UILabel(
            relative_rect=parallax_entry_text_rect,
            manager=self.ui_manager,
            container=self.layer_panel,
            text="Parallax:"
        )

        cancel_button_rect = pygame.Rect(layer_panel_rect.right - 100, layer_panel_rect.bottom + 5, 100, 30)
        self.cancel_button = pygame_gui.elements.UIButton(
            relative_rect=cancel_button_rect,
            manager=self.ui_manager,
            container=self,
            text="Cancel"
        )

        create_button_rect = pygame.Rect(layer_panel_rect.right - 205, layer_panel_rect.bottom + 5, 100, 30)
        self.create_button = pygame_gui.elements.UIButton(
            relative_rect=create_button_rect,
            manager=self.ui_manager,
            container=self,
            text="Create"
        )
    
    def _call_callback(self, data: Any) -> None:
        if not self.callback: return

        self.callback(data)
    
    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element is self.create_button:
                layer_name = self.name_entry.get_text()
                parallax = float(self.parallax_entry.get_text())
                callback_data = {"name": layer_name, "parallax": parallax}
                self._call_callback(callback_data)
                self.kill()
            if event.ui_element is self.cancel_button:
                self.kill()

        return super().process_event(event)

    def update(self, time_delta: float):
        name_entry_text = self.name_entry.get_text()
        parallax_entry_text = self.parallax_entry.get_text()
        if (name_entry_text.isspace() or name_entry_text == "") or (parallax_entry_text.isspace() or parallax_entry_text == "" or not string_is_float(parallax_entry_text)) or (name_entry_text in self.exclude_words): 
            self.create_button.disable()
        else:
            self.create_button.enable()
        
        return super().update(time_delta)

    