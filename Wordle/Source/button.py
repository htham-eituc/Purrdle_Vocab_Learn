import pygame
from settings import BUTTON_BG, BUTTON_HOVER, BUTTON_TEXT, get_button_font

class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.font = get_button_font()
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.callback()
                return True
        return False
    
    def render(self, screen):
        color = BUTTON_HOVER if self.hovered else BUTTON_BG
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BUTTON_TEXT, self.rect, 3, border_radius=10)
        
        text_surface = self.font.render(self.text, True, BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)