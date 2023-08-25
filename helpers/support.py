from os import walk

import pygame

from .settings import TILE_SIZE


def import_folder(path, return_type="list"):
    """for importing a folder with images and converting them to surfaces (sprites)

    Args:
        path: path to folder with images
        return_type: dict or list, defaults to "list".

    Returns:
        list or dict: list of surfaces or dict with filenames as keys and surfaces as values
    """
    surfaces = [] if return_type == "list" else {}
    for _, _, img_path in walk(path):
        for image in img_path:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surfaces.append(
                image_surf
            ) if return_type == "list" else surfaces.update(
                {image.replace(".png", ""): image_surf}
            )
    return surfaces


def tile_to_grid(pos):
    """convert tile position to grid position

    Args:
        pos: position in pixels

    Returns:
        tuple: position in grid
    """
    return (pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)


def grid_to_tile(pos):
    """convert grid position to tile position

    Args:
        pos: position in grid

    Returns:
        position in pixels
    """
    return (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE)
