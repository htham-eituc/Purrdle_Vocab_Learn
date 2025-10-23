import pygame
import math
from settings import *

class Animation:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.finished = False
    
    def get_progress(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = min(elapsed / self.duration, 1.0)
        if progress >= 1.0:
            self.finished = True
        return progress
    
    def update(self):
        pass

class FlipAnimation(Animation):
    def __init__(self, row, col, delay=0):
        super().__init__(FLIP_DURATION)
        self.row = row
        self.col = col
        self.delay = delay
        self.start_time += delay
        self.scale_y = 1.0
    
    def update(self):
        if pygame.time.get_ticks() < self.start_time:
            return 1.0
        
        progress = self.get_progress()
        if progress < 0.5:
            self.scale_y = 1.0 - (progress * 2)
        else:
            self.scale_y = (progress - 0.5) * 2
        return self.scale_y

class PopAnimation(Animation):
    def __init__(self, row, col):
        super().__init__(POP_DURATION)
        self.row = row
        self.col = col
        self.scale = 1.0
    
    def update(self):
        progress = self.get_progress()
        if progress < 0.5:
            self.scale = 1.0 + (0.15 * (progress * 2))
        else:
            self.scale = 1.15 - (0.15 * ((progress - 0.5) * 2))
        return self.scale

class ShakeAnimation(Animation):
    def __init__(self, row):
        super().__init__(SHAKE_DURATION)
        self.row = row
        self.offset_x = 0
    
    def update(self):
        progress = self.get_progress()
        frequency = 4
        damping = 1.0 - progress
        self.offset_x = SHAKE_INTENSITY * math.sin(progress * frequency * 2 * math.pi) * damping
        return self.offset_x

class AnimationManager:
    def __init__(self):
        self.animations = []
    
    def add(self, animation):
        self.animations.append(animation)
    
    def update(self):
        for anim in self.animations[:]:
            anim.update()
            if anim.finished:
                self.animations.remove(anim)
    
    def get_flip_scale(self, row, col):
        for anim in self.animations:
            if isinstance(anim, FlipAnimation) and anim.row == row and anim.col == col:
                return anim.scale_y
        return 1.0
    
    def get_pop_scale(self, row, col):
        for anim in self.animations:
            if isinstance(anim, PopAnimation) and anim.row == row and anim.col == col:
                return anim.scale
        return 1.0
    
    def get_shake_offset(self, row):
        for anim in self.animations:
            if isinstance(anim, ShakeAnimation) and anim.row == row:
                return anim.offset_x
        return 0
    
    def is_animating(self):
        return any(
            not isinstance(anim, PopAnimation)
            for anim in self.animations
        )
    
    def clear(self):
        self.animations.clear()