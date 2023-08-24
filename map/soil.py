from random import choice

import pygame
from pytmx.util_pygame import load_pygame

from helpers.settings import *
from helpers.support import *


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["soil"]


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["soil water"]


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered) -> None:
        super().__init__(groups)
        self.plant_type = plant_type
        self.frames = import_folder_dict(f"../graphics/fruit/{plant_type}")
        self.soil = soil

        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        self.image = self.frames[str(self.age)]
        self.y_offset = -16 if plant_type == "corn" else -8
        self.rect = self.image.get_rect(
            midbottom=soil.rect.midbottom
            + pygame.math.Vector2(0, self.y_offset)
        )
        self.z = LAYERS["ground plant"]
        self.check_watered = check_watered

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed

            if int(self.age) > 0:
                self.z = LAYERS["main"]
                self.hitbox = self.rect.copy().inflate(
                    -26, -self.rect.height * 0.4
                )

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[str(round(self.age))]
            self.rect = self.image.get_rect(
                midbottom=self.soil.rect.midbottom
                + pygame.math.Vector2(0, self.y_offset)
            )


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites) -> None:
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        self.collision_sprites = collision_sprites

        self.soil_surfs = import_folder_dict("../graphics/soil")
        self.water_surfs = import_folder("../graphics/soil_water")
        self.tile_type = "o"
        # print(self.soil_surfs)
        self.create_soil_grid()
        self.create_hit_rects()

        self.raining = False

    def create_soil_grid(self):
        groundw, groundh = pygame.image.load(
            "../graphics/world/ground.png"
        ).get_size()
        h_tiles, v_tiles = (
            groundw // TILE_SIZE,
            groundh // TILE_SIZE,
        )
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in (
            load_pygame("../data/map.tmx")
            .get_layer_by_name("Farmable")
            .tiles()
        ):
            self.grid[y][x].append("F")

    def check_watered(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        return "W" in cell

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def plant_seed(self, point, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if not "P" in self.grid[y][x]:
                    self.grid[y][x].append("P")
                    Plant(
                        seed,
                        [
                            self.all_sprites,
                            self.plant_sprites,
                            self.collision_sprites,
                        ],
                        soil_sprite,
                        self.check_watered,
                    )

    def create_hit_rects(self):
        self.hit_rects = []
        for ridx, row in enumerate(self.grid):
            for cidx, cell in enumerate(row):
                if "F" in cell:
                    self.hit_rects.append(
                        pygame.Rect(
                            cidx * TILE_SIZE,
                            ridx * TILE_SIZE,
                            TILE_SIZE,
                            TILE_SIZE,
                        )
                    )

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if "F" in self.grid[y][x]:
                    print("HIT")
                    self.grid[y][x].append("X")
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def water(self, point):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                # print("WA'AH")
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if "X" in self.grid[y][x]:
                    self.grid[y][x].append("W")
                    WaterTile(
                        (soil_sprite.rect.x, soil_sprite.rect.y),
                        choice(self.water_surfs),
                        [self.water_sprites, self.all_sprites],
                    )

    def water_all(self):
        for ridx, row in enumerate(self.grid):
            for cidx, cell in enumerate(row):
                if "X" in cell and not "W" in cell:
                    self.grid[ridx][cidx].append("W")
                    WaterTile(
                        (cidx * TILE_SIZE, ridx * TILE_SIZE),
                        choice(self.water_surfs),
                        [self.water_sprites, self.all_sprites],
                    )

    def remove_water(self):
        for water_sprite in self.water_sprites.sprites():
            x = water_sprite.rect.x // TILE_SIZE
            y = water_sprite.rect.y // TILE_SIZE
            self.grid[y][x].remove("W")
            water_sprite.kill()

    def basic_directions(self, t, r, l, b):
        if all([t, r, l, b]):
            self.tile_type = "x"

        if l and not any([t, r, b]):
            self.tile_type = "r"

        if r and not any([t, l, b]):
            self.tile_type = "l"

        if t and not any([r, l, b]):
            self.tile_type = "b"

        if b and not any([t, r, l]):
            self.tile_type = "t"

    def cross_directions(self, t, r, l, b):
        if r and l and not any([t, b]):
            self.tile_type = "lr"

        if t and b and not any([r, l]):
            self.tile_type = "tb"

        if l and b and not any([t, r]):
            self.tile_type = "tr"

        if r and b and not any([t, l]):
            self.tile_type = "tl"

        if t and l and not any([b, r]):
            self.tile_type = "br"

        if t and r and not any([b, l]):
            self.tile_type = "bl"

    def t_shapes(self, t, r, l, b):
        if all([t, b, r]) and not l:
            self.tile_type = "tbr"

        if all([t, b, l]) and not r:
            self.tile_type = "tbl"

        if all([t, l, r]) and not b:
            self.tile_type = "lrb"

        if all([b, l, r]) and not t:
            self.tile_type = "lrt"

    def autotiling(self, ridx, cidx):
        t, r, l, b = (
            "X" in self.grid[ridx - 1][cidx],
            "X" in self.grid[ridx][cidx + 1],
            "X" in self.grid[ridx][cidx - 1],
            "X" in self.grid[ridx + 1][cidx],
        )
        self.basic_directions(t, r, l, b)
        self.cross_directions(t, r, l, b)
        self.t_shapes(t, r, l, b)

    def create_soil_tiles(
        self,
    ):  # for joining the soil tiles, so it looks better
        self.soil_sprites.empty()
        for ridx, row in enumerate(self.grid):
            for cidx, cell in enumerate(row):
                if "X" in cell:
                    self.autotiling(ridx, cidx)

                    SoilTile(
                        (cidx * TILE_SIZE, ridx * TILE_SIZE),
                        self.soil_surfs[self.tile_type],
                        [self.all_sprites, self.soil_sprites],
                    )
