import pygame
import pygame_gui
import tkinter as tk
from tkinter import filedialog
import os
import json
from typing import Callable, List, Any, Tuple

from ..utils.other import tkinter_root_init


@tkinter_root_init
def load_image_from_file_explorer(valid_extentions: set = {".png", ".jpg", ".jpeg"}) -> Tuple[pygame.Surface] | Tuple[None]:
    from ..utils.file import is_valid_file_type

    filetypes = [("Image files", f"*{extention}") for extention in valid_extentions]
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    
    if not file_path: return (None, None)
    if not is_valid_file_type(file_path, valid_extentions): return (None, None)

    return (pygame.image.load(file_path).convert_alpha(), file_path)

@tkinter_root_init
def load_images_from_file_explorer(valid_extentions: set = {".png", ".jpg", ".jpeg"}) -> List[Tuple[pygame.Surface]] | List:
    from ..utils.file import is_valid_file_type
    filetypes = [("Image files", f"*{extention}") for extention in valid_extentions]
    file_paths = filedialog.askopenfilenames(filetypes=filetypes)

    if not file_paths: return []

    images_data = []
    for path in file_paths:
        if is_valid_file_type(path, valid_extentions):
            images_data.append((pygame.image.load(path).convert_alpha(), path))

    return images_data

def load_image(path: str, colorkey: pygame.Color = None, size: List[int] | Tuple[int] = None, size_multiplier: float | int = None) -> pygame.Surface | None:
    if not os.path.exists(path): return

    image = pygame.image.load(path).convert_alpha()

    if colorkey: image.set_colorkey(colorkey)
    if size: pygame.transform.scale(image, size)
    if size_multiplier and not size:
        original_size = image.get_size()
        pygame.transform.scale(image, (original_size[0] * size_multiplier, original_size[1] * size_multiplier))
    
    return image

def load_images(directory_path: str, colorkey: pygame.Color = None, size: List[int] | Tuple[int] = None, size_multiplier: float | int = None) -> List[pygame.Surface] | List[None]:
    if not os.path.exists(directory_path): return

    images = []

    for image_name in os.listdir(directory_path):
        image_path = os.path.join(directory_path, image_name)
        image = load_image(image_path, colorkey=colorkey, size=size, size_multiplier=size_multiplier)
        if image: images.append(image)
    
    return images




