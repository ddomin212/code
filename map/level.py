from random import randint

import pygame
from pytmx.util_pygame import load_pygame

from helpers.settings import *
from helpers.support import *
from helpers.support import grid_to_tile, tile_to_grid
from map.sky import Rain, Sky
from map.soil import SoilLayer
from map.transition import Transition
from objects.player import Player
from objects.sprites import (
    Generic,
    Interaction,
    Particle,
    Tree,
    Water,
    WildFlower,
)
from ui.menu import Menu
from ui.overlay import Overlay


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.sky = Sky()
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 3
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.soil_layer.raining = self.raining

        self.setup()

        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)

    def setup_objects(self, tmx_data, type, groups, layer):
        """setup objects in game world

        Args:
            tmx_data: tile map data
            layers: layers to setup
            groups: sprite groups to add objects to
            rank: which layer is the object on, defaults to "main", this is important for drawing order
            frames: frames for animated objects, defaults to None
        """

        for obj in tmx_data.get_layer_by_name(layer):
            eval(
                f"""{type}(
                    pos=(obj.x, obj.y),
                    surf=obj.image,
                    groups={groups},
                    {"name=obj.name, player_add=self.player_add" if type == "Tree" else ""}
                )"""
            )

    def setup_layer(self, tmx_data, layers, groups, rank="main", frames=None):
        """setup layers in game world

        Args:
            tmx_data: tile map data
            layers: layers to setup
            groups: sprite groups to add objects to
            rank: which layer is the object on, defaults to "main", this is important for drawing order
            frames: frames for animated objects, defaults to None
        """
        for layer in layers:
            for x, y, tile in tmx_data.get_layer_by_name(layer).tiles():
                if layers[0] == "Water":
                    Water(
                        pos=(x * tmx_data.tilewidth, y * tmx_data.tileheight),
                        frames=frames,
                        groups=groups,
                    )
                else:
                    Generic(
                        pos=(x * tmx_data.tilewidth, y * tmx_data.tileheight),
                        surf=tile,
                        groups=groups,
                        z=LAYERS[rank],
                    )

    def player_add(self, item):
        """add item to player inventory

        Args:
            item: item to add
        """
        self.player.item_inventory[item] += 1

    def setup_architecture(self, tmx_data):
        """setup architecture (houses and fences) in game world

        Args:
            tmx_data: tile map data
        """
        self.setup_layer(
            tmx_data,
            ["HouseWalls", "HouseFurnitureTop"],
            self.all_sprites,
        )
        self.setup_layer(
            tmx_data,
            ["HouseFloor", "HouseFurnitureBottom"],
            self.all_sprites,
            rank="house bottom",
        )
        self.setup_layer(
            tmx_data,
            ["Fence"],
            [self.all_sprites, self.collision_sprites],
        )

    def setup_nature(self, tmx_data):
        """setup nature (trees, flowers, water) in game world

        Args:
            tmx_data: tile map data
        """
        self.setup_layer(
            tmx_data,
            ["Water"],
            self.all_sprites,
            frames=import_folder("../graphics/water"),
        )

        self.setup_objects(
            tmx_data,
            "WildFlower",
            "[self.all_sprites, self.collision_sprites]",
            "Decoration",
        )
        self.setup_objects(
            tmx_data,
            "Tree",
            "[self.all_sprites, self.collision_sprites, self.tree_sprites]",
            "Trees",
        )

    def setup_layers(self, tmx_data):
        """setup layers in game world

        Args:
            tmx_data: tile map data
        """
        self.setup_architecture(tmx_data)

        self.setup_layer(tmx_data, ["Collision"], self.collision_sprites)

        self.setup_nature(tmx_data)

    def harvest_plant(self, plant):
        """harvest plant

        Args:
            plant: the plant to harvest
        """
        self.player_add(plant.plant_type)
        plant.kill()
        Particle(
            pos=plant.rect.topleft,
            surf=pygame.image.load(
                f"../graphics/fruit/{plant.plant_type}/{plant.max_age}.png"
            ).convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS["main"],
            duration=500,
        )
        col, row = tile_to_grid(plant.rect.center)
        self.soil_layer.grid[row][col].remove("P")

    def plant_collision(self):
        """determine if the player collides with a plant, if harvestable, harvest it"""
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(
                    self.player.hitbox
                ):
                    self.harvest_plant(plant)

    def setup_interactives(self, obj):
        """setup interactive objects in game world

        Args:
            obj: object to setup
        """
        if obj.name == "Start":
            self.player = Player(
                (obj.x, obj.y),
                self.all_sprites,
                self.collision_sprites,
                self.tree_sprites,
                self.interaction_sprites,
                self.soil_layer,
                self.toggle_shop,
            )
        if obj.name == "Bed":
            Interaction(
                (obj.x, obj.y),
                (obj.width, obj.height),
                self.interaction_sprites,
                obj.name,
            )
        if obj.name == "Trader":
            Interaction(
                (obj.x, obj.y),
                (obj.width, obj.height),
                self.interaction_sprites,
                obj.name,
            )

    def setup(self):
        """setup the level"""
        tmx_data = load_pygame("../data/map.tmx")

        self.setup_layers(tmx_data)

        Generic(
            pos=(0, 0),
            surf=pygame.image.load(
                "../graphics/world/ground.png"
            ).convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS["ground"],
        )
        for obj in tmx_data.get_layer_by_name("Player"):
            self.setup_interactives(obj)

    def toggle_shop(self):
        """toggle the shop"""
        self.shop_active = not self.shop_active

    def reset_fruits(self):
        """reset fruits on trees"""
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

    def reset_map(self):
        """reset the map, this is called when the player goes to sleep"""
        self.soil_layer.update_plants()

        self.soil_layer.remove_water()
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining

        if self.raining:
            self.soil_layer.water_all()

        self.sky.start_color = [255, 255, 255]

    def reset(self):
        """reset the level"""
        self.reset_map()

        self.reset_fruits()

    def run(self, dt):
        """run the level

        Args:
            dt: delta time
        """
        self.all_sprites.custom_draw(self.player)

        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()

        self.overlay.display()

        if self.raining and not self.shop_active:
            self.rain.update(dt)

        self.sky.display(dt)

        if self.player.sleep:
            self.transition.play(dt)


class CameraGroup(pygame.sprite.Group):
    """Group that draws all its sprites with a custom draw function"""

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2(0, 0)

    def custom_draw(self, player):
        """draw all sprites in the group, offset by the player position,
           so that the player is always in the center of the screen

        Args:
            player: player object
        """
        self.offset = pygame.math.Vector2(
            player.rect.center
        ) - pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        for sprite in sorted(
            sorted(
                self.sprites(),
                key=lambda s: s.rect.centery,  # aby hrac mohl bejt za a pred objekty
            ),
            key=lambda x: x.z,  # aby se hrac vykresloval na spravne vrstve
        ):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)
