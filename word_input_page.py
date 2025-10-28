import pygame
from settings import *
from button import Button
from data_manager import DataManager

class InputBox:
    """Text input box component"""
    def __init__(self, x, y, width, height, placeholder="", max_length=50, multiline=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.max_length = max_length
        self.multiline = multiline
        self.active = False
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.scroll_offset = 0
        
    def handle_event(self, event):
        """Handle keyboard and mouse events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return None
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN and not self.multiline:
                return "submit"
            elif event.key == pygame.K_TAB:
                return "next"
            elif len(self.text) < self.max_length:
                # Allow letters, spaces, hyphens
                if event.unicode.isprintable():
                    self.text += event.unicode
        return None
    
    def update(self):
        """Update cursor blinking"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blink every 30 frames
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def render(self, screen):
        """Draw the input box"""
        # Background
        bg_color = WHITE if self.active else LIGHT_GRAY
        border_color = CAT_GREEN if self.active else OUTLINE_COLOR
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=5)
        
        # Text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else (150, 150, 150)
        
        if self.multiline:
            # Multi-line rendering for definition
            self._render_multiline(screen, display_text, text_color)
        else:
            # Single line rendering for word
            text_surface = self.font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
            screen.blit(text_surface, text_rect)
            
            # Cursor
            if self.active and self.cursor_visible and self.text:
                cursor_x = text_rect.right + 2
                cursor_y = self.rect.centery - 15
                pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + 30), 2)
    
    def _render_multiline(self, screen, text, color):
        """Render multi-line text with wrapping"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.small_font.render(test_line, True, color)
            if test_surface.get_width() < self.rect.width - 20:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
        
        if current_line:
            lines.append(current_line)
        
        # Render lines
        y_offset = self.rect.y + 10
        for line in lines[:4]:  # Max 4 lines visible
            line_surface = self.small_font.render(line, True, color)
            screen.blit(line_surface, (self.rect.x + 10, y_offset))
            y_offset += 30
    
    def get_text(self):
        """Get the current text"""
        return self.text.strip()
    
    def clear(self):
        """Clear the input"""
        self.text = ""


class WordListItem:
    """Display item for a word in the list"""
    def __init__(self, word, definition, y_pos, width):
        self.word = word
        self.definition = definition
        self.rect = pygame.Rect(20, y_pos, width - 40, 60)
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
    
    def render(self, screen):
        """Draw the word list item"""
        # Background
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=5)
        pygame.draw.rect(screen, OUTLINE_COLOR, self.rect, 2, border_radius=5)
        
        # Word (bold)
        word_surface = self.font.render(self.word, True, BLACK)
        screen.blit(word_surface, (self.rect.x + 10, self.rect.y + 8))
        
        # Definition (smaller, truncated)
        def_text = self.definition
        if len(def_text) > 60:
            def_text = def_text[:60] + "..."
        def_surface = self.small_font.render(def_text, True, (100, 100, 100))
        screen.blit(def_surface, (self.rect.x + 10, self.rect.y + 35))


class WordInputPage:
    """Page for adding new vocabulary words"""
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
        # Title
        self.title_font = get_title_font()
        self.message_font = pygame.font.Font(None, 28)
        
        # Input boxes
        self.word_input = InputBox(50, 120, SCREEN_WIDTH - 100, 50, 
                                   placeholder="Enter word (max 20 chars)", 
                                   max_length=20)
        
        self.def_input = InputBox(50, 200, SCREEN_WIDTH - 100, 120, 
                                 placeholder="Enter definition", 
                                 max_length=200, 
                                 multiline=True)
        
        # Buttons
        button_y = 340
        button_spacing = 170
        self.add_button = Button(50, button_y, 150, 50, "Add Word", self.add_word)
        self.clear_button = Button(220, button_y, 150, 50, "Clear", self.clear_inputs)
        self.back_button = Button(SCREEN_WIDTH - 170, button_y, 120, 50, "Back", lambda: None)
        
        # Recently added words list
        self.recent_words = []
        self.scroll_offset = 0
        
        # Feedback message
        self.message = ""
        self.message_color = BLACK
        self.message_timer = 0
        
    def add_word(self):
        """Add word to data manager"""
        word = self.word_input.get_text()
        definition = self.def_input.get_text()
        
        if word and not definition:
            from dictionary_api import get_definition  # or top-level import
            api_def = get_definition(word)
            if api_def:
                definition = api_def
                self.def_input.text = api_def
            else:
                self.message = f"No definition found for '{word}', please enter manually."
                self.message_color = (200, 50, 50)
                return
        
        success, message = self.data_manager.add_word(word, definition)
        
        if success:
            self.message = message
            self.message_color = CAT_GREEN
            self.clear_inputs()
            # Add to recent list
            self.recent_words.insert(0, (word, definition))
            if len(self.recent_words) > 5:
                self.recent_words.pop()
        else:
            self.message = message
            self.message_color = (200, 50, 50)
        
        self.message_timer = 180  # Show for 3 seconds at 60fps
    
    def clear_inputs(self):
        """Clear both input boxes"""
        self.word_input.clear()
        self.def_input.clear()
    
    def handle_event(self, event):
        """Handle all events"""
        # Check back button first
        if self.back_button.handle_event(event):
            return "back"
        
        # Buttons
        self.add_button.handle_event(event)
        self.clear_button.handle_event(event)
        
        # Input boxes
        result = self.word_input.handle_event(event)
        if result == "next":
            self.word_input.active = False
            self.def_input.active = True
            return None
        elif result == "submit":
            self.add_word()
            return None
        
        result = self.def_input.handle_event(event)
        if result == "next":
            self.def_input.active = False
            self.word_input.active = True
        
        return None
    
    def update(self):
        """Update animations"""
        self.word_input.update()
        self.def_input.update()
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""
    
    def render(self, screen):
        """Draw the page"""
        screen.fill(BG_COLOR)
        
        # Title
        title_text = "Add New Words"
        title_surface = self.title_font.render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)
        
        # Labels
        label_font = pygame.font.Font(None, 26)
        word_label = label_font.render("Word:", True, BLACK)
        screen.blit(word_label, (50, 95))
        
        def_label = label_font.render("Definition:", True, BLACK)
        screen.blit(def_label, (50, 175))
        
        # Input boxes
        self.word_input.render(screen)
        self.def_input.render(screen)
        
        # Buttons
        self.add_button.render(screen)
        self.clear_button.render(screen)
        self.back_button.render(screen)
        
        # Feedback message
        if self.message:
            message_surface = self.message_font.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, 410))
            screen.blit(message_surface, message_rect)
        
        # Recently added words section
        if self.recent_words:
            recent_label = self.message_font.render("Recently Added:", True, BLACK)
            screen.blit(recent_label, (20, 450))
            
            y_pos = 500
            for word, definition in self.recent_words:
                item = WordListItem(word, definition, y_pos, SCREEN_WIDTH)
                item.render(screen)
                y_pos += 70
        
        # Character counter for word input
        if self.word_input.active:
            char_count = len(self.word_input.text)
            counter_text = f"{char_count}/20"
            counter_color = (200, 50, 50) if char_count > 20 else (100, 100, 100)
            counter_surface = label_font.render(counter_text, True, counter_color)
            screen.blit(counter_surface, (SCREEN_WIDTH - 120, 95))