import pygame

from helpers.settings import *
from helpers.timer import Timer


class Menu:
    """class for the merchant menu"""

    def __init__(self, player, toggle_menu) -> None:
        self.player = player
        self.toggle_menu = toggle_menu

        # display properties
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("../font/LycheeSoda.ttf", 32)
        self.width = 400
        self.space = 10
        self.padding = 8
        self.sell_text = self.font.render("sell", False, (0, 0, 0))
        self.buy_text = self.font.render("buy", False, (0, 0, 0))

        # menu options
        self.options = list(self.player.item_inventory.keys()) + list(
            self.player.seed_inventory.keys()
        )
        self.index = 0
        self.sell_border = len(self.player.item_inventory) - 1

        # timer
        self.timer = Timer(200)

        # displaying the menu
        self.setup()

    def menu_rectangle(self):
        """draw the menu rectangle"""
        self.total_height += self.space * (len(self.options) - 1)
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(
            SCREEN_WIDTH / 2 - self.width / 2,
            self.menu_top,
            self.width,
            self.total_height,
        )

    def menu_text(self):
        """draw the text for menu entries"""
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text = self.font.render(item, False, (0, 0, 0))
            self.text_surfs.append(text)
            self.total_height += text.get_height() + self.padding * 2

    def setup(self):
        """setup the menu for trading"""
        self.menu_text()
        self.menu_rectangle()

    def display_money(self):
        """display the money"""
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

    def buy_or_sell(self, keys):
        """buy or sell the item you have selected

        Args:
            keys: the keys that are pressed
        """
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

    def menu_movement(self, keys):
        """navigate the menu

        Args:
            keys: the keys that are pressed
        """
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

    def input(self):
        """handle the input for the menu"""
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            self.menu_movement(keys)
            if keys[pygame.K_SPACE]:
                self.buy_or_sell()

    def highlight_entry(self, bg_rect):
        """highlight item when selected

        Args:
            bg_rect: background rectangle
        """
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

    def display_item(self, surf, top):
        """display an item in the menu

        Args:
            surf: the surface to display
            top: the top position of the item rectangle"""
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
        return bg_rect

    def show_amount(self, amount, bg_rect):
        """display the amount of an

        Args:
            amount: the amount of the item
            bg_rect: the background rectangle of the item
        """
        amount_surf = self.font.render(f"x{amount}", False, (0, 0, 0))
        amount_rect = amount_surf.get_rect(
            midright=(self.main_rect.right - 20, bg_rect.centery)
        )
        self.display_surface.blit(amount_surf, amount_rect)

    def show_entry(self, surf, amount, top, selected):
        """display the menu entry, including the amount of the item, its name and the option to buy or sell it

        Args:
            surf: the surface to display
            amount: the amount of the item
            top: the top position of the item rectangle
            selected: whether the item is selected or not
        """
        bg_rect = self.show_item(surf, top)
        self.show_amount(amount, bg_rect)

        if selected:
            self.highlight_entry(bg_rect)

    def display_menu_entries(self):
        """display all the menu entries"""
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

    def update(self):
        """update the menu"""
        self.input()
        self.display_money()
        self.display_menu_items()
