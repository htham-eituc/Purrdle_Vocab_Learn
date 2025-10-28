import pygame
import sys
from settings import * 
from animations import AnimationManager, FlipAnimation, PopAnimation, ShakeAnimation
from button import Button
from assets import AssetManager
from data_manager import DataManager

class VocabGame:
    """Vocabulary learning game with dynamic grid"""
    def __init__(self, data_manager, word_obj):
        self.data_manager = data_manager
        self.word_obj = word_obj  # Word object from data_manager
        
        # Game settings
        self.secret_word = word_obj.get_grid_word() 
        self.word_length = word_obj.get_display_length()  
        self.definition = word_obj.definition
        
        print(f"Secret Word: {self.secret_word} (length: {self.word_length})")
        
        # Dynamic grid settings
        self.grid_rows = 3  # Only 3 attempts!
        self.grid_cols = self.word_length
        
        # Calculate dynamic tile size and positioning
        self.calculate_grid_dimensions()
        
        self.guesses = []
        self.current_guess = []
        self.current_row = 0
        self.game_over = False
        self.game_message = ""
        self.won = False
        self.attempts_used = 0
        
        self.fonts = {
            "letter": self.get_dynamic_letter_font(),
            "message": get_message_font(),
            "title": get_title_font(),
            "definition": pygame.font.Font(None, 28)
        }
        
        self.animation_manager = AnimationManager()
        self.assets = AssetManager()
        
        # Back button (top left)
        self.back_button = Button(20, 20, 100, 40, "← Back", lambda: None, 18)
        
        # Continue button (after game over)
        self.continue_button = Button(
            SCREEN_WIDTH // 2 - 75,
            SCREEN_HEIGHT - 100,
            150,
            50,
            "Continue",
            lambda: None
        )
        
        self.can_input = True
        
        # Cache surfaces
        self.def_surfaces = self.render_definition_wrapped()
        self.decor_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.render_decorations(self.decor_surface)
    
    def calculate_grid_dimensions(self):
        """Calculate tile size and grid position based on word length"""
        # Max tile size
        max_tile_size = 75
        min_tile_size = 40
        
        # Calculate tile size to fit screen
        available_width = SCREEN_WIDTH - 100  # margins
        max_width_per_tile = available_width // self.grid_cols
        
        self.tile_size = min(max_tile_size, max(min_tile_size, max_width_per_tile - 8))
        self.tile_padding = 6
        
        # Calculate grid position (centered)
        grid_width = self.grid_cols * (self.tile_size + self.tile_padding) - self.tile_padding
        self.grid_start_x = (SCREEN_WIDTH - grid_width) // 2
        self.grid_start_y = 250
    
    def get_dynamic_letter_font(self):
        """Get font size based on tile size"""
        font_size = int(self.tile_size * 0.7)
        return pygame.font.Font(None, font_size)
    
    def render_decorations(self, screen):
        # Corner decorations - cats
        if self.assets.has("cat1"):
            self.assets.draw(self.decor_surface, "cat1", (15, 30), size=(80, 80))
        if self.assets.has("cat2"):
            self.assets.draw(self.decor_surface, "cat2", (SCREEN_WIDTH - 85, 30), size=(80, 80))
        # Scattered paw prints
            paw_positions = [
                (40, SCREEN_HEIGHT - 130),
                (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 150),
                (60, 250),
                (SCREEN_WIDTH - 80, 280),
                (35, 450),
                (SCREEN_WIDTH - 60, 500),
                (120, 100),
                (SCREEN_WIDTH // 2 - 150, 200),
                (SCREEN_WIDTH // 2 + 180, 400),
                (SCREEN_WIDTH // 3, SCREEN_HEIGHT - 220),
                (SCREEN_WIDTH // 1.5, SCREEN_HEIGHT - 300),
            ]
            for pos in paw_positions:
                self.assets.draw(self.decor_surface, "paw_print", pos, size=(50, 50), center=True)

    def render_definition_wrapped(self):
        """Pre-render definition with word wrapping"""
        words = self.definition.split()
        lines = []
        current_line = ""
        max_width = SCREEN_WIDTH - 100
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.fonts["definition"].render(test_line, True, BLACK)
            if test_surface.get_width() < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # Render each line
        surfaces = []
        for line in lines[:3]:  # Max 3 lines
            surface = self.fonts["definition"].render(line, True, BLACK)
            surfaces.append(surface)
        
        return surfaces
    
    def handle_event(self, event):
        # Back button
        if self.back_button.handle_event(event):
            return "back"
        
        # Continue button (only after game over)
        if self.game_over:
            if self.continue_button.handle_event(event):
                return "continue"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return "continue"
        
        # Keyboard events
        if event.type != pygame.KEYDOWN:
            return None
        
        # Don't allow input during animations or after game over
        if not self.can_input or self.animation_manager.is_animating():
            return None
        
        if self.game_over:
            return None
        
        if event.key == pygame.K_BACKSPACE:
            if len(self.current_guess) > 0:
                self.current_guess.pop()
        elif event.key == pygame.K_RETURN and len(self.current_guess) == self.grid_cols:
            self.submit_guess()
        elif len(self.current_guess) < self.grid_cols:
            char = event.unicode.upper()
            # Allow letters, spaces, and hyphens
            if char.isalpha() or char == ' ' or char == '-':
                self.current_guess.append(char)
                col = len(self.current_guess) - 1
                self.animation_manager.add(PopAnimation(self.current_row, col))
        
        return None
    
    def submit_guess(self):
        guess_str = "".join(self.current_guess)
        
        # Check if guess matches secret word
        colors = self.check_guess(guess_str)
        self.guesses.append(list(zip(self.current_guess, colors)))
        self.attempts_used += 1
        
        # Add flip animations
        for col in range(self.grid_cols):
            delay = col * FLIP_DELAY
            self.animation_manager.add(FlipAnimation(self.current_row, col, delay))
        
        # Disable input during animation
        self.can_input = False
        
        # Check win/lose after animation
        total_animation_time = FLIP_DURATION + (self.grid_cols - 1) * FLIP_DELAY
        pygame.time.set_timer(pygame.USEREVENT, total_animation_time, 1)
        
        if guess_str == self.secret_word:
            self.won = True
            if self.attempts_used == 1:
                self.game_message = "Perfect! First try! "
            else:
                self.game_message = f"Great job! ({self.attempts_used} tries)"
        elif self.current_row == self.grid_rows - 1:
            # Failed all attempts
            self.won = False
            self.game_message = f"The answer was: {self.secret_word}"
        
        self.current_row += 1
        self.current_guess.clear()
    
    
    def handle_animation_complete(self):
        """Called when animations complete"""
        self.can_input = True
        if self.game_message:
            self.game_over = True
            # Update word status in data manager (only for learning mode)
            if self.word_obj.status != "infinity":
                self.data_manager.update_word_status(
                    self.word_obj.word,
                    self.won,
                    self.attempts_used
                )
    
    def check_guess(self, guess_str):
        """Check guess against secret word (supports spaces and hyphens)"""
        feedback = []
        secret_list = list(self.secret_word)
        
        # Green pass - exact position matches
        for i in range(len(guess_str)):
            if guess_str[i] == secret_list[i]:
                feedback.append("green")
                secret_list[i] = None
            else:
                feedback.append(None)
        
        # Yellow/Gray pass
        for i in range(len(guess_str)):
            if feedback[i] is None:
                if guess_str[i] in secret_list:
                    feedback[i] = "yellow"
                    secret_list[secret_list.index(guess_str[i])] = None
                else:
                    feedback[i] = "gray"
        
        return feedback
    
    def render_tile(self, screen, row, col, letter=None, color_name=None, is_current=False):
        """Render a single tile with animations"""
        x = self.grid_start_x + col * (self.tile_size + self.tile_padding)
        y = self.grid_start_y + row * (self.tile_size + self.tile_padding)
        
        # Apply shake animation
        shake_offset = self.animation_manager.get_shake_offset(row)
        x += shake_offset
        
        rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
        
        # Apply pop animation for current input
        if is_current and letter:
            pop_scale = self.animation_manager.get_pop_scale(row, col)
            original_center = rect.center
            rect.width = int(self.tile_size * pop_scale)
            rect.height = int(self.tile_size * pop_scale)
            rect.center = original_center
        
        # Apply flip animation for submitted guesses
        if color_name and row < self.current_row:
            flip_scale = self.animation_manager.get_flip_scale(row, col)
            original_center = rect.center
            rect.height = int(self.tile_size * flip_scale)
            rect.center = original_center
            
            # Show color only in second half of flip
            if flip_scale > 0.5:
                tile_color = COLOR_MAP.get(color_name, CAT_GRAY)
            else:
                tile_color = WHITE
            
            pygame.draw.rect(screen, tile_color, rect, border_radius=5)
            pygame.draw.rect(screen, OUTLINE_GRAY, rect, 2, border_radius=5)
        elif color_name:
            # Completed tiles (no animation)
            tile_color = COLOR_MAP.get(color_name, CAT_GRAY)
            pygame.draw.rect(screen, tile_color, rect, border_radius=5)
        else:
            # Empty or current input tiles
            pygame.draw.rect(screen, WHITE, rect, border_radius=5)
            pygame.draw.rect(screen, OUTLINE_GRAY, rect, 2, border_radius=5)
        
        # Render letter
        if letter:
            text_color = FILLED_TEXT_COLOR if color_name else EMPTY_TEXT_COLOR
            # Special rendering for space
            if letter == ' ':
                display_letter = '_'
            else:
                display_letter = letter
            
            text_surface = self.fonts["letter"].render(display_letter, True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
    
    def update(self):
        """Update animations"""
        self.animation_manager.update()
    
    def render(self, screen):
        """Render the game"""
        screen.fill(BG_COLOR)
        
         # Draw background decorations
        screen.blit(self.decor_surface, (0, 0))
        
        # Back button
        self.back_button.render(screen)
        
        # Title
        title_text = "Vocab Challenge"
        title_surface = self.fonts["title"].render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)
        
        # Definition box
        def_box_y = 100
        def_box_height = 120
        def_box = pygame.Rect(50, def_box_y, SCREEN_WIDTH - 100, def_box_height)
        pygame.draw.rect(screen, WHITE, def_box, border_radius=10)
        pygame.draw.rect(screen, CAT_YELLOW, def_box, 3, border_radius=10)
        
        # Definition label
        def_label = self.fonts["definition"].render("Definition:", True, BLACK)
        screen.blit(def_label, (60, def_box_y + 10))
        
        # Definition text (wrapped)
        y_offset = def_box_y + 40
        for surface in self.def_surfaces:
            text_rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(surface, text_rect)
            y_offset += 30
        
        # Grid
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if row < len(self.guesses):
                    # Submitted guess
                    letter, color_name = self.guesses[row][col]
                    self.render_tile(screen, row, col, letter, color_name)
                elif row == self.current_row:
                    # Current input row
                    if col < len(self.current_guess):
                        letter = self.current_guess[col]
                        self.render_tile(screen, row, col, letter, is_current=True)
                    else:
                        self.render_tile(screen, row, col)
                else:
                    # Empty row
                    self.render_tile(screen, row, col)
        
        # Attempt counter
        attempts_text = f"Attempt: {self.current_row + 1}/{self.grid_rows}"
        attempts_surface = pygame.font.Font(None, 26).render(attempts_text, True, BLACK)
        attempts_rect = attempts_surface.get_rect(center=(SCREEN_WIDTH // 2, self.grid_start_y + (self.grid_rows * (self.tile_size + self.tile_padding)) + 20))
        screen.blit(attempts_surface, attempts_rect)
        
        # Game over screen
        if self.game_over:
            message_y = attempts_rect.bottom + 40
            
            # Cat image
            cat_image_key = "cat_win" if self.won else "cat_lose"
            if self.assets.has(cat_image_key):
                cat_y = message_y - 60
                self.assets.draw(screen, cat_image_key, (SCREEN_WIDTH // 2, cat_y), size=(100, 100), center=True)
            
            # Message
            message_surface = self.fonts["message"].render(self.game_message, True, BLACK)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, message_y))
            screen.blit(message_surface, message_rect)
            
            # Status update info
            status_text = f"Status: {self.word_obj.status.replace('_', ' ').title()}"
            status_color = CAT_GREEN if self.won else (CAT_YELLOW if self.attempts_used > 1 else (200, 50, 50))
            status_surface = pygame.font.Font(None, 24).render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, message_y + 35))
            screen.blit(status_surface, status_rect)
            
            # Continue button
            self.continue_button.render(screen)
        
        # Instructions at bottom (only when not game over)
        if not self.game_over:
            hint_text = "Type letters, Space, or Hyphen (-) | ENTER to submit | BACKSPACE to delete"
            hint_surface = pygame.font.Font(None, 20).render(hint_text, True, (120, 120, 120))
            hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            screen.blit(hint_surface, hint_rect)