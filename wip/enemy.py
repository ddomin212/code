from typing import Any

import pygame
from entity import Entity

from helpers.support import import_folder


class Enemy(Entity):
    def __init__(
        self,
        monster_name,
        pos,
        groups,
        obstacle_sprites,
        damage_player,
        particle_func,
        enemy_xp,
    ) -> None:
        super().__init__(groups)

        self.animations = import_folder("../graphics/cow/")
        # print(self.animations)
        self.status = "idle"
        self.image = self.animations[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        self.monster_name = "cow"
        self.speed = 2
        self.notice_radius = 100

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2(0, 0)

        return distance, direction

    def get_status(self, player):
        distance, _ = self.get_player_distance_direction(player)
        if distance <= self.notice_radius:
            self.status = "move"
        else:
            self.status = "idle"

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.status]):
            if self.status == "attack":
                self.can_attack = False
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        self.flicker()

    def actions(self, player):
        if self.status == "move":
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def update(self) -> None:
        self.move(self.speed)
        self.animate()
        self.entity_cooldown()

    def enemy_update(self, player) -> None:  # jenom pro enemy kvuli vykonnosti
        self.get_status(player)
        self.actions(player)
