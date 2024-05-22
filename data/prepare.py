"""
This module initializes the display and creates dictionaries of resources.
Also contained are various constants used throughout the program.
"""
import os
path = os.path.dirname(os.path.abspath(__file__)).rsplit('\\',1)[0]+'\\global_package'
print(path)

global_package_dir = path
import sys
sys.path.append(global_package_dir)

import pygame as pg
# from pygame_lib import tools
from pg_tools import load_all_gfx,load_all_sfx

pg.init()

# paths
this_dir = os.path.abspath(__file__)
main_dir = os.path.split(os.path.split(this_dir)[0])[0] + '\\'
resourses_dir = os.path.join(main_dir, 'resources')

# parameters for game loop
updates_pr_sec = 15
draws_pr_sec = 60
fps_max = 140
updates_pr_sec_design = None

# screen
SCREEN_SIZE = (1200, 700)
ORIGINAL_CAPTION = "Tanks"
BACKGROUND_COLOR = (30, 40, 50)
SCREEN_RECT = pg.Rect((0,0), SCREEN_SIZE)
# _FONT_PATH = os.path.join(resourses_dir, "fonts","Fixedsys500c.ttf")
# BIG_FONT = pg.font.Font(_FONT_PATH, 100)

#Initialization
#_ICON_PATH = os.path.join(resourses_dir, "graphics", "misc", "icon.png")
_Y_OFFSET = (pg.display.Info().current_w-SCREEN_SIZE[0])//2
os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(_Y_OFFSET,50)  # set window y-pos to centre of screen
pg.display.set_caption(ORIGINAL_CAPTION)
# pg.display.set_icon(pg.image.load(_ICON_PATH))
_screen = pg.display.set_mode(SCREEN_SIZE)


#Display until loading finishes.
_screen.fill(BACKGROUND_COLOR)
# _render = BIG_FONT.render("LOADING...", 0, pg.Color("white"))
# _screen.blit(_render, _render.get_rect(center=SCREEN_RECT.center))

_screen.fill(pg.Color(20,20,20))
font = pg.font.SysFont(None, 24)
img = font.render('loading', True, pg.Color(200,200,0))
_screen.blit(img, (20, 20))

pg.display.update()

#General constants

#Draw layer order for all types of items.
# Z_ORDER = {"BG Tiles" : -4,
#            "Water" : -3,
#            "Shadows" : -2,
#            "Solid" : -1,
#            "Solid/Fore" : 750,
#            "Foreground" : 800,
#            "Projectiles" : 850}

#Resource loading (Fonts and music just contain path names).
# SAVE_PATH = os.path.join(resourses_dir, "save_data", "save_data.dat")
# FONTS = load_all_fonts(os.path.join(resourses_dir, "fonts"))
# MUSIC = load_all_music(os.path.join(resourses_dir, "music"))
SFX = load_all_sfx(os.path.join(resourses_dir, 'sounds'))
#print('SFX',SFX)


def graphics_from_directories(directories):
    """
    Calls the load_all_graphics() function for all directories passed.
    """
    base_path = os.path.join(resourses_dir, 'graphics')
    GFX = {}
    for directory in directories:
        path = os.path.join(base_path, directory)
        GFX[directory] = load_all_gfx(path)
    return GFX


_SUB_DIRECTORIES = ['']
GFX = graphics_from_directories(_SUB_DIRECTORIES)
#print('GFX',GFX)