import pygame
from settings import *
from button import Button

class ModeButton(Button):
    """Game mode selection button"""
    def __init__(self, x, y, width, height, title, description, icon, callback):
        super().__init__(x, y, width, height, title, callback)
        self.description = description
        self.icon = icon
        self.title_font = pygame.font.Font(None, 40)
        self.desc_font = pygame.font.Font(None, 24)
        self.icon_font = get_icon_font(65)
    
    def render(self, screen):
        """Draw mode selection button"""
        color = BUTTON_HOVER if self.hovered else BUTTON_BG
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        pygame.draw.rect(screen, BUTTON_TEXT, self.rect, 3, border_radius=15)
        
        # Icon at top
        icon_surface = self.icon_font.render(self.icon, True, BUTTON_TEXT)
        icon_rect = icon_surface.get_rect(center=(self.rect.centerx, self.rect.y + 60))
        screen.blit(icon_surface, icon_rect)
        
        # Title
        title_surface = self.title_font.render(self.text, True, BUTTON_TEXT)
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.centery + 10))
        screen.blit(title_surface, title_rect)
        
        # Description (wrapped)
        self._render_description(screen)
    
    def _render_description(self, screen):
        """Render wrapped description text"""
        words = self.description.split()
        lines = []
        current_line = ""
        max_width = self.rect.width - 40
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.desc_font.render(test_line, True, BUTTON_TEXT)
            if test_surface.get_width() < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # Render lines
        y_offset = self.rect.centery + 45
        for line in lines[:3]:
            line_surface = self.desc_font.render(line, True, BUTTON_TEXT)
            line_rect = line_surface.get_rect(center=(self.rect.centerx, y_offset))
            screen.blit(line_surface, line_rect)
            y_offset += 28


class ModeSelectPage:
    """Game mode selection page"""
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
        # Fonts
        self.title_font = get_title_font()
        self.subtitle_font = get_subtitle_font()
        self.info_font = pygame.font.Font(None, 26)
        
        # Mode buttons
        button_width = 250
        button_height = 280
        button_spacing = 40
        start_x = (SCREEN_WIDTH - (2 * button_width + button_spacing)) // 2
        start_y = 200
        
        self.learning_button = ModeButton(
            start_x, start_y,
            button_width, button_height,
            "Learning Mode",
            "Practice your own vocabulary words with weighted selection",
            "📚",
            lambda: "learning"
        )
        
        self.infinity_button = ModeButton(
            start_x + button_width + button_spacing, start_y,
            button_width, button_height,
            "Infinity Mode",
            "Play with random dictionary words from the internet",
            "🌐",
            lambda: "infinity"
        )
        
        # Back button
        self.back_button = Button(20, 20, 100, 40, "← Back", lambda: "back", 18)
        
        self.buttons = [self.learning_button, self.infinity_button, self.back_button]
    
    def handle_event(self, event):
        """Handle button clicks"""
        for button in self.buttons:
            result = button.handle_event(event)
            if result:
                return button.callback()
        return None
    
    def render(self, screen):
        """Draw the mode selection page"""
        screen.fill(BG_COLOR)
        
        # Title
        title_text = "Choose Game Mode"
        title_surface = self.title_font.render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "How do you want to play?"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, BLACK)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 110))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Buttons
        for button in self.buttons:
            button.render(screen)
        
        # Info about learning mode
        stats = self.data_manager.get_statistics()
        if stats["total"] > 0:
            info_y = 520
            info_text = f"You have {stats['total']} word(s) in your learning list"
            info_surface = self.info_font.render(info_text, True, (100, 100, 100))
            info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y))
            screen.blit(info_surface, info_rect)
        else:
            # No words warning
            warning_y = 520
            warning_text = "⚠ Add words first to use Learning Mode!"
            warning_surface = self.info_font.render(warning_text, True, (200, 50, 50))
            warning_rect = warning_surface.get_rect(center=(SCREEN_WIDTH // 2, warning_y))
            screen.blit(warning_surface, warning_rect)
            
            # Disable learning button visually
            overlay = pygame.Surface((self.learning_button.rect.width, self.learning_button.rect.height))
            overlay.set_alpha(128)
            overlay.fill((150, 150, 150))
            screen.blit(overlay, self.learning_button.rect.topleft)