from .prepare import global_package_dir,ORIGINAL_CAPTION,updates_pr_sec,draws_pr_sec,fps_max,updates_pr_sec_design
import sys
sys.path.append(global_package_dir)
import pg_game_loop, pg_game_loop_timer
from .states import menu, game

def start():
    '''Add states to game_loop here.'''
    glt = pg_game_loop_timer.Game_Loop_Timer( updates_pr_sec,
                                              draws_pr_sec,
                                              fps_max,
                                              updates_pr_sec_design)
    app = pg_game_loop.Game_Loop( ORIGINAL_CAPTION,
                                  glt)
    state_dict = {
                  'MENU'    :   menu.Menu(),
                  'GAME'    :   game.Game(),
                  }
    app.state_machine.setup_states(state_dict, 'MENU')
    app.main()