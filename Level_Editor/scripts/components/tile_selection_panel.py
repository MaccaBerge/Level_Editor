import pygame
import pygame_gui
from typing import List, Tuple, Dict, Any, Callable

from ..widgets.image_button import Image_Button

class Tile_Selection_Panel(pygame_gui.elements.UIPanel):
    def __init__(self, manager: pygame_gui.UIManager, position: List[int] | Tuple[int], size: List[int] | Tuple[int], callback: Callable[[Any], Any] | None = None, *args, **kwargs) -> None:
        relative_rect = pygame.Rect(position, size)
        super().__init__(manager=manager, relative_rect=relative_rect, *args, **kwargs)
        self.callback = callback

        self.buttons = {}
        self.selected_button_id = None
        self.current_scrollbar_percentage = 0

        self._create_widgets()
    
    def _create_widgets(self) -> None:
        self.scrolling_container = pygame_gui.elements.UIScrollingContainer(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(0, 10, self.rect.width-10, self.rect.height-20),
            container=self,
            allow_scroll_x=False,
            allow_scroll_y=True,
            anchors={"top": "top", "bottom": "bottom", "left": "left", "right": "right"}
        )
        self.scrolling_container.vert_scroll_bar.top_button.kill()
        self.scrolling_container.vert_scroll_bar.bottom_button.kill()
        self.scrolling_container.vert_scroll_bar.arrow_button_height = 0
        self.scrolling_container.vert_scroll_bar.scroll_position -= 1
        self.scrolling_container.rebuild()

        self.no_content_label = pygame_gui.elements.UILabel(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(0, 0, -1, -1),
            text="Hmm... Looks like this is empty.",
            container=self
        )
        self.no_content_label.relative_rect.center = (self.scrolling_container.rect.width / 2, 20)
        self.no_content_label.rebuild()
        

    def _button_pressed_callback(self, button_id: str) -> None:
        self._select_button(button_id)
    
    def _select_button(self, button_id: str) -> None:
        selected_button: pygame_gui.elements.UIButton = self.buttons[button_id]
        selected_button.select()
        for image_button in self.buttons.values():
            if image_button != selected_button:
                image_button.unselect()

        if self.selected_button_id == button_id: return
        self.selected_button_id = button_id
        self.callback(button_id)
    
    def remove_tileset_images(self) -> None:
        for button in self.buttons.values():
            button.kill()
        self.buttons.clear()
    
    def set_tileset_images(self, tiles: Dict[int, pygame.Surface]) -> None:
        self.remove_tileset_images()
        self.selected_button_id = None

        for index, (image_id, image) in enumerate(tiles.items()):
            image_button = Image_Button(
                id=image_id, 
                image=image, 
                manager=self.ui_manager, 
                relative_rect=pygame.Rect((66)*(index % 3)+40, (index // 3) * (66) + 19, 64, 64),
                callback=self._button_pressed_callback,
                container=self.scrolling_container
            )
            
            self.buttons[image_id] = image_button
    
    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame.WINDOWSIZECHANGED:
            self.scrolling_container.vert_scroll_bar.set_scroll_from_start_percentage(self.scrolling_container.vert_scroll_bar.start_percentage)

        return super().process_event(event)
    
    def update(self, time_delta: float):
        if len(self.buttons) > 0:
            self.no_content_label.visible = False
        else:
            self.no_content_label.visible = True
        self.no_content_label.rebuild()

        return super().update(time_delta)
