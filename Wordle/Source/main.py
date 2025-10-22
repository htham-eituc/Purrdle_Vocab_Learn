import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Purrdle")
    clock = pygame.time.Clock()
    
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT:
                game.handle_animation_complete()
            else:
                game.handle_event(event)
        
        game.render(screen)
        pygame.display.update()
        clock.tick(30)  

if __name__ == "__main__":
    main()