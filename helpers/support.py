from os import listdir, walk

import pygame


def import_folder(path):
    surface_list = []
    for _, _, img_path in walk(path):
        for image in img_path:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list


def import_folder_dict(path):
    surface_dict = {}
    for _, _, img_path in walk(path):
        for image in img_path:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.replace(".png", "")] = image_surf
    return surface_dict
