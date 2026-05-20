import pygame as pg
import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_custom_font(size):
    font_path = resource_path('resources/fonts/kenvector_future.ttf')
    return pg.font.Font(font_path, size)
