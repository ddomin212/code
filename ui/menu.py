import pygame

from helpers.settings import *
from helpers.timer import Timer


class Menu:
    def __init__(self, player, toggle_menu) -> None:
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("../font/LycheeSoda.ttf", 32)
        self.width = 400
        self.space = 10
        self.padding = 8
        self.options = list(self.player.item_inventory.keys()) + list(
            self.player.seed_inventory.keys()
        )
        self.index = 0
        self.sell_border = len(self.player.item_inventory) - 1
        self.timer = Timer(200)
        self.setup()

    def setup(self):
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text = self.font.render(item, False, (0, 0, 0))
            self.text_surfs.append(text)
            self.total_height += text.get_height() + self.padding * 2
        self.total_height += self.space * (len(self.options) - 1)
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(
            SCREEN_WIDTH / 2 - self.width / 2,
            self.menu_top,
            self.width,
            self.total_height,
        )
        self.sell_text = self.font.render("sell", False, (0, 0, 0))
        self.buy_text = self.font.render("buy", False, (0, 0, 0))

    def display_money(self):
        text_surf = self.font.render(f"${self.player.money}", False, (0, 0, 0))
        text_rect = text_surf.get_rect(
            midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20)
        )

        pygame.draw.rect(
            self.display_surface,
            (255, 255, 255),
            text_rect.inflate(10, 10),
            0,
            6,
        )
        self.display_surface.blit(text_surf, text_rect)

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.timer.activate()
                self.index -= 1
                if self.index < 0:
                    self.index = len(self.options) - 1

            if keys[pygame.K_DOWN]:
                self.timer.activate()
                self.index += 1
                if self.index > len(self.options) - 1:
                    self.index = 0

            if keys[pygame.K_SPACE]:
                self.timer.activate()

                current_item = self.options[self.index]
                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                else:
                    if self.player.money >= PURCHASE_PRICES[current_item]:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= PURCHASE_PRICES[current_item]

    def show_entry(self, surf, amount, top, selected):
        bg_rect = pygame.Rect(
            self.main_rect.left,
            top,
            self.width,
            surf.get_height() + self.padding * 2,
        )
        pygame.draw.rect(self.display_surface, (255, 255, 255), bg_rect, 0, 6)

        text_rect = surf.get_rect(
            midleft=(self.main_rect.left + 20, bg_rect.centery)
        )
        self.display_surface.blit(surf, text_rect)

        amount_surf = self.font.render(f"x{amount}", False, (0, 0, 0))
        amount_rect = amount_surf.get_rect(
            midright=(self.main_rect.right - 20, bg_rect.centery)
        )
        self.display_surface.blit(amount_surf, amount_rect)

        if selected:
            pygame.draw.rect(
                self.display_surface,
                (0, 0, 0),
                bg_rect,
                4,
                6,
            )
            pos_rect = self.sell_text.get_rect(
                midleft=(self.main_rect.left + 150, bg_rect.centery)
            )
            if self.index > self.sell_border:
                self.display_surface.blit(self.buy_text, pos_rect)
            else:
                self.display_surface.blit(self.sell_text, pos_rect)

    def update(self):
        self.input()
        self.display_money()
        for idx, text_surf in enumerate(self.text_surfs):
            top = self.menu_top + idx * (
                text_surf.get_height() + self.padding * 2 + self.space
            )
            amount_list = list(self.player.item_inventory.values()) + list(
                self.player.seed_inventory.values()
            )

            self.show_entry(
                text_surf, amount_list[idx], top, idx == self.index
            )
