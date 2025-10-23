import pygame
from settings import *

class Key:
    """Individual key on the keyboard"""
    def __init__(self, letter, x, y, width, height):
        self.letter = letter
        self.rect = pygame.Rect(x, y, width, height)
        self.color = "none"  # none, gray, yellow, green
        self.hovered = False
        self.font = get_key_font()
    
    def update_color(self, new_color):
        """Update key color based on guess results (priority: green > yellow > gray)"""
        priority = {"none": 0, "gray": 1, "yellow": 2, "green": 3}
        if priority.get(new_color, 0) > priority.get(self.color, 0):
            self.color = new_color
    
    def reset(self):
        """Reset key color"""
        self.color = "none"
    
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                return self.letter
        return None
    
    def render(self, screen):
        """Draw the key"""
        # Determine color
        if self.color == "green":
            bg_color = CAT_GREEN
            text_color = WHITE
        elif self.color == "yellow":
            bg_color = CAT_YELLOW
            text_color = WHITE
        elif self.color == "gray":
            bg_color = CAT_GRAY
            text_color = WHITE
        else:  # none
            bg_color = KEY_BG
            text_color = BLACK
        
        # Hover effect
        if self.hovered and self.color == "none":
            bg_color = KEY_HOVER
        
        # Draw key
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(screen, KEY_BORDER, self.rect, 2, border_radius=4)
        
        # Draw letter
        text_surface = self.font.render(self.letter, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Keyboard:
    """On-screen keyboard with color feedback"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.keys = {}
        self.special_keys = {}
        self.create_keyboard()
    
    def create_keyboard(self):
        """Create QWERTY keyboard layout"""
        rows = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
        
        key_width = 38
        key_height = 50
        key_padding = 6
        
        y_offset = 0
        
        for row_idx, row in enumerate(rows):
            # Calculate x offset for centering
            row_width = len(row) * (key_width + key_padding) - key_padding
            x_offset = (KEYBOARD_WIDTH - row_width) // 2
            
            for col_idx, letter in enumerate(row):
                x = self.x + x_offset + col_idx * (key_width + key_padding)
                y = self.y + y_offset
                key = Key(letter, x, y, key_width, key_height)
                self.keys[letter] = key
            
            y_offset += key_height + key_padding
        
        # Add special keys (Enter and Backspace)
        last_row_y = self.y + y_offset - (key_height + key_padding)
        
        # Enter key (left side)
        enter_width = 75
        enter_x = self.x + (KEYBOARD_WIDTH - row_width) // 2 - enter_width - key_padding
        self.special_keys["ENTER"] = Key("Enter", enter_x, last_row_y, enter_width, key_height)
        
        # Backspace key (right side)
        backspace_width = 75
        backspace_x = self.x + (KEYBOARD_WIDTH + row_width) // 2 + key_padding
        self.special_keys["BACK"] = Key("Back", backspace_x, last_row_y, backspace_width, key_height)
    
    def update_from_guess(self, guess_letters, colors):
        """Update keyboard colors based on guess results"""
        for letter, color in zip(guess_letters, colors):
            if letter in self.keys:
                self.keys[letter].update_color(color)
    
    def reset(self):
        """Reset all key colors"""
        for key in self.keys.values():
            key.reset()
        for key in self.special_keys.values():
            key.reset()
    
    def handle_event(self, event):
        """Handle mouse events, returns action (letter, 'ENTER', 'BACK', or None)"""
        # Check special keys first
        for action, key in self.special_keys.items():
            result = key.handle_event(event)
            if result:
                return action
        
        # Check letter keys
        for key in self.keys.values():
            result = key.handle_event(event)
            if result:
                return result
        
        return None
    
    def render(self, screen):
        """Draw the keyboard"""
        # Draw background
        # bg_rect = pygame.Rect(self.x - 10, self.y - 10, KEYBOARD_WIDTH + 20, KEYBOARD_HEIGHT + 20)
        # pygame.draw.rect(screen, KEYBOARD_BG, bg_rect, border_radius=10)
        
        # Draw all letter keys
        for key in self.keys.values():
            key.render(screen)
        
        # Draw special keys
        for key in self.special_keys.values():
            key.render(screen)