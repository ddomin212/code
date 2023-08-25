import pygame

from helpers.settings import *


class Overlay:
    def __init__(self, player) -> None:
        self.display_surface = pygame.display.get_surface()
        self.player = player

        overlay_path = "../graphics/overlay/"
        self.tools_surface = {
            tool: pygame.image.load(
                f"{overlay_path}{tool}.png"
            ).convert_alpha()
            for tool in player.tools
        }
        self.seeds_surface = {
            seed: pygame.image.load(
                f"{overlay_path}{seed}.png"
            ).convert_alpha()
            for seed in player.seeds
        }

    def display_box(self, flag):
        """display the selected item for seeds or tools"""
        surf = eval(f"self.{flag}s_surface[self.player.selected_{flag}]")
        rect = surf.get_rect(midbottom=OVERLAY_POSITIONS[flag])
        self.display_surface.blit(surf, rect)

    def display(self):
        """display the overlay"""
        self.display_box("tool")
        self.display_box("seed")
