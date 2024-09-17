from .right_click_button import Right_Click_Button

class DraggableButton(Right_Click_Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_dragging = False
        self.original_position = self.relative_rect.topleft

    def start_drag(self, mouse_pos):
        self.is_dragging = True
        self.original_position = self.relative_rect.topleft
        self.mouse_offset = (self.rect.x - mouse_pos[0], self.rect.y - mouse_pos[1])

    def drag(self, mouse_pos):
        if self.is_dragging: self.set_position((self.rect.x, mouse_pos[1]+self.mouse_offset[1]))

    def stop_drag(self):
        self.is_dragging = False
        self.set_relative_position(self.original_position)
    