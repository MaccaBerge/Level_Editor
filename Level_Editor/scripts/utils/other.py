import pygame
import pygame_gui
import tkinter as tk

from typing import Callable, Tuple, List

def tkinter_root_init(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        root = tk.Tk()
        root.withdraw()

        return_value = func(*args, **kwargs)

        root.destroy()

        return return_value
    
    return wrapper

def get_color_from_colorpicker(manager: pygame_gui.UIManager, rect: pygame.Rect, title: str = "Color Picker",*args, **kwargs) -> pygame.Color | None:
    color_picker = pygame_gui.windows.UIColourPickerDialog(
        manager=manager,
        rect=rect,
        window_title=title,
        *args,
        **kwargs
    )
    color_picker.set_blocking(True)

    
    for event in pygame.event.get():
        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            return event.colour

def throw_error_window(message: str, manager: pygame_gui.UIManager, rect: pygame.Rect) -> None:
    error_window = pygame_gui.windows.UIMessageWindow(rect, message, manager, window_title="Error Window", always_on_top=True)
    error_window.set_blocking(True)

def one_key_pressed(keys: List | Tuple) -> bool:
    pressed_keys = pygame.key.get_pressed()
    return any([pressed_keys[key] for key in keys])

def string_is_float(string: str) -> bool:
    try:
        string = float(string)
        return True
    except ValueError:
        return False