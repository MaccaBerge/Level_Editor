import pygame
import pygame_gui
import pygame_gui.elements.ui_scrolling_container
from typing import Any, Callable, Dict

from ..widgets.right_click_button import Right_Click_Button
from ..widgets.context_menu import Context_Menu
from ..tileset import Tileset


class File_Manager_Panel(pygame_gui.elements.UIPanel):
    def __init__(self, manager: pygame_gui.UIManager, position: list | tuple, size: list | tuple, callback: Callable[[Any], Any] | None = None, *args, **kwargs) -> None:
        super().__init__(
            manager=manager,
            relative_rect=pygame.Rect(position[0], position[1], size[0], size[1]),
            *args, 
            **kwargs
        )
        self.callback = callback

        self.vertical_scrollbar_last_state = False

        self.buttons = {}
        self.button_id_count = 0
        self.selected_button_id = None

        self._create_widgets()
        self.new_radio_button_size = (self.scrolling_container.rect.width-11, 30)

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
        self.scrolling_container.rebuild()

        self.no_content_label = pygame_gui.elements.UILabel(
            manager=self.ui_manager,
            relative_rect=pygame.Rect(0, 0, -1, -1),
            text="Hmm... Looks like this is empty.",
            container=self
        )
        self.no_content_label.relative_rect.center = (self.scrolling_container.rect.width / 2, 20)
        self.no_content_label.rebuild()
    
    def _context_menu_callback(self, context_menu_button_id: str) -> None:
        if context_menu_button_id == "delete":
            self.remove_option(self.selected_button_id)
    
    def _reload_option_stack(self, deleted_button_id: str) -> None:
        for button_id in [key for key in self.buttons.keys() if int(key) > int(deleted_button_id)]:
            button: Right_Click_Button = self.buttons[button_id]["button"]
            button.set_relative_position((button.relative_rect.x, button.relative_rect.y - 30))
        
    def add_option(self, callback_id: str) -> None:
        number_of_buttons = len(self.buttons)
        button_id = self.button_id_count
        self.button_id_count += 1

        button = Right_Click_Button(
            id=button_id,
            manager=self.ui_manager,
            relative_rect=pygame.Rect(10, (30)*number_of_buttons, self.new_radio_button_size[0], self.new_radio_button_size[1]),
            text=str(callback_id),
            container=self.scrolling_container,
            callback=self.option_right_clicked_callback,
            object_id="#radio_button",
            command=lambda _: self.option_pressed(button_id),
            anchors={
                "left": "left",
                "right": "right"
            }
        )
        
        self.buttons[button_id] = {"button": button, "callback_id": callback_id}
    
    def remove_option(self, button_id: str) -> None:
        self.callback({"option_deleted": self.buttons[button_id]["callback_id"]})
        self.buttons[button_id]["button"].kill()
        self.buttons.pop(button_id)
        self._reload_option_stack(button_id)
    
    def select_option(self, button_id: str) -> None:
        button: pygame_gui.elements.UIButton = self.buttons[button_id]["button"]
        button.border_width = 1
        button.text_horiz_alignment_padding = 9
        button.rebuild()
        button.select()
        self.selected_button_id = button_id
        for other_button in (dict_["button"] for dict_ in self.buttons.values()):
            if other_button != button:
                other_button.unselect()
                other_button.border_width = 0
                button.text_horiz_alignment_padding = 10
                other_button.rebuild()
        
        if self.callback: self.callback({"option_selected": self.buttons[button_id]["callback_id"]})
    
    def option_pressed(self, button_id: str) -> None:
        self.select_option(button_id)
    
    def option_right_clicked_callback(self, button_id: Any) -> None:
        self.select_option(button_id)
        mouse_position = pygame.mouse.get_pos()
        self.context_menu = Context_Menu(
            manager=self.ui_manager, 
            relative_rect=pygame.Rect(mouse_position[0], mouse_position[1], 100, 32), 
            callback=self._context_menu_callback
        )
    
    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame.WINDOWSIZECHANGED:
            self.scrolling_container.vert_scroll_bar.set_scroll_from_start_percentage(self.scrolling_container.vert_scroll_bar.start_percentage)

        return super().process_event(event)
    
    def update(self, time_delta: float) -> None:
        super().update(time_delta)

        vertical_scrollbar_current_state = self.scrolling_container.vert_scroll_bar.is_enabled

        # i know its bad code, i am just too fuckin lazy right now (ok?)
        if vertical_scrollbar_current_state and not self.vertical_scrollbar_last_state:
            for button in (dict_["button"] for dict_ in self.buttons.values()):
                self.new_radio_button_size = (self.scrolling_container.rect.width-10-25, 30)
                button.set_dimensions(self.new_radio_button_size)
        elif not vertical_scrollbar_current_state and self.vertical_scrollbar_last_state:
            for button in (dict_["button"] for dict_ in self.buttons.values()):
                self.new_radio_button_size = (self.scrolling_container.rect.width-11, 30)
                button.set_dimensions(self.new_radio_button_size)

        self.vertical_scrollbar_last_state = vertical_scrollbar_current_state

        if len(self.buttons) > 0:
            self.no_content_label.visible = False
        else:
            self.no_content_label.visible = True
        self.no_content_label.rebuild()