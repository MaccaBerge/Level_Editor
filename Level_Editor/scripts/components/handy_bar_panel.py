import pygame
import pygame_gui
from typing import Callable, Any

class Handy_Bar_Panel(pygame_gui.elements.UIPanel):
    def __init__(self, manager: pygame_gui.UIManager, relative_rect: pygame.Rect, callback: Callable[[Any], Any] | None = None) -> None:
        super().__init__(manager=manager, relative_rect=relative_rect)
        self.callback = callback

        self._create_widgets()
    
    def _create_widgets(self) -> None:
        self.new_file_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(9,11,-1,-1),
            text="New File",
            container=self
        )

        self.open_file_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(self.new_file_button.rect.right+2,11,-1,-1),
            text="Open File",
            container=self
        )

        self.save_file_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(self.open_file_button.rect.right+2,11,-1,-1),
            text="Save File",
            container=self
        )

        self.new_tileset_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(300,11,-1,-1),
            text="New Tileset",
            container=self
        )

        self.open_tileset_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(114+300-9,11,-1,-1),
            text="Open Tileset",
            container=self
        )

        self.open_image_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(227+300-9,11,-1,-1),
            text="Open Image",
            container=self
        )

        self.layers_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(0,11,-1,-1),
            text="Open Layer Manager",
            container=self,
            anchors={"left": "right"}
        )
    
    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self.callback:
                if event.ui_element in (self.new_tileset_button, self.open_tileset_button, self.open_image_button, self.layers_button):
                    self.callback(event.ui_element.text)
                    return True

        return super().process_event(event)

        