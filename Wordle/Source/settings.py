import pygame

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 850

WHITE = (255, 255, 255)
BLACK = (58, 54, 52)  # Soft black 
CREAM = (255, 251, 250)  # Warm cream background
LIGHT_PINK = (255, 228, 225)  # Soft pink
PEACH = (255, 218, 193)  # Peachy tone

# Tile colors
CAT_GREEN = (168, 218, 181)      # Soft mint green 
CAT_YELLOW = (255, 213, 128)     # Warm golden yellow 
CAT_GRAY = (169, 164, 175)       # Soft purple-gray 
CAT_ORANGE = (255, 183, 147)     # Coral orange 

# UI Colors
BUTTON_BG = (255, 192, 203)      # Pink button
BUTTON_HOVER = (255, 160, 180)   # Darker pink hover
BUTTON_TEXT = (88, 64, 82)       # Dark mauve text
OUTLINE_COLOR = (220, 210, 215)  # Soft outline
BG_COLOR = CREAM                 # Warm cream background

GRID_ROWS = 6
GRID_COLS = 5
SQUARE_SIZE = 62  
SQUARE_PADDING = 8
GRID_START_X = (SCREEN_WIDTH - (GRID_COLS * SQUARE_SIZE + (GRID_COLS - 1) * SQUARE_PADDING)) // 2
GRID_START_Y = 180

# Font & Color Mapping
FILLED_TEXT_COLOR = WHITE
EMPTY_TEXT_COLOR = BLACK
OUTLINE_GRAY = OUTLINE_COLOR
COLOR_MAP = {
    "green": CAT_GREEN,
    "yellow": CAT_YELLOW,
    "gray": CAT_GRAY
}

# Animation settings
FLIP_DURATION = 400  # ms per tile
FLIP_DELAY = 150     # ms between tiles
POP_DURATION = 50    # ms
SHAKE_DURATION = 400 # ms
SHAKE_INTENSITY = 8  # pixels

# Button settings
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 50
BUTTON_Y = SCREEN_HEIGHT - 100

IMAGE_PATHS = {
    "logo": "assets/cat_logo.png",
    
    "cat_win": "assets/cat_happy.png",
    "cat_lose": "assets/cat_sad.png",
    
    "paw_print": "assets/paw_print.png",
    "yarn_ball": "assets/yarn_ball.png",

    "paw_small": "assets/paw_small.png",
}

# Cat theme settings
CAT_THEME = {
    "title": "PURRDLE",
    "subtitle": " Guess the word! ",
    "win_messages": [
        "Purr-fect! ",
        "Meow-velous! ",
        "Cat-tastic! ",
        "Paw-some! ",
        "You're the cat's meow!"
    ],
    "lose_messages": [
        "Curiosity got the cat... ",
        "Not this time, kitty! ",
        "Better luck meow! "
    ]
}

def get_letter_font():
    return pygame.font.Font(None, 52)  

def get_message_font(): 
    return pygame.font.Font("assets/fonts/Comfortaa-Regular.ttf", 34)

def get_title_font():
    return pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", 64)  

def get_subtitle_font():
    return pygame.font.Font("assets/fonts/Comfortaa-Regular.ttf", 28)

def get_button_font():
    return pygame.font.Font("assets/fonts/Comfortaa-Regular.ttf", 30)