import os
import sys

def get_app_folder():
    """Определяет папку, где находится программа"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_brightness(hex_color):
    """Определяет яркость цвета"""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return (r * 0.299 + g * 0.587 + b * 0.114)

def adjust_color_alpha(color, alpha):
    """Изменяет прозрачность цвета"""
    if color.startswith('#'):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        r = int(r * alpha)
        g = int(g * alpha)
        b = int(b * alpha)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    return color