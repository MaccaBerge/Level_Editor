import pygame
import pygame_gui
from typing import Callable, Any

class Right_Click_Button(pygame_gui.elements.UIButton):
    def __init__(self, id: Any, manager: pygame_gui.UIManager, relative_rect: pygame.Rect, text: str, container:  pygame_gui.elements.UIPanel = None, callback: Callable = None, *args, **kwargs) -> None:
        super().__init__(manager=manager, relative_rect=relative_rect, text=text, container=container, *args, **kwargs)
        self.container = container
        self.id = id
        self.callback = callback
    
    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3 and self.rect.collidepoint(event.pos) and self.container.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback(self.id)
                return True

        return super().process_event(event)