"""
This module contains the primary gameplay state.
"""
from ..prepare import global_package_dir,GFX,SFX
import sys
sys.path.append(global_package_dir)
import pygame as pg
from pg_camera import Camera
import pg_state_machine
from pg_pathfind import Grid, Pathfinding
from pg_tools import get_game_speed_dt_and_loops, scale_image, rotate_image, change_image_color
# from pg_sprite import Sprite
from .. components.player import Player
from .. components.unit import Unit
from ..data import unit_data

class Game(pg_state_machine._State):
    """Core state for the actual gameplay."""
    def __init__(self):
        pg_state_machine._State.__init__(self)
        self.reset_state()

    def reset_state(self):
        self.scale = 2
        self.game_speed_default = 1
        self.game_speed = 1
        self.is_paused = False

        self.tile_size = pg.Vector2(16,16)*self.scale
        self.world_size_tiles = (40,40)
        self.world_size = (self.tile_size[0]*self.world_size_tiles[0] , self.tile_size[1]*self.world_size_tiles[1])
        self.world_surf = pg.Surface(self.world_size, pg.SRCALPHA)

        self.path_grid = Grid(  self.world_size_tiles[0],
                                self.world_size_tiles[1],
                                self.tile_size
                              )
        self.path_find = Pathfinding(self.path_grid)

        display_surf_rect = pg.display.get_surface().get_rect()
        self.camera = Camera(display_area_p=(0,0,display_surf_rect.width,display_surf_rect.height),
                             world_surf_p=self.world_surf,
                             enable_mouse_edge_scroll_p=True,
                             enable_right_mouse_pan_p=False
                            )

        # draw grid
        self.grid_surf = self.world_surf.copy()
        self.grid_surf_rect = self.grid_surf.get_rect()
        for x in range(self.world_size_tiles[0]):
            for y in range(self.world_size_tiles[1]):
                rect = pg.Rect(x*self.tile_size[0], y*self.tile_size[1], self.tile_size[0], self.tile_size[1])
                pg.draw.rect(self.grid_surf, (50,50,50), rect, 1)


        # test
        self.tank_img = GFX['']['tank_base_1_up']
        self.tank_img = scale_image(self.tank_img, self.scale)
        self.tank_img.set_colorkey(pg.Color(255,255,255))
        change_image_color(self.tank_img, pg.Color(255,0,255), pg.Color(0,255,0))
        self.tank_angle = 0

        self.turret_img = GFX['']['turret_1_up']
        self.turret_img = scale_image(self.turret_img, self.scale)
        self.turret_img.set_colorkey(pg.Color(255,255,255))
        change_image_color(self.turret_img, pg.Color(255,0,255), pg.Color(0,255,0))
        self.turret_angle = 0

        self.player_01 = Player('Perik', pg.Color(250,0,0), [])
        self.tank_01 = Unit(    self.scale,
                                self.tile_size[0]*9 + self.tile_size[0]/2,
                                self.tile_size[1]*13 + self.tile_size[1]/2,
                                self.tile_size,
                                unit_data['tank_01'],
                                self.player_01
                            )
        self.tank_01.is_selected = True
        # test

    def get_event(self, event):
        """
        Processes events that were passed from the main event loop.
        Must be overloaded in children.
        """
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.next = "MENU"
                self.done = True

        # test
        self.tank_01.events(event, self.camera.get_mouse_screen_to_world(), self.path_find)
        # test

        self.camera.events(event)

    def startup(self, dt, persistant):
        """
        Add variables passed in persistant to the proper attributes and
        set the start time of the State to the current time.
        """
        self.persist = persistant
        self.dt = dt

    def cleanup(self):
        """
        Add variables that should persist to the self.persist dictionary.
        Then reset State.done to False.
        """
        self.done = False
        self.reset_state()
        return self.persist

    def update(self, keys, dt):
        """Update function for state.  Must be overloaded in children."""
        if not self.is_paused:

            dt_game_speed, loops = get_game_speed_dt_and_loops(dt, self.game_speed, self.game_speed_default)

            for _ in range(loops):

                # test
                self.tank_angle += 0.3
                self.turret_angle += 1
                self.tank_01.update(dt_game_speed)
                # test

    def draw(self, surface, interpolate):

        # update camera at same rate as drawing to prevent stuttering camera at low update rates
        self.camera.update()

        #background
        self.world_surf.fill(pg.Color(0,0,0))

        # draw grid
        self.world_surf.blit(self.grid_surf, self.grid_surf_rect)
        # self.path_grid.draw(self.world_surf)

        # test
        # pos_tank = (200*self.scale , 200*self.scale)
        # offset = (0*self.scale , 0*self.scale)
        # tank_img, tank_rect = rotate_image(self.tank_img, self.tank_angle, pos_tank, offset)
        # self.world_surf.blit(tank_img,tank_rect)

        # pos_turret = (200*self.scale , 200*self.scale)
        # offset = (0*self.scale , 6*self.scale)
        # turret_img, turret_rect = rotate_image(self.turret_img, self.turret_angle, pos_turret, offset)
        # self.world_surf.blit(turret_img,turret_rect)

        #pg.draw.circle(self.world_surf, pg.Color(200,0,0), pos_tank, 2)

        self.tank_01.draw(self.world_surf, interpolate)
        pg.draw.circle(self.world_surf, pg.Color(100,100,200), self.tank_01.pos, 2*self.scale)
        pg.draw.circle(self.world_surf, pg.Color(200,100,200), self.tank_01.attack_target, 2*self.scale)
        # test

        # camera
        self.camera.draw(surface, interpolate)
        