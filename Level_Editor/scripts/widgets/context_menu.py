import pygame
import pygame_gui
from typing import Callable, Any

class Context_Menu(pygame_gui.elements.UIPanel):
    def __init__(self, manager: pygame_gui.UIManager, relative_rect: pygame.Rect, callback: Callable[[Any], None], starting_height: int = 100, *args, **kwargs) -> None:
        super().__init__(manager=manager, relative_rect=relative_rect, starting_height=starting_height, *args, **kwargs)
        self.callback = callback

        self.add_widgets()
    
    def add_widgets(self) -> None:
        self.delete_button = pygame_gui.elements.UIButton(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(6,6, self.relative_rect.width, -1),
            text="Delete",
            container=self,
            command=lambda _: self.button_pressed("delete"),
            object_id="#radio_button"
        )
    
    def button_pressed(self, button_id: str) -> None:
        if button_id == "delete":
            self.callback(button_id)
        self.kill()
    
    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.kill()

        return super().process_event(event)