import os
import math
import pygame as pg

def dir_files_to_dict(directory, accept_extensions=()):
    """
    Create a dictionary of paths to files in given directory
    if their extensions are in accept_extensions.
    """
    file_dict = {}
    for file in os.listdir(directory):
        name,ext = os.path.splitext(file)
        if ext.lower() in accept_extensions:
            file_dict[name] = os.path.join(directory,file)
    return file_dict

def change_image_color(surface, old_color, new_color):
    pa = pg.PixelArray(surface)
    pa.replace(old_color, new_color, distance=0.01)
    pa.close()

def scale_image(img: pg.Surface, factor):
    w, h = img.get_width() * factor, img.get_height() * factor
    return pg.transform.scale(img.copy(), (int(w), int(h)))

def rotate_image(surface, angle, pos_center, offset_center=(0,0)): 
    # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame

    # surface       = pygame surface
    # angle         = angle in degrees to rotate counter clockwise
    # pos_center    = tuple, absolute center position of image
    # offset_center = tuple, offset from center position of image to center of rotation

    image_rect_center = ( pos_center[0]-offset_center[0] , pos_center[1]-offset_center[1] )
    image_rect = surface.get_rect(center = image_rect_center)
    offset_center_to_center_of_rotation = pg.math.Vector2(pos_center) - image_rect.center
    rotated_offset = offset_center_to_center_of_rotation.rotate(-angle)
    rotated_image_center = ( pos_center[0]-rotated_offset.x , pos_center[1]-rotated_offset.y )
    rotated_image = pg.transform.rotate(surface, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    return rotated_image, rotated_image_rect

def strip_from_sheet(sheet, start, size, nr_of_frames, sheet_width_in_frames, colorkey=None):
    """
    Strips individual frames from a sprite sheet given a start location.
    Assumes that sprites progress from left to right and from top to
    bottom on the sprite sheet.
    """
    frames = []
    x_pos,y_pos = start[0],start[1]
    for _ in range(nr_of_frames):
        frames.append(sheet.subsurface(pg.Rect((x_pos,y_pos),size)))
        x_pos += size[0]
        if x_pos/size[0] >= sheet_width_in_frames:
            x_pos = 0
            y_pos += size[1]
    if colorkey != None:
        for frame in frames:
            frame.set_colorkey(colorkey)
    return frames

def get_game_speed_dt_and_loops(dt, game_speed, game_speed_default):
    loops = 1
    if game_speed < 0:
        dt_game_speed = 0
    elif game_speed < 1:
        dt_game_speed = dt * game_speed
    elif game_speed > 1:
        loops = math.ceil(game_speed / game_speed_default)
        dt_game_speed = dt * game_speed / loops
    else:
        dt_game_speed = dt
    return dt_game_speed, loops

### Resource loading functions.
def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png','.jpg','.bmp')):
    """
    Load all graphics with extensions in the accept argument.  If alpha
    transparency is found in the image the image will be converted using
    convert_alpha().  If no alpha transparency is detected image will be
    converted using convert() and colorkey will be set to colorkey.
    """
    graphics = {}
    for pic in os.listdir(directory):
        name,ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory,pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                if colorkey != None:
                    img.set_colorkey(colorkey)
            graphics[name]=img
    return graphics

def load_all_sfx(directory, accept=(".wav",".mp3",".ogg",".mdi")):
    """
    Load all sfx of extensions found in accept.  Unfortunately it is
    common to need to set sfx volume on a one-by-one basis.  This must be done
    manually if necessary.
    """
    effects = {}
    for fx in os.listdir(directory):
        name,ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory,fx))
    return effects

def load_all_music(directory, accept_extensions=(".wav",".mp3",".ogg",".mdi")):
    """
    Create a dictionary of paths to music files in given directory
    if their extensions are in accept_extensions.
    """
    return dir_files_to_dict(directory, accept_extensions)

def load_all_fonts(directory, accept_extensions=(".ttf",)):
    """
    Create a dictionary of paths to font files in given directory
    if their extensions are in accept_extensions.
    """
    return dir_files_to_dict(directory,accept_extensions)