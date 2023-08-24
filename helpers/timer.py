import pygame


class Timer:  # cooldown function class - finally
    def __init__(self, duration, func=None):
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False

    def activate(self):
        """Activate cooldown"""
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        """Deactivate cooldown"""
        self.active = False
        self.start_time = 0

    def update(self):
        """Update cooldown vars"""
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()
