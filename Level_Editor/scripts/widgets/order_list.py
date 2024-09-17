import pygame
import pygame_gui
from random import randint
from typing import Any, Callable, List

from .draggeble_button import DraggableButton
from .context_menu import Context_Menu

class Order_List(pygame_gui.elements.UIPanel):
    def __init__(self, relative_rect, manager, starting_buttons: List[str] = None, starting_selected_button_text: str | None = None, 
                 callback: Callable[[dict], Any] = None, *args, **kwargs):
        super().__init__(relative_rect, manager=manager, starting_height=1, *args, **kwargs)
        self.manager = manager
        self.starting_buttons = starting_buttons
        self.starting_selected_button_text = starting_selected_button_text
        self.callback = callback
        
        self.scroll_panel = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 10, relative_rect.width-20, relative_rect.height-20),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
            allow_scroll_x=False
        )
        
        self.buttons = []
        self.selected_button = None
        self.button_height = 30
        self.dragged_button: DraggableButton = None
        self.animation_duration = 0.1  # duration of the animation in seconds

        self.dragged_button_last_index = None

        if self.starting_buttons: self._add_starting_buttons(self.starting_buttons)
        for button in self.buttons:
            if button.text == self.starting_selected_button_text:
                self.select_button(button)
                break
    
    def _trigger_callback(self, data: dict) -> None:
        if not self.callback: return

        self.callback(data)
    
    def _button_callback(self, id: int) -> None:
        mouse_position = pygame.mouse.get_pos()
        self.context_menu = Context_Menu(
            manager=self.ui_manager, 
            relative_rect=pygame.Rect(mouse_position[0], mouse_position[1], 100, 32), 
            callback=self._context_menu_callback
        )
    
    def _context_menu_callback(self, context_menu_button_id: str) -> None:
        if context_menu_button_id == "delete":
            self.remove_button(self.selected_button)
    
    def _add_starting_buttons(self, starting_buttons: List[str]) -> None:
        for button_text in starting_buttons:
            self.add_button(button_text, starting_button=True)

    def _check_for_reorder(self):
        if not self.dragged_button:
            return
    
        dragged_button_index = self.buttons.index(self.dragged_button)
        dragged_button_rect = self.dragged_button.rect

        if dragged_button_index == 0 and (self.dragged_button_last_index != dragged_button_index):
            self._reorder_buttons()
            self._trigger_reposition_animation()
        self.dragged_button_last_index = dragged_button_index

        for i, button in enumerate(self.buttons):
            if button is self.dragged_button or button.is_animating:
                continue

            button_rect = button.rect

            if i < dragged_button_index and dragged_button_rect.top < button_rect.centery:
                # Move dragged button up in the stack when it surpasses the top half of the above button
                self._shift_buttons(dragged_button_index, i)
                break
            elif i > dragged_button_index and dragged_button_rect.bottom > button_rect.centery:
                # Move dragged button down in the stack when it surpasses the bottom half of the below button
                self._shift_buttons(dragged_button_index, i)
                break

    def _shift_buttons(self, start_index, end_index):
        dragged_button = self.buttons[start_index]

        if start_index < end_index:
            # Moving down: Shift other buttons up
            for i in range(start_index, end_index):
                self.buttons[i] = self.buttons[i + 1]
                self.buttons[i].animation_start_time = pygame.time.get_ticks() / 1000.0  # Set individual animation time
                self.buttons[i].is_animating = True  # Set animating flag
        else:
            # Moving up: Shift other buttons down
            for i in range(start_index, end_index, -1):
                self.buttons[i] = self.buttons[i - 1]
                self.buttons[i].animation_start_time = pygame.time.get_ticks() / 1000.0  # Set individual animation time
                self.buttons[i].is_animating = True  # Set animating flag

        # Place the dragged button in its new position
        self.buttons[end_index] = dragged_button
        self._reorder_buttons()
        dragged_button.animation_start_time = pygame.time.get_ticks() / 1000.0  # Set the animation time for the dragged button
        dragged_button.is_animating = True  # Set animating flag

        self._trigger_callback({"reorder_layers": None})

    def _reorder_buttons(self):
        for i, button in enumerate(self.buttons):
            button.target_position = (0, i * self.button_height)
            button.original_position = button.relative_rect.topleft

    def _trigger_reposition_animation(self):
        current_time = pygame.time.get_ticks() / 1000.0
        for button in self.buttons:
            button.original_position = button.relative_rect.topleft
            button.animation_start_time = current_time
            button.is_animating = True

    def _update_button_positions(self, time_delta):
        current_time = pygame.time.get_ticks() / 1000.0

        for button in self.buttons:
            if button.animation_start_time is None or button is self.dragged_button:
                continue
            
            elapsed_time = current_time - button.animation_start_time
            
            if elapsed_time > self.animation_duration:
                elapsed_time = self.animation_duration

            progress = elapsed_time / self.animation_duration

            start_x, start_y = button.original_position
            target_x, target_y = button.target_position

            new_x = start_x + (target_x - start_x) * self._ease_out_quad(progress)
            new_y = start_y + (target_y - start_y) * self._ease_out_quad(progress)

            button.set_relative_position((new_x, new_y))

            if progress >= 1.0:
                button.animation_start_time = None  # Stop animation for this button
                button.is_animating = False  # Reset animating flag

    def _ease_out_quad(self, t):
        return t * (2 - t)

    def add_button(self, button_text: str, starting_button: bool = False) -> None:
        button = DraggableButton(
            id=None,
            relative_rect=pygame.Rect(0, len(self.buttons) * self.button_height, self.scroll_panel.rect.width - 20, self.button_height),
            text=button_text,
            manager=self.ui_manager,
            container=self.scroll_panel,
            object_id="#radio_button",
            callback=self._button_callback
        )
        button.target_position = button.relative_rect.topleft
        button.animation_start_time = None  # Each button has its own animation start time
        button.is_animating = False  # Flag to indicate if the button is animating
        self.buttons.append(button)

        if not starting_button: self.select_button(button)
    
    def remove_random_button(self) -> None:
        if not self.buttons: return

        removed_button = self.buttons.pop(randint(0, len(self.buttons)-1))  # Remove the button from the list
        if removed_button is self.selected_button: self.selected_button = None
        button_text = removed_button.text
        removed_button.kill()  # Kill the button (remove it from the UI)

        # Reorder the remaining buttons and trigger animations
        self._reorder_buttons()
        self._trigger_reposition_animation()

        self._trigger_callback({"remove_layer": {"name": button_text}})
    
    def remove_button(self, button: pygame_gui.elements.UIButton) -> None:
        if not self.buttons: return
        if button not in self.buttons: return

        removed_button = self.buttons.pop(self.buttons.index(button))  # Remove the button from the list
        if removed_button is self.selected_button: self.selected_button = None
        button_text = removed_button.text
        removed_button.kill()  # Kill the button (remove it from the UI)

        # Reorder the remaining buttons and trigger animations
        self._reorder_buttons()
        self._trigger_reposition_animation()

        self._trigger_callback({"remove_layer": {"name": button_text}})

    def select_button(self, button: pygame_gui.elements.UIButton) -> None:
        if not button in self.buttons: return
        if button is self.selected_button: return

        if self.selected_button:
            self.selected_button.unselect()
            self.selected_button.border_width = 0
            self.selected_button.text_horiz_alignment_padding = 10
            self.selected_button.colours["normal_bg"] = pygame.Color(0,0,0,0)#"rgba(0,0,0,0)"
            self.selected_button.rebuild()

        button.border_width = 1
        button.text_horiz_alignment_padding = 9
        button.colours["normal_bg"] = pygame.Color(49,59,66)#"rgb(92,96,98)"
        button.rebuild()
        button.select()
        self.selected_button = button

        self._trigger_callback({"selected_layer": {"name": self.selected_button.text}})
    
    def get_order_list(self) -> None:
        return [button.text for button in self.buttons]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.add_button(f"Button {len(self.buttons)}")
            if event.key == pygame.K_b:
                if self.buttons:
                    self.remove_random_button()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        self.dragged_button = button
                        self.dragged_button.change_layer(20)
                        self.dragged_button.start_drag(event.pos)
                        self.select_button(self.dragged_button)
                        break

        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragged_button:
                self.dragged_button.stop_drag()
                self.dragged_button.change_layer(15)
                self.dragged_button = None
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for button in self.buttons:
                if button is event.ui_element:
                    self.select_button(button)
                    break
        
    def update(self, time_delta):
        super().update(time_delta)

        if self.dragged_button:
            # Handle dragging
            mouse_pos = pygame.mouse.get_pos()

            self.dragged_button.drag(mouse_pos)

            min_position = self.scroll_panel.rect.y
            max_position = min_position + self.scroll_panel.rect.height - self.dragged_button.rect.height
            self.dragged_button.set_position((self.dragged_button.rect.x, max(min_position, min(max_position, self.dragged_button.rect.y))))

            if self.dragged_button.rect.y == max_position and not (self.dragged_button.relative_rect.y > (len(self.buttons)-1)*self.button_height):
                scroll_y = self.scroll_panel.get_container().get_relative_rect().y
                self.scroll_panel.get_container().set_relative_position((0, scroll_y-(200*time_delta)))

            if self.dragged_button.rect.y == min_position and self.scroll_panel.get_container().get_relative_rect().y < 0:
                scroll = self.scroll_panel.get_container().rect.topleft
                self.scroll_panel.get_container().set_position((scroll[0], scroll[1]+(200*time_delta)))

            # Check for reordering in real-time
            self._check_for_reorder()
        
        # Update button positions with easing
        self._update_button_positions(time_delta)
