import pygame
import random
import sys
from settings import * 

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

    def load_words(self):
        try:
            with open("words_of_5.txt", "r") as f:
                words = [line.strip().upper() for line in f.readlines()]
            return words
        except FileNotFoundError:
            print("Error: words_of_5.txt not found!")
            sys.exit()

    def reset(self):
        self.__init__() 

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.game_over:
            self.reset()
            return
            
        if event.key == pygame.K_BACKSPACE:
            if len(self.current_guess) > 0:
                self.current_guess.pop()
        elif event.key == pygame.K_RETURN and len(self.current_guess) == GRID_COLS:
            self.submit_guess()
        elif len(self.current_guess) < GRID_COLS and event.unicode.isalpha():
            self.current_guess.append(event.unicode.upper())

    def submit_guess(self):
        guess_str = "".join(self.current_guess)
        if guess_str not in self.word_list:
            print(f"Invalid word: {guess_str}") 
            return

        colors = self.check_guess(guess_str)
        self.guesses.append(list(zip(self.current_guess, colors)))
        
        if guess_str == self.secret_word:
            self.game_message = "You Win!"
            self.game_over = True
        elif self.current_row == GRID_ROWS -1: 
            self.game_message = f"The word was: {self.secret_word}"
            self.game_over = True
            
        self.current_row += 1
        self.current_col = 0
        self.current_guess.clear()

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

    def render(self, screen):
        screen.fill(WHITE)
        
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = GRID_START_X + col * (SQUARE_SIZE + SQUARE_PADDING)
                y = GRID_START_Y + row * (SQUARE_SIZE + SQUARE_PADDING)
                rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)

                if row < self.current_row:
                    letter, color_name = self.guesses[row][col]
                    tile_color = COLOR_MAP.get(color_name, GRAY)
                    pygame.draw.rect(screen, tile_color, rect, border_radius=3)
                    text_surface = LETTER_FONT.render(letter, True, FILLED_TEXT_COLOR)
                    text_rect = text_surface.get_rect(center=rect.center)
                    screen.blit(text_surface, text_rect)
                elif row == self.current_row:
                    pygame.draw.rect(screen, OUTLINE_GRAY, rect, 2, border_radius=3)
                    if col < len(self.current_guess):
                        letter = self.current_guess[col]
                        text_surface = LETTER_FONT.render(letter, True, EMPTY_TEXT_COLOR)
                        text_rect = text_surface.get_rect(center=rect.center)
                        screen.blit(text_surface, text_rect)
                else:
                    pygame.draw.rect(screen, OUTLINE_GRAY, rect, 2, border_radius=3)

        if self.game_over:
            message_surface = MESSAGE_FONT.render(self.game_message, True, BLACK)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, GRID_START_Y + (GRID_ROWS * (SQUARE_SIZE + SQUARE_PADDING)) + 25))
            screen.blit(message_surface, message_rect)
