import pygame
import pygame_gui
from typing import List, Tuple

from ..tilemap import Tilemap
from ..utils.other import one_key_pressed

class Map_Panel:
    def __init__(self, position: List[int] | Tuple[int], size: List[int] | Tuple[int], color: pygame.Color = pygame.Color(33, 40, 45), 
                 border_width: int = 1, border_color: pygame.Color = pygame.Color(92, 96, 98), tile_size: int = 64) -> None:
        self.position = position
        self.size = (max(0, size[0]), max(0, size[1]))
        self.color = color
        self.border_width = border_width
        self.border_color = border_color
        self.border_position = None
        self.border: pygame.Rect = None

        self.render_surface = None
        self.render_surface_position = None
        self.render_surface_size = None

        self.rect = None

        self.tilemap = Tilemap(tile_size)

        self.world_offset = [0,0]

        self.camera_controls = {"left": [pygame.K_LEFT], "right": [pygame.K_RIGHT], "up": [pygame.K_UP], "down": [pygame.K_DOWN]}
        self.camera_direction = pygame.math.Vector2(0,0)
        self.camera_speed = 600
        self.drag_camera = False

        self.alt_pressed = False
        self.mouse_wheel_speed = 40

        self._create_border()
        self._create_render_surface()
        self._create_rect()
    
    def _create_border(self) -> None:
        if not self.border_width: return

        self.border_position = self.position

        self.border = pygame.Rect(self.border_position, self.size)
    
    def _create_render_surface(self) -> None:
        if self.border:
            self.render_surface_position = (self.border.x + self.border_width, self.border.y + self.border_width)
            self.render_surface_size = (max(0, self.border.width - self.border_width * 2), max(0, self.border.height - self.border_width * 2))
        else:
            self.render_surface_position = self.position
            self.render_surface_size = self.size
        
        self.render_surface = pygame.Surface(self.render_surface_size, pygame.SRCALPHA)
        self.render_surface.fill(self.color)
    
    def _create_rect(self) -> None:
        self.rect = self.render_surface.get_rect()
        self.rect.topleft = self.position
    
    def _move_camera(self, dt: float) -> None:
        self.camera_direction.x = 0
        self.camera_direction.y = 0

        if one_key_pressed(self.camera_controls["left"]):  self.camera_direction.x -= 1
        if one_key_pressed(self.camera_controls["right"]): self.camera_direction.x += 1
        if one_key_pressed(self.camera_controls["up"]):    self.camera_direction.y -= 1
        if one_key_pressed(self.camera_controls["down"]):  self.camera_direction.y += 1
        
        if self.camera_direction.length() > 0:
            self.camera_direction = self.camera_direction.normalize()
        
        self.camera_direction *= self.camera_speed

        self.world_offset[0] += self.camera_direction.x * dt
        self.world_offset[1] += self.camera_direction.y * dt

    def _draw_grid(self) -> None:
        tile_size = self.tilemap.tile_size

        number_of_row_lines = self.render_surface.get_width() // tile_size + 2
        number_of_column_lines = self.render_surface.get_height() // tile_size + 2

        selected_layer_parallax = self.tilemap.get_selected_layer_parallax()
        if not selected_layer_parallax: selected_layer_parallax = 1

        for row in range(number_of_row_lines):
            x = row * tile_size
            if (self.world_offset[0] * selected_layer_parallax) != 0: x -= ((self.world_offset[0] * selected_layer_parallax) % tile_size)
            pygame.draw.line(self.render_surface, (255,255,255, 50), (x, 0), (x, self.render_surface.get_height()))
        
        for col in range(number_of_column_lines):
            y = col * tile_size
            if (self.world_offset[1] * selected_layer_parallax) != 0: y -= ((self.world_offset[1] * selected_layer_parallax) % tile_size)
            pygame.draw.line(self.render_surface, (255,255,255, 50), (0, y), (self.render_surface.get_width(), y))
     
    def __draw_mouse_tile_rect(self) -> None:
        mouse_position = pygame.mouse.get_pos()
        relative_mouse_position = mouse_position[0] - self.position[0], mouse_position[1] - self.position[1]

        if not self.rect.collidepoint(mouse_position): return

        selected_layer_parallax = self.tilemap.get_selected_layer_parallax()
        if not selected_layer_parallax: selected_layer_parallax = 1
        tile_size = self.tilemap.tile_size

        # x = (relative_mouse_position[0] + self.world_offset[0] * selected_layer_parallax) // tile_size 
        # y = (relative_mouse_position[1] + self.world_offset[1] * selected_layer_parallax) // tile_size

        # print(int(x), int(y))

        x = relative_mouse_position[0] // tile_size * tile_size
        if (self.world_offset[0] * selected_layer_parallax) != 0: x -= ((self.world_offset[0] * selected_layer_parallax) % tile_size)

        y = relative_mouse_position[1] // tile_size * tile_size
        if (self.world_offset[1] * selected_layer_parallax) != 0: y -= ((self.world_offset[1] * selected_layer_parallax) % tile_size)

        pygame.draw.rect(self.render_surface, (255,0,0), pygame.Rect(x, y, tile_size, tile_size))
    
    def _draw_mouse_tile_rect(self, deleting: bool = False, drawing_image: pygame.Surface | None = None, layer_selected: bool = True) -> None:
        if not deleting and not drawing_image: return
        if not layer_selected: return

        mouse_position = pygame.mouse.get_pos()
        print(deleting, drawing_image)

        # Subtract self.position to get the relative mouse position on the grid
        relative_mouse_position = mouse_position[0] - self.position[0], mouse_position[1] - self.position[1]

        # Check if the mouse is within the map bounds
        if not self.rect.collidepoint(mouse_position): return

        tile_size = self.tilemap.tile_size

        # Get the selected layer's parallax factor
        selected_layer_parallax = self.tilemap.get_selected_layer_parallax()
        if not selected_layer_parallax:
            selected_layer_parallax = 1

        # Adjust the world offset by parallax
        parallax_offset_x = self.world_offset[0] * selected_layer_parallax
        parallax_offset_y = self.world_offset[1] * selected_layer_parallax

        # Adjust the relative mouse position by subtracting the world offset (with parallax)
        adjusted_mouse_x = relative_mouse_position[0] + parallax_offset_x
        adjusted_mouse_y = relative_mouse_position[1] + parallax_offset_y

        # Snap the mouse position to the nearest tile on the grid
        tile_x = (adjusted_mouse_x // tile_size) * tile_size
        tile_y = (adjusted_mouse_y // tile_size) * tile_size

        if deleting:
            surface = pygame.Surface((tile_size+1, tile_size+1), pygame.SRCALPHA)
            surface.fill(pygame.Color(231, 41, 41, 50))
            self.render_surface.blit(surface, (tile_x - parallax_offset_x, tile_y - parallax_offset_y))
            pygame.draw.rect(self.render_surface, pygame.Color(231, 41, 41, 220), pygame.Rect(tile_x - parallax_offset_x, tile_y - parallax_offset_y, tile_size+1, tile_size+1), width=1)
        else:
            drawing_image_copy = drawing_image.copy()
            drawing_image_copy.set_alpha(50)
            drawing_image_copy = pygame.transform.scale(drawing_image_copy, (tile_size, tile_size))
            self.render_surface.blit(drawing_image_copy, (tile_x - parallax_offset_x, tile_y - parallax_offset_y))


    def set_dimensions(self, dimension: List[int] | Tuple[int]):
        self.size = (max(0, dimension[0]), max(0, dimension[1]))
        self._create_border()
        self._create_render_surface()
        self._create_rect()
    
    def add_tile(self, tile_data: dict, mouse_position_screen: List[int] | Tuple[int], on_grid: bool = True) -> None:
        if not self.rect.collidepoint(mouse_position_screen): return

        t_type = tile_data["type"]
        variant = tile_data["variant"]
        image = tile_data["image"].copy()
        alpha_image = tile_data["image"].copy()
        alpha_image.set_alpha(40)
        position_x = (mouse_position_screen[0] - self.position[0])
        position_y = (mouse_position_screen[1] - self.position[1])
        position = (position_x, position_y)
        
        self.tilemap.add_tile(t_type, variant, position, image, alpha_image, on_grid=on_grid, world_offset=self.world_offset)
    
    def remove_tile(self, mouse_position_screen: List[int] | Tuple[int], on_grid: bool = True, delete_overlapping_objects: bool = False) -> None:
        position_x = (mouse_position_screen[0] - self.position[0])
        position_y = (mouse_position_screen[1] - self.position[1])
        position = (position_x, position_y)
        self.tilemap.remove_tile(position=position, on_grid=on_grid, world_offset=self.world_offset, delete_overlapping_objects=delete_overlapping_objects)

    def render_map(self, render_surface: pygame.Surface, offset: List[int] | Tuple[int] = (0,0)) -> None:
        render_surface.blit(self.render_surface, (self.render_surface_position[0] + offset[0], self.render_surface_position[1] + offset[1]))
        if self.border:
            render_border = self.border.copy()
            render_border.x += offset[0]
            render_border.y += offset[1]
            pygame.draw.rect(render_surface, self.border_color, render_border, width=self.border_width)
    
    def process_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 2: self.drag_camera = True
                if event.button == 4: self.world_offset[0 if self.alt_pressed else 1] -= self.mouse_wheel_speed
                if event.button == 5: self.world_offset[0 if self.alt_pressed else 1] += self.mouse_wheel_speed
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2: self.drag_camera = False
        if event.type == pygame.MOUSEMOTION:
            if self.drag_camera: 
                self.world_offset[0] += -event.rel[0]
                self.world_offset[1] += -event.rel[1]
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LALT:
                self.alt_pressed = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LALT:
                self.alt_pressed = False
        
        self.tilemap.process_event(event)

    def update(self, dt: float, deleting: bool = False, drawing_image: pygame.Surface | None = None, layer_selected: bool = False) -> None:
        self.render_surface.fill(self.color)
        self.tilemap.render_tilemap(self.render_surface, offset=(int(self.world_offset[0]), int(self.world_offset[1])))
        
        self._draw_grid()
        self._draw_mouse_tile_rect(deleting, drawing_image, layer_selected)
        self._move_camera(dt)
        
        #self.tilemap.update()

