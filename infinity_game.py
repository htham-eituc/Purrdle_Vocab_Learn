import pygame
import threading
from settings import *
from vocab_game import VocabGame
from data_manager import Word
from dictionary_api import get_random_word_with_definition, get_fallback_word

class LoadingScreen:
    """Loading animation while fetching word from API"""
    def __init__(self):
        self.angle = 0
        self.font = get_title_font()
        self.message_font = pygame.font.Font(None, 28)
        self.dots = 0
        self.dot_timer = 0
    
    def update(self):
        """Update loading animation"""
        self.angle += 5
        self.dot_timer += 1
        if self.dot_timer >= 20:
            self.dots = (self.dots + 1) % 4
            self.dot_timer = 0
    
    def render(self, screen):
        """Draw loading screen"""
        screen.fill(BG_COLOR)
        
        # Title
        title_text = "Infinity Mode"
        title_surface = self.font.render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_surface, title_rect)
        
        # Loading spinner (simple circle animation)
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        radius = 40
        
        for i in range(8):
            angle = self.angle + (i * 45)
            x = center_x + int(radius * pygame.math.Vector2(1, 0).rotate(angle).x)
            y = center_y + int(radius * pygame.math.Vector2(1, 0).rotate(angle).y)
            
            # Fade effect
            alpha = int(255 * (i / 8))
            color = (alpha, alpha, alpha)
            pygame.draw.circle(screen, color, (x, y), 8)
        
        # Loading message
        dots_text = "." * self.dots
        message_text = f"Fetching random word{dots_text}"
        message_surface = self.message_font.render(message_text, True, BLACK)
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, center_y + 80))
        screen.blit(message_surface, message_rect)
        
        # Hint
        hint_text = "This may take a few seconds..."
        hint_surface = pygame.font.Font(None, 22).render(hint_text, True, (120, 120, 120))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(hint_surface, hint_rect)


class InfinityGameManager:
    """Manages Infinity Mode with API word fetching"""
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.loading_screen = LoadingScreen()
        self.vocab_game = None
        
        # Threading for API calls
        self.is_loading = False
        self.word_data = None
        self.load_error = False
        
        # Start loading first word
        self.start_loading_word()
    
    def start_loading_word(self):
        """Start fetching word in background thread"""
        self.is_loading = True
        self.load_error = False
        self.word_data = None
        
        # Start API call in separate thread
        thread = threading.Thread(target=self._fetch_word_thread)
        thread.daemon = True
        thread.start()
    
    def _fetch_word_thread(self):
        """Background thread to fetch word from API"""
        try:
            word, definition = get_random_word_with_definition(max_attempts=5)
            
            if word and definition:
                # Create temporary Word object (not saved to data)
                word_obj = Word(word, definition, status="infinity")
                self.word_data = word_obj
            else:
                # Use fallback
                print("API failed, using fallback word")
                word, definition = get_fallback_word()
                word_obj = Word(word, definition, status="infinity")
                self.word_data = word_obj
            
            self.is_loading = False
            
        except Exception as e:
            print(f"Error fetching word: {e}")
            self.load_error = True
            self.is_loading = False
    
    def handle_event(self, event):
        """Handle events"""
        if self.vocab_game:
            return self.vocab_game.handle_event(event)
        return None
    
    def update(self):
        """Update game state"""
        if self.is_loading:
            self.loading_screen.update()
        elif self.word_data and not self.vocab_game:
            # Word loaded, create game
            self.vocab_game = VocabGame(self.data_manager, self.word_data)
        elif self.vocab_game:
            self.vocab_game.update()
    
    def handle_animation_complete(self):
        """Handle animation completion in game"""
        if self.vocab_game:
            self.vocab_game.handle_animation_complete()
    
    def render(self, screen):
        """Render current state"""
        if self.is_loading:
            self.loading_screen.render(screen)
        elif self.load_error:
            self._render_error_screen(screen)
        elif self.vocab_game:
            self.vocab_game.render(screen)
    
    def _render_error_screen(self, screen):
        """Render error screen"""
        screen.fill(BG_COLOR)
        
        error_font = get_message_font()
        error_text = "Failed to load word"
        error_surface = error_font.render(error_text, True, (200, 50, 50))
        error_rect = error_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(error_surface, error_rect)
        
        hint_text = "Check your internet connection"
        hint_surface = pygame.font.Font(None, 24).render(hint_text, True, (120, 120, 120))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(hint_surface, hint_rect)
    
    def should_load_new_word(self):
        """Check if game is over and we should load next word"""
        if self.vocab_game and self.vocab_game.game_over:
            return True
        return False
    
    def load_next_word(self):
        """Load next word after game over"""
        self.vocab_game = None
        self.start_loading_word()