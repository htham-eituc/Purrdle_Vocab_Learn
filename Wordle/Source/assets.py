import pygame
import os
from settings import IMAGE_PATHS

class AssetManager:
    def __init__(self):
        self.images = {}
        self.load_all_assets()
    
    def load_all_assets(self):
        for key, path in IMAGE_PATHS.items():
            try:
                if os.path.exists(path):
                    image = pygame.image.load(path).convert_alpha()
                    self.images[key] = image
                    print(f"Loaded: {path}")
                else:
                    print(f"Missing: {path} (will use placeholder)")
                    self.images[key] = None
            except Exception as e:
                print(f"Error loading {path}: {e}")
                self.images[key] = None
    
    def get(self, key, size=None):
        image = self.images.get(key)
        if image and size:
            return pygame.transform.smoothscale(image, size)
        return image
    
    def has(self, key):
        return self.images.get(key) is not None
    
    def draw(self, screen, key, pos, size=None, center=False):
        image = self.get(key, size)
        if image:
            rect = image.get_rect()
            if center:
                rect.center = pos
            else:
                rect.topleft = pos
            screen.blit(image, rect)
            return True
        return False
    
    def draw_tiled(self, screen, key, area_rect, tile_size=(32, 32)):
        image = self.get(key, tile_size)
        if not image:
            return
        
        for x in range(area_rect.left, area_rect.right, tile_size[0]):
            for y in range(area_rect.top, area_rect.bottom, tile_size[1]):
                screen.blit(image, (x, y))