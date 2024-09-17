import pygame
import pygame_gui
from typing import Callable, Any

class Image_Button(pygame_gui.elements.UIButton):
    def __init__(self, id: str, image: pygame.Surface, manager: pygame_gui.UIManager, relative_rect: pygame.Rect, callback: Callable[[Any], Any] = None, *args, **kwargs) -> None:
        super().__init__(manager=manager, relative_rect=relative_rect, text="", command=lambda: callback(id), *args, **kwargs)
        self.id = id
        self.callback = callback
        self.image = pygame.transform.scale(image.copy(), (self.relative_rect.width, self.relative_rect.height))
        self.normal_image = self._generate_normal_image()
        self.hovered_image = self._generate_hovered_image()
        self.selected_image = self._generate_selected_image()

        self.rebuild()
    
    def _add_base_image(func: Callable[[Any], Any]) -> Callable:
        def wrapper(*args, **kwargs):
            image: pygame.Surface = func(*args, **kwargs)
            base_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            base_image.fill((33,40,45))
            base_image.blit(image, (0,0))
            return base_image
        return wrapper
    
    @_add_base_image
    def _generate_normal_image(self) -> pygame.Surface:
        image = self.image.copy()

        return image
    
    @_add_base_image
    def _generate_hovered_image(self) -> pygame.Surface:
        image: pygame.Surface = self.image.copy().convert_alpha()

        border_rect = pygame.Rect((0,0), image.get_size())
        border_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, pygame.Color(255,255,255, 10), border_rect)
        pygame.draw.rect(border_surface, pygame.Color(255,255,255, 100), border_rect, width=4)
        image.blit(border_surface, (0,0))

        return image
    
    @_add_base_image
    def _generate_selected_image(self) -> pygame.Surface:
        tint_surface = pygame.Surface((self.relative_rect.width, self.relative_rect.height), pygame.SRCALPHA)
        tint_surface.fill(pygame.Color(255,255,255,100)) # rgb(92,96,98)

        image = self.image.copy()
        
        image.blit(tint_surface, (0,0))

        return image