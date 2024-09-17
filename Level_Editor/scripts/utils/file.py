import pygame
import tkinter as tk
from tkinter import filedialog
import os
import json
from typing import Any, Callable

from ..tileset import Tileset_Encoder
from ..utils.other import tkinter_root_init

def is_valid_file_type(path: str, valid_extentions: set) -> bool:
    return os.path.splitext(path)[1].lower() in valid_extentions

def save_json_data(data: Any, path: str, extention: str = ".json") -> bool:
    if not path.endswith(extention): path = path + extention
    try:
        with open(path, "w") as file:
            json.dump(data, file, cls=Tileset_Encoder, indent=4)
        return True
    except Exception as e:
        print(f"Error saving JSON file: {e}")

    return False

def load_json_data(path: str, extention: str = ".json") -> Any | None:
    if not path.endswith(extention): path = path + extention
    try:
        with open(path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")

@tkinter_root_init
def save_as_json_data(data: Any) -> str:
    file_path = filedialog.asksaveasfilename(title="Save JSON File", filetypes=[("json files (*json)", "*.json")], defaultextension=".json")

    if not file_path: return

    if not save_json_data(data, file_path):
        print("JSON file not saved.")

    return file_path

@tkinter_root_init
def load_json_data_from_file_explorer() -> Any | None:
    file_path = filedialog.askopenfilename(title="Open JSON File", filetypes=[("json files (*json)", "*.json")])

    if not file_path: return
    if not is_valid_file_type(file_path, [".json"]): return

    return load_json_data(file_path)

def get_save_path_from_file_explorer() -> str | None:
    file_path = filedialog.askdirectory()
    
    if not file_path: return 

    return file_path
