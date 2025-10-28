import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from data_manager import DataManager
from main_menu import MainMenu
from word_input_page import WordInputPage
from mode_select import ModeSelectPage
from vocab_game import VocabGame
from word_list_page import WordListPage
from infinity_game import InfinityGameManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("🐱 Purrdle - Vocabulary Learning 🐱")
    clock = pygame.time.Clock()
    
    # Initialize data manager
    data_manager = DataManager("data/vocabulary.json")
    
    # Pages
    current_page = "menu"
    menu = MainMenu(data_manager)
    word_input_page = WordInputPage(data_manager)
    mode_select_page = ModeSelectPage(data_manager)
    word_list_page = WordListPage(data_manager)
    vocab_game = None  # Initialize when starting learning mode
    infinity_manager = None  # Initialize when starting infinity mode
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Animation complete event for games
            if event.type == pygame.USEREVENT:
                if vocab_game:
                    vocab_game.handle_animation_complete()
                elif infinity_manager:
                    infinity_manager.handle_animation_complete()
            
            # Handle events based on current page
            if current_page == "menu":
                result = menu.handle_event(event)
                if result == "play":
                    current_page = "mode_select"
                elif result == "add_words":
                    current_page = "add_words"
                elif result == "word_list":
                    word_list_page.update_word_list()  # Refresh list
                    current_page = "word_list"
            
            elif current_page == "add_words":
                result = word_input_page.handle_event(event)
                if result == "back":
                    current_page = "menu"
                    menu.update_stats()  # Refresh stats
            
            elif current_page == "word_list":
                result = word_list_page.handle_event(event)
                if result == "back":
                    current_page = "menu"
                    menu.update_stats()  # Refresh stats
            
            elif current_page == "mode_select":
                result = mode_select_page.handle_event(event)
                if result == "back":
                    current_page = "menu"
                    menu.update_stats()
                elif result == "learning":
                    # Check if user has words
                    stats = data_manager.get_statistics()
                    if stats["total"] > 0:
                        # Get a random word
                        word_obj = data_manager.get_random_word_weighted()
                        vocab_game = VocabGame(data_manager, word_obj)
                        current_page = "vocab_game"
                    else:
                        print("No words available! Add words first.")
                elif result == "infinity":
                    # Start infinity mode
                    infinity_manager = InfinityGameManager(data_manager)
                    current_page = "infinity_game"
            
            elif current_page == "vocab_game":
                result = vocab_game.handle_event(event)
                if result == "back":
                    current_page = "mode_select"
                    vocab_game = None
                elif result == "continue":
                    # Get next word
                    word_obj = data_manager.get_random_word_weighted()
                    vocab_game = VocabGame(data_manager, word_obj)
            
            elif current_page == "infinity_game":
                result = infinity_manager.handle_event(event)
                if result == "back":
                    current_page = "mode_select"
                    infinity_manager = None
                elif result == "continue":
                    # Load next random word from API
                    infinity_manager.load_next_word()
        
        # Update
        if current_page == "add_words":
            word_input_page.update()
        elif current_page == "vocab_game" and vocab_game:
            vocab_game.update()
        elif current_page == "infinity_game" and infinity_manager:
            infinity_manager.update()
        
        # Render
        if current_page == "menu":
            menu.render(screen)
        elif current_page == "add_words":
            word_input_page.render(screen)
        elif current_page == "mode_select":
            mode_select_page.render(screen)
        elif current_page == "word_list":
            word_list_page.render(screen)
        elif current_page == "vocab_game" and vocab_game:
            vocab_game.render(screen)
        elif current_page == "infinity_game" and infinity_manager:
            infinity_manager.render(screen)
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()