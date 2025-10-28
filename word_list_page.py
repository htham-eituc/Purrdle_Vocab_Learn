import pygame
from settings import *
from button import Button
from data_manager import DataManager

class FilterButton(Button):
    """Filter button with active state"""
    def __init__(self, x, y, width, height, text, filter_value, callback):
        super().__init__(x, y, width, height, text, callback, FILTER_SIZE)
        self.filter_value = filter_value
        self.active = False
    
    def render(self, screen):
        """Draw filter button"""
        if self.active:
            color = CAT_GREEN
            text_color = WHITE
        elif self.hovered:
            color = BUTTON_HOVER
            text_color = BUTTON_TEXT
        else:
            color = BUTTON_BG
            text_color = BUTTON_TEXT
        
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BUTTON_TEXT, self.rect, 2, border_radius=8)
        
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class WordCard:
    """Display card for a single word"""
    def __init__(self, word_obj, y_pos, width):
        self.word_obj = word_obj
        self.rect = pygame.Rect(20, y_pos, width - 40, 100)
        self.word_font = pygame.font.Font(None, 32)
        self.def_font = pygame.font.Font(None, 22)
        self.stats_font = pygame.font.Font(None, 20)
        
        # Delete button
        delete_size = 30
        self.delete_button = Button(
            self.rect.right - delete_size - 10,
            self.rect.y + 10,
            delete_size, delete_size,
            "X", 
            lambda: None
        )
        self.delete_button.font = pygame.font.Font(None, 28)
        
        self.hovered = False
    
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        
        # Check delete button
        if self.delete_button.handle_event(event):
            return ("delete", self.word_obj.word)
        
        return None
    
    def render(self, screen):
        """Draw the word card"""
        # Background color based on status
        status_colors = {
            "not_learned": (255, 240, 240),  # Light red
            "few_mistakes": (255, 250, 220),  # Light yellow
            "learned": (240, 255, 240)        # Light green
        }
        bg_color = status_colors.get(self.word_obj.status, WHITE)
        
        # Border color based on status
        border_colors = {
            "not_learned": (200, 100, 100),
            "few_mistakes": CAT_YELLOW,
            "learned": CAT_GREEN
        }
        border_color = border_colors.get(self.word_obj.status, OUTLINE_COLOR)
        
        # Draw background
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 3 if self.hovered else 2, border_radius=8)
        
        # Word (bold)
        word_surface = self.word_font.render(self.word_obj.word, True, BLACK)
        screen.blit(word_surface, (self.rect.x + 15, self.rect.y + 12))
        
        # Definition (truncated)
        def_text = self.word_obj.definition
        if len(def_text) > 70:
            def_text = def_text[:70] + "..."
        def_surface = self.def_font.render(def_text, True, (80, 80, 80))
        screen.blit(def_surface, (self.rect.x + 15, self.rect.y + 45))
        
        # Stats at bottom
        stats_text = f"Attempts: {self.word_obj.attempts} | Correct: {self.word_obj.correct} | Wrong: {self.word_obj.wrong}"
        stats_surface = self.stats_font.render(stats_text, True, (120, 120, 120))
        screen.blit(stats_surface, (self.rect.x + 15, self.rect.y + 72))
        
        # Status badge (top right)
        status_text = self.word_obj.status.replace("_", " ").title()
        badge_color = border_color
        badge_width = 120
        badge_height = 28
        badge_rect = pygame.Rect(
            self.rect.right - badge_width - 50,
            self.rect.y + 10,
            badge_width, badge_height
        )
        pygame.draw.rect(screen, badge_color, badge_rect, border_radius=5)
        
        badge_surface = pygame.font.Font(None, 22).render(status_text, True, WHITE)
        badge_text_rect = badge_surface.get_rect(center=badge_rect.center)
        screen.blit(badge_surface, badge_text_rect)
        
        # Delete button
        self.delete_button.render(screen)


class SearchBox:
    """Search input box"""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.font = get_icon_font(28)
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return None
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 30 and event.unicode.isprintable():
                self.text += event.unicode
            return "search"
        
        return None
    
    def render(self, screen):
        """Draw search box"""
        bg_color = WHITE if self.active else LIGHT_GRAY
        border_color = CAT_GREEN if self.active else OUTLINE_COLOR
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Search icon
        icon_surface = self.font.render("🔍", True, (100, 100, 100))
        screen.blit(icon_surface, (self.rect.x + 10, self.rect.y + 8))
        
        # Text or placeholder
        display_text = self.text if self.text else "Search words..."
        text_color = BLACK if self.text else (150, 150, 150)
        text_surface = self.font.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 45, self.rect.y + 10))
    
    def get_text(self):
        """Get search text"""
        return self.text.lower().strip()


class WordListPage:
    """Word list tracker and management page"""
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
        # Fonts
        self.title_font = get_title_font()
        self.subtitle_font = pygame.font.Font(None, 26)
        
        # Filter buttons
        filter_y = 120
        filter_width = 120
        filter_height = 40
        filter_spacing = 10
        start_x = 20
        
        self.all_filter = FilterButton(
            start_x, filter_y, filter_width, filter_height,
            "All", None, lambda: self.set_filter(None)
        )
        self.all_filter.active = True
        
        self.not_learned_filter = FilterButton(
            start_x + filter_width + filter_spacing, filter_y,
            filter_width, filter_height,
            "Not Learned", "not_learned",
            lambda: self.set_filter("not_learned")
        )
        
        self.few_mistakes_filter = FilterButton(
            start_x + 2 * (filter_width + filter_spacing), filter_y,
            filter_width + 20, filter_height,
            "Few Mistakes", "few_mistakes",
            lambda: self.set_filter("few_mistakes")
        )
        
        self.learned_filter = FilterButton(
            start_x + 3 * (filter_width + filter_spacing) + 20, filter_y,
            filter_width, filter_height,
            "Learned", "learned",
            lambda: self.set_filter("learned")
        )
        
        self.filter_buttons = [
            self.all_filter, self.not_learned_filter,
            self.few_mistakes_filter, self.learned_filter
        ]
        
        # Search box
        self.search_box = SearchBox(20, 175, SCREEN_WIDTH - 40, 45)
        
        # Back button
        self.back_button = Button(20, 20, 100, 40, "← Back", lambda: "back", 18)
        
        # Current filter and search
        self.current_filter = None
        self.search_query = ""
        
        # Scrolling
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Word cards
        self.word_cards = []
        self.update_word_list()
    
    def set_filter(self, filter_value):
        """Set the active filter"""
        self.current_filter = filter_value
        for button in self.filter_buttons:
            button.active = (button.filter_value == filter_value)
        self.update_word_list()
    
    def update_word_list(self):
        """Update the displayed word list"""
        # Get filtered words
        words = self.data_manager.get_all_words(
            sort_by="alphabetical",
            filter_status=self.current_filter
        )
        
        # Apply search filter
        if self.search_query:
            words = [w for w in words if self.search_query in w.word.lower() or 
                     self.search_query in w.definition.lower()]
        
        # Create word cards
        self.word_cards = []
        y_pos = 0
        for word_obj in words:
            card = WordCard(word_obj, y_pos, SCREEN_WIDTH)
            self.word_cards.append(card)
            y_pos += 110
        
        # Calculate max scroll
        content_height = len(self.word_cards) * 110
        visible_height = SCREEN_HEIGHT - 240 - 20
        self.max_scroll = max(0, content_height - visible_height)
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)
    
    def handle_event(self, event):
        """Handle all events"""
        # Back button
        if self.back_button.handle_event(event):
            return "back"
        
        # Filter buttons
        for button in self.filter_buttons:
            button.handle_event(event)
        
        # Search box
        result = self.search_box.handle_event(event)
        if result == "search":
            self.search_query = self.search_box.get_text()
            self.update_word_list()
        
        # Scrolling with mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
        
        # Word cards (with scroll offset)
        for card in self.word_cards:
            # Adjust card position for scrolling
            original_y = card.rect.y
            card.rect.y = original_y - self.scroll_offset + 240
            card.delete_button.rect.y = card.rect.y + 10
            
            result = card.handle_event(event)
            
            # Restore original position
            card.rect.y = original_y
            card.delete_button.rect.y = original_y + 10
            
            if result and result[0] == "delete":
                # Confirm and delete
                word_to_delete = result[1]
                self.data_manager.delete_word(word_to_delete)
                self.update_word_list()
                return None
        
        return None
    
    def render(self, screen):
        """Draw the word list page"""
        screen.fill(BG_COLOR)
        self.back_button.render(screen)

        # Title & stats
        title_surface = self.title_font.render("Word List & Tracker", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)

        stats = self.data_manager.get_statistics()
        stats_text = f"Total: {stats['total']} | Not Learned: {stats['not_learned']} | Few Mistakes: {stats['few_mistakes']} | Learned: {stats['learned']}"
        stats_surface = self.subtitle_font.render(stats_text, True, (100, 100, 100))
        screen.blit(stats_surface, stats_surface.get_rect(center=(SCREEN_WIDTH // 2, 85)))

        # Filters + search
        for button in self.filter_buttons:
            button.render(screen)
        self.search_box.render(screen)

        # Scrollable area
        scroll_top = 240
        scroll_height = SCREEN_HEIGHT - scroll_top
        scroll_area = pygame.Rect(0, scroll_top, SCREEN_WIDTH, scroll_height)
        screen.set_clip(scroll_area)

        if self.word_cards:
            for card in self.word_cards:
                # Compute visible position
                display_y = card.rect.y - self.scroll_offset
                if display_y + card.rect.height >= 0 and display_y <= scroll_height:
                    # Temporarily move rect
                    original_y = card.rect.y
                    card.rect.y = display_y + scroll_top
                    card.delete_button.rect.y = card.rect.y + 10

                    card.render(screen)

                    # Restore original position
                    card.rect.y = original_y
                    card.delete_button.rect.y = original_y + 10
        else:
            text = "No words found" if self.search_query else "No words yet. Add some words!"
            text_surface = pygame.font.Font(None, 32).render(text, True, (150, 150, 150))
            screen.blit(text_surface, text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        screen.set_clip(None)

        # Scroll indicator
        if self.max_scroll > 0:
            visible_ratio = scroll_height / max(scroll_height + self.max_scroll, 1)
            indicator_height = max(int(scroll_height * visible_ratio), 30)
            indicator_x = SCREEN_WIDTH - 14
            indicator_y = scroll_top + int((self.scroll_offset / self.max_scroll) * (scroll_height - indicator_height))
            pygame.draw.rect(screen, CAT_GRAY, (indicator_x, indicator_y, 4, indicator_height), border_radius=2)
