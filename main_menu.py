import pygame
from settings import *
from button import Button
from assets import AssetManager

class MenuButton(Button):
    """Enhanced menu button with icons"""
    def __init__(self, x, y, width, height, text, icon_text, callback):
        super().__init__(x, y, width, height, text, callback)
        self.icon_text = icon_text
        self.icon_font = get_icon_font(50)
    
    def render(self, screen):
        """Draw the menu button with icon"""
        color = BUTTON_HOVER if self.hovered else BUTTON_BG
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, BUTTON_TEXT, self.rect, 3, border_radius=12)
        
        # Icon
        icon_surface = self.icon_font.render(self.icon_text, True, BUTTON_TEXT)
        icon_rect = icon_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 20))
        screen.blit(icon_surface, icon_rect)
        
        # Text
        text_surface = self.font.render(self.text, True, BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery + 25))
        screen.blit(text_surface, text_rect)


class MainMenu:
    """Main menu for navigation"""
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.assets = AssetManager()
        
        # Fonts
        self.title_font = get_title_font()
        self.subtitle_font = get_subtitle_font()
        self.stats_font = pygame.font.Font(None, 28)
        
        # Buttons - centered layout
        button_width = 250
        button_height = 120
        button_spacing = 30
        start_y = 200
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.play_button = MenuButton(
            center_x, start_y, 
            button_width, button_height,
            "Play Game", "🎮",
            lambda: "play"
        )
        
        self.add_words_button = MenuButton(
            center_x, start_y + button_height + button_spacing,
            button_width, button_height,
            "Add Words", "➕",
            lambda: "add_words"
        )
        
        self.word_list_button = MenuButton(
            center_x, start_y + 2 * (button_height + button_spacing),
            button_width, button_height,
            "Word List", "📚",
            lambda: "word_list"
        )
        
        self.buttons = [self.play_button, self.add_words_button, self.word_list_button]
        
        # Statistics cache
        self.stats = None
        self.update_stats()
    
    def update_stats(self):
        """Update statistics"""
        self.stats = self.data_manager.get_statistics()
    
    def handle_event(self, event):
        """Handle button clicks"""
        for button in self.buttons:
            result = button.handle_event(event)
            if result:
                return button.callback()
        return None
    
    def render(self, screen):
        """Draw the main menu"""
        screen.fill(BG_COLOR)
        
        # Title
        title_text = "PURRDLE"
        subtitle_text = " Vocabulary Learning "
        
        title_surface = self.title_font.render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title_surface, title_rect)
        
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, BLACK)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 110))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Cat logos
        if self.assets.has("logo"):
            logo_y = title_rect.centery - 12
            self.assets.draw(screen, "logo", (SCREEN_WIDTH // 2 - 170, logo_y), size=(100, 100), center=True)
            self.assets.draw(screen, "logo", (SCREEN_WIDTH // 2 + 170, logo_y), size=(100, 100), center=True)
        
        # Buttons
        for button in self.buttons:
            button.render(screen)
        
        # Statistics display at bottom
        if self.stats and self.stats["total"] > 0:
            stats_y = SCREEN_HEIGHT - 150
            
            # Stats background
            stats_rect = pygame.Rect(50, stats_y, SCREEN_WIDTH - 100, 120)
            pygame.draw.rect(screen, WHITE, stats_rect, border_radius=10)
            pygame.draw.rect(screen, OUTLINE_COLOR, stats_rect, 2, border_radius=10)
            
            # Title
            stats_title = self.subtitle_font.render("Your Progress", True, BLACK)
            stats_title_rect = stats_title.get_rect(center=(SCREEN_WIDTH // 2, stats_y + 30))
            screen.blit(stats_title, stats_title_rect)
            
            # Stats bars
            bar_y = stats_y + 70
            bar_width = (SCREEN_WIDTH - 160) // 3
            bar_spacing = 10
            
            # Not Learned
            self._draw_stat_bar(screen, 70, bar_y, bar_width, 
                              self.stats["not_learned"], 
                              CAT_GRAY, "Not Learned")
            
            # Few Mistakes
            self._draw_stat_bar(screen, 70 + bar_width + bar_spacing, bar_y, bar_width,
                              self.stats["few_mistakes"],
                              CAT_YELLOW, "Few Mistakes")
            
            # Learned
            self._draw_stat_bar(screen, 70 + 2 * (bar_width + bar_spacing), bar_y, bar_width,
                              self.stats["learned"],
                              CAT_GREEN, "Learned")
        
        # Instructions if no words
        if not self.stats or self.stats["total"] == 0:
            info_text = "Add words to start learning!"
            info_surface = self.stats_font.render(info_text, True, (150, 150, 150))
            info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
            screen.blit(info_surface, info_rect)
    
    def _draw_stat_bar(self, screen, x, y, width, count, color, label):
        """Draw a statistic bar"""
        # Background bar
        bar_height = 30
        pygame.draw.rect(screen, (230, 230, 230), (x, y, width, bar_height), border_radius=5)
        
        # Filled portion
        if self.stats["total"] > 0:
            fill_width = int((count / self.stats["total"]) * width)
            pygame.draw.rect(screen, color, (x, y, fill_width, bar_height), border_radius=5)
        
        # Border
        pygame.draw.rect(screen, OUTLINE_COLOR, (x, y, width, bar_height), 2, border_radius=5)
        
        # Label
        label_surface = pygame.font.Font(None, 20).render(label, True, BLACK)
        label_rect = label_surface.get_rect(center=(x + width // 2, y - 12))
        screen.blit(label_surface, label_rect)
        
        # Count
        count_surface = pygame.font.Font(None, 24).render(str(count), True, BLACK)
        count_rect = count_surface.get_rect(center=(x + width // 2, y + bar_height // 2))
        screen.blit(count_surface, count_rect)