"""
This module contains the menu state.
"""
from ..prepare import global_package_dir
import sys
sys.path.append(global_package_dir)
import pygame as pg
import pg_state_machine

class Menu(pg_state_machine._State):
    """Core state for the actual gameplay."""
    def __init__(self):
        pg_state_machine._State.__init__(self)

    def get_event(self, event):
        """
        Processes events that were passed from the main event loop.
        Must be overloaded in children.
        """
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.next = "GAME"
                self.done = True

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
        return self.persist

    def update(self, keys, dt):
        """Update function for state.  Must be overloaded in children."""
        pass

    def draw(self, surface, interpolate):
        surface.fill(pg.Color(20,20,20))
        font = pg.font.SysFont(None, 24)
        img1 = font.render('menu', True, pg.Color(200,0,200))
        img2 = font.render('press <space> to toggle game / menu', True, pg.Color(200,0,200))
        img3 = font.render('press <esc> to quit', True, pg.Color(200,0,200))
        surface.blit(img1, (20, 20))
        surface.blit(img2, (20, 40))
        surface.blit(img3, (20, 60))