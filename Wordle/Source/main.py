import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Purrdle")
    
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            game.handle_event(event)
        
        game.draw(screen)

        pygame.display.update()

if __name__ == "__main__":
    main()