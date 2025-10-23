import pygame
import random
import sys
from settings import * 
from animations import AnimationManager, FlipAnimation, PopAnimation, ShakeAnimation
from button import Button
from assets import AssetManager
from keys import Keyboard

class Game:
    def __init__(self):
        self.word_list = self.load_words()
        self.secret_word = random.choice(self.word_list)
        print(f"Secret Word: {self.secret_word}") 
        
        self.guesses = []
        self.current_guess = []
        self.current_row = 0
        self.game_over = False
        self.game_message = ""
        self.won = False
        
        self.fonts = {
            "letter": get_letter_font(),
            "message": get_message_font(),
            "title": get_title_font(),
            "subtitle": get_subtitle_font()
        }
        
        self.animation_manager = AnimationManager()
        self.assets = AssetManager()
        self.keyboard = Keyboard(KEYBOARD_X, KEYBOARD_Y)
        
        self.restart_button = Button(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            BUTTON_Y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Restart",
            self.reset
        )
        self.can_input = True
        self.title_surface = self.fonts["title"].render(CAT_THEME["title"], True, BLACK)
        self.subtitle_surface = self.fonts["subtitle"].render(CAT_THEME["subtitle"], True, BLACK)
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.subtitle_rect = self.subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 105))
        self.decor_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        self.render_decorations(self.decor_surface)

    def load_words(self):
        try:
            with open("assets/words_of_5_old.txt", "r") as f:
                words = [line.strip().upper() for line in f.readlines()]
            return words
        except FileNotFoundError:
            print("Error: words_of_5_old.txt not found!")
            sys.exit()

    def reset(self):
        self.__init__() 

    def update(self):
        self.animation_manager.update()

    def handle_event(self, event):
        # Button events (mouse)
        if self.restart_button.handle_event(event):
            return
        
        # Keyboard click events
        keyboard_action = self.keyboard.handle_event(event)
        if keyboard_action:
            if not self.can_input or self.animation_manager.is_animating():
                return
            
            if keyboard_action == "BACK":
                if len(self.current_guess) > 0:
                    self.current_guess.pop()
            elif keyboard_action == "ENTER":
                if len(self.current_guess) == GRID_COLS:
                    self.submit_guess()
            else:  # Letter key
                if len(self.current_guess) < GRID_COLS:
                    self.current_guess.append(keyboard_action)
                    col = len(self.current_guess) - 1
                    self.animation_manager.add(PopAnimation(self.current_row, col))
            return
        
        # Physical keyboard events
        if event.type != pygame.KEYDOWN:
            return

        # Don't allow input during animations
        if not self.can_input or self.animation_manager.is_animating():
            return
            
        if event.key == pygame.K_BACKSPACE:
            if len(self.current_guess) > 0:
                self.current_guess.pop()
        elif event.key == pygame.K_RETURN and len(self.current_guess) == GRID_COLS:
            self.submit_guess()
        elif len(self.current_guess) < GRID_COLS and event.unicode.isalpha():
            self.current_guess.append(event.unicode.upper())
            # Add pop animation for the newly typed letter
            col = len(self.current_guess) - 1
            self.animation_manager.add(PopAnimation(self.current_row, col))

    def submit_guess(self):
        guess_str = "".join(self.current_guess)
        if guess_str not in self.word_list:
            print(f"Invalid word: {guess_str}") 
            # Add shake animation for invalid word
            self.animation_manager.add(ShakeAnimation(self.current_row))
            return

        colors = self.check_guess(guess_str)
        self.guesses.append(list(zip(self.current_guess, colors)))
        
        # Update keyboard colors
        self.keyboard.update_from_guess(self.current_guess, colors)
        
        # Add flip animations for each tile
        for col in range(GRID_COLS):
            delay = col * FLIP_DELAY
            self.animation_manager.add(FlipAnimation(self.current_row, col, delay))
        
        # Disable input during flip animation
        self.can_input = False
        
        # Check win/lose after animation completes
        total_animation_time = FLIP_DURATION + (GRID_COLS - 1) * FLIP_DELAY
        pygame.time.set_timer(pygame.USEREVENT, total_animation_time, 1)
        
        if guess_str == self.secret_word:
            self.won = True
            self.game_message = random.choice(CAT_THEME["win_messages"])
        elif self.current_row == GRID_ROWS - 1: 
            self.won = False
            self.game_message = random.choice(CAT_THEME["lose_messages"])
            
        self.current_row += 1
        self.current_guess.clear()

    def handle_animation_complete(self):
        self.can_input = True
        if self.game_message:
            self.game_over = True

    def check_guess(self, guess_str):
        feedback = []
        secret_list = list(self.secret_word)

        # Green pass
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
                    secret_list.remove(guess_str[i])
                else:
                    feedback[i] = "gray"
        return feedback

    def render_tile(self, screen, row, col, letter=None, color_name=None, is_current=False):
        x = GRID_START_X + col * (SQUARE_SIZE + SQUARE_PADDING)
        y = GRID_START_Y + row * (SQUARE_SIZE + SQUARE_PADDING)
        
        # Apply shake animation
        shake_offset = self.animation_manager.get_shake_offset(row)
        x += shake_offset
        
        rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
        
        # Apply pop animation for current input
        if is_current and letter:
            pop_scale = self.animation_manager.get_pop_scale(row, col)
            original_center = rect.center
            rect.width = int(SQUARE_SIZE * pop_scale)
            rect.height = int(SQUARE_SIZE * pop_scale)
            rect.center = original_center
        
        # Apply flip animation for submitted guesses
        if color_name and row < self.current_row:
            flip_scale = self.animation_manager.get_flip_scale(row, col)
            original_center = rect.center
            rect.height = int(SQUARE_SIZE * flip_scale)
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
            text_surface = self.fonts["letter"].render(letter, True, text_color)
            text_rect = text_surface.get_rect(center=(rect.centerx, rect.centery + 2))
            screen.blit(text_surface, text_rect)
            
            # Add small paw print decoration on completed tiles
            if color_name and self.assets.has("paw_small"):
                paw_x = rect.right - 10
                paw_y = rect.bottom - 10
                self.assets.draw(screen, "paw_small", (paw_x, paw_y), size=(14, 14), center=True)

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

    def render(self, screen):
        screen.fill(BG_COLOR)
        
        # Draw background decorations
        screen.blit(self.decor_surface, (0, 0))
        
        # --- Draw cached title + subtitle ---
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.subtitle_surface, self.subtitle_rect)
        
        # Draw title with logo
        if self.assets.has("logo"):
            logo_y = self.title_rect.centery - 12
            self.assets.draw(screen, "logo", (SCREEN_WIDTH // 2 - 170, logo_y), size=(100, 100), center=True)
            self.assets.draw(screen, "logo", (SCREEN_WIDTH // 2 + 170, logo_y), size=(100, 100), center=True)
        
        # Draw grid
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
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

        # Draw game over message and cat
        if self.game_over:
            message_y = GRID_START_Y + (GRID_ROWS * (SQUARE_SIZE + SQUARE_PADDING)) + 10
            
            # Draw cat image based on win/lose
            cat_image_key = "cat_win" if self.won else "cat_lose"
            if self.assets.has(cat_image_key):
                cat_y = message_y - 60
                self.assets.draw(screen, cat_image_key, (SCREEN_WIDTH // 2, cat_y), size=(100, 100), center=True)
            
            # Draw message
            message_surface = self.fonts["message"].render(self.game_message, True, BLACK)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, message_y))
            screen.blit(message_surface, message_rect)
            
            # Show secret word if lost
            if not self.won:
                word_y = message_y + 35
                word_text = f"Word: {self.secret_word}"
                word_surface = self.fonts["message"].render(word_text, True, BLACK)
                word_rect = word_surface.get_rect(center=(SCREEN_WIDTH // 2, word_y))
                screen.blit(word_surface, word_rect)
        
        # Draw restart button
        self.restart_button.render(screen)
        
        # Draw keyboard
        self.keyboard.render(screen)