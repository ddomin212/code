from random import choice, randint

import pygame

from helpers.settings import *
from helpers.support import *
from objects.sprites import Generic


class Sky:
    """sky class for day and night cycle"""

    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.full_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]
        self.end_color = (38, 101, 189)

    def display(self, dt):
        """handle the day and night cycle

        Args:
            dt: delta time
        """
        for idx, value in enumerate(self.end_color):
            if self.start_color[idx] > value:
                self.start_color[idx] -= 2 * dt
        self.full_surface.fill(self.start_color)
        self.display_surface.blit(
            self.full_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )


class Drop(Generic):
    """drop object for the rain effect

    Args:
        Generic: generic sprite class
    """

    def __init__(self, surf, pos, moving, groups, z) -> None:
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        self.moving = moving
        if self.moving:  # attributes for moving anything in pygame
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt):
        """make the drop fall down

        Args:
            dt: delta time
        """
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = round(self.pos.x), round(self.pos.y)
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    """rain class for rain effect"""

    def __init__(self, all_sprites) -> None:
        self.all_sprites = all_sprites
        self.rain_drops = import_folder("../graphics/rain/drops/")
        self.rain_surfs = import_folder("../graphics/rain/floor/")
        self.floor_w, self.floor_h = pygame.image.load(
            "../graphics/world/ground.png"
        ).get_size()

    def create_floor(self):
        """generate rain effects on the ground"""
        Drop(
            choice(self.rain_surfs),
            (randint(0, self.floor_w), randint(0, self.floor_h)),
            False,
            self.all_sprites,
            LAYERS["rain floor"],
        )

    def create_rain(self):
        """generate rain drops in the sky"""
        Drop(
            choice(self.rain_drops),
            (randint(0, self.floor_w), randint(0, self.floor_h)),
            True,
            self.all_sprites,
            LAYERS["rain drops"],
        )

    def update(self, dt):
        """update the rain effect

        Args:
            dt: delta time
        """
        self.create_floor()
        self.create_rain()
