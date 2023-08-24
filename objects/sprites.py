from random import choice, randint
from typing import Any

import pygame

from helpers.settings import *
from helpers.settings import LAYERS
from helpers.timer import Timer


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS["main"]) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75
        )


class Water(Generic):
    def __init__(self, pos, frames, groups) -> None:
        self.frames = frames
        self.frame_index = 0

        super().__init__(
            pos=pos,
            surf=self.frames[self.frame_index],
            groups=groups,
            z=LAYERS["water"],
        )

    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class WildFlower(Generic):
    def __init__(self, pos, surf, groups) -> None:
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=100) -> None:
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.flash()

    def flash(self):
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.kill()


class Tree(Generic):
    def __init__(self, pos, surf, groups, name, player_add) -> None:
        super().__init__(pos, surf, groups)

        self.health = 5
        self.alive = True
        self.stump = pygame.image.load(
            f'../graphics/stumps/{"small" if name=="Small" else "large"}.png'
        ).convert_alpha()

        self.invul_timer = Timer(200)
        self.player_add = player_add

        self.get_fruit(name)

    def get_fruit(self, name):
        self.apple = pygame.image.load(
            "../graphics/fruit/apple.png"
        ).convert_alpha()
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

    def damage(self):
        self.health -= 1

        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                random_apple.rect.topleft,
                random_apple.image,
                self.groups()[0],
                LAYERS["fruit"],
            )
            self.player_add("apple")
            choice(self.apple_sprites.sprites()).kill()

    def check_death(self):
        if self.health <= 0:
            Particle(
                self.rect.topleft,
                self.image,
                self.groups()[0],
                LAYERS["main"],
            )
            self.player_add("wood")
            self.rect = self.stump.get_rect(midbottom=self.rect.midbottom)
            self.image = self.stump
            self.hitbox = self.rect.copy().inflate(
                -10, -self.rect.height * 0.6
            )
            self.alive = False

    def update(self, dt):
        if self.alive:
            self.check_death()

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                apple_pos = (
                    self.rect.left + pos[0],
                    self.rect.top + pos[1],
                )
                Generic(
                    apple_pos,
                    self.apple,
                    [self.apple_sprites, self.groups()[0]],
                    z=LAYERS["fruit"],
                )


class Interaction(Generic):
    def __init__(self, pos, size, groups, name) -> None:
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name
