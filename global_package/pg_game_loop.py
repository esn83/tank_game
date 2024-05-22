import pygame as pg
import pg_state_machine

class Game_Loop(object):
    """
    Control class for entire project. Contains the game loop, and contains
    the event_loop which passes events to States as needed.
    """
    def __init__(self, caption, game_loop_timer):
        self.screen = pg.display.get_surface()
        self.caption = caption
        self.done = False
        self.fps_visible = True
        # self.now = 0
        # self.dt = 0
        self.keys = pg.key.get_pressed()
        self.state_machine = pg_state_machine.StateMachine()
        self.game_loop_timer = game_loop_timer
        self.dt = self.game_loop_timer.get_dt_ms()  # dt is fixed as game loop runs with fixed time step
        self.first_loop = True

    def event_loop(self):
        """
        Process all events and pass them down to the state_machine.
        The f5 key globally turns on/off the display of FPS in the caption
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.done = True
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            self.state_machine.get_event(event)

    def update(self):
        """
        Updates the currently active state.
        """

        self.game_loop_timer.update()

        if self.game_loop_timer.is_draw_ready(): # things that needs to be updated at same rate as drawing fx. camera
            pass

        while self.game_loop_timer.is_update_ready() or self.first_loop == True:
            if self.first_loop:
                self.first_loop = False
            self.game_loop_timer.subtract_accumulator_update()
            # self.dt = pg.time.get_ticks() - self.now
            # self.now = pg.time.get_ticks() # get ms elapsed since pg.init() was called
            self.state_machine.update(self.keys, self.dt)

    def draw(self, interpolate):
        if not self.state_machine.state.done:            
            if self.game_loop_timer.is_draw_ready():
                self.game_loop_timer.subtract_accumulator_draw()
                self.state_machine.draw(self.screen, interpolate)
                self.show_fps() # FPS
                pg.display.update()

    def toggle_show_fps(self, key):
        """Press f5 to turn on/off displaying the framerate in the caption."""
        if key == pg.K_F5:
            self.fps_visible = not self.fps_visible
            if not self.fps_visible:
                pg.display.set_caption(self.caption)

    def show_fps(self):
        """
        Display the current FPS in the window handle if fps_visible is True.
        """
        if self.fps_visible:
            fps, fps_upd, fps_draw = self.game_loop_timer.get_fps()
            with_fps = self.caption + ' | fps : ' + str(fps) + ' | fps update : ' + str(fps_upd) + ' | fps draw : ' + str(fps_draw)
            pg.display.set_caption(with_fps)

    def main(self):
        """Main loop for entire program. Uses a constant timestep."""
        while not self.done:
            self.event_loop()
            self.update()
            interpolate = self.game_loop_timer.get_alpha()
            self.draw(interpolate)