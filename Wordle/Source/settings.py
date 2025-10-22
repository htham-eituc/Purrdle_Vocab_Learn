import pygame

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (106, 170, 100)
YELLOW = (201, 180, 88)

# Grid settings
GRID_ROWS = 6
GRID_COLS = 5
SQUARE_SIZE = 75
SQUARE_PADDING = 10
GRID_START_X = (SCREEN_WIDTH - (GRID_COLS * SQUARE_SIZE + (GRID_COLS - 1) * SQUARE_PADDING)) // 2
GRID_START_Y = 50

# Font & Color Mapping
LETTER_FONT = pygame.font.Font(None, 60)
MESSAGE_FONT = pygame.font.Font(None, 40)
FILLED_TEXT_COLOR = WHITE
EMPTY_TEXT_COLOR = BLACK
OUTLINE_GRAY = (211, 211, 211)
COLOR_MAP = {
    "green": GREEN,
    "yellow": YELLOW,
    "gray": (120, 124, 126)
}