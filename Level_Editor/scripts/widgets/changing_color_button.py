import pygame
import pygame_gui

class Changing_Color_Button(pygame_gui.elements.UIButton):
    def __init__(self, relative_rect, manager, container, text = "", *args, **kwargs):
        super().__init__(relative_rect=relative_rect, manager=manager, container=container, text=text, object_id="#changing_color_button", *args, **kwargs)

        self.normal_border_color = self.colours["normal_bg"]
        self.hover_border_color = self.colours["hovered_bg"]
        self.active_border_color = self.colours["selected_bg"]

        self.color = (0,0,0,255)
    
    def set_color(self, new_color: pygame.Color) -> None:
        self.color = new_color
    
    def update(self, time_delta: float):
        self.colours["normal_bg"] = pygame.Color(self.color)
        if self.held:
            self.colours["normal_border"] = self.active_border_color
        elif self.hovered:
            self.colours["normal_border"] = self.hover_border_color
        else:
            self.colours["normal_border"] = self.normal_border_color
        
        self.rebuild()

        super().update(time_delta)