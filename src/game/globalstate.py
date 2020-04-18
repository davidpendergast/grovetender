

_INSTANCE = None


def create_instance():
    global _INSTANCE
    if _INSTANCE is not None:
        raise ValueError("global state already created")
    else:
        _INSTANCE = GlobalState()
        return _INSTANCE


def get_instance():
    return _INSTANCE

MAIN_MENU_MODE = 0
IN_GAME_MODE = 1
PAUSED_MODE = 2

class GlobalState:

    def __init__(self):
        self.tick_count = 0
        self.px_scale = 0
        self.px_scale_options = [0, 1, 2, 3]

        self.active_game_mode = IN_GAME_MODE
        self.next_game_mode = None
        self.game_state = None

    def is_dev(self):
        return True

    def set_game_state(self, game_state):
        self.game_state = game_state

    def set_next_game_mode(self, mode):
        self.next_game_mode = mode

    def update_all(self):
        if self.active_game_mode == IN_GAME_MODE:
            if self.game_state is not None:
                self.game_state.update()
        elif self.active_game_mode == MAIN_MENU_MODE:
            pass
        elif self.active_game_mode == PAUSED_MODE:
            pass

        if self.next_game_mode is not None and self.next_game_mode != self.active_game_mode:
            self.active_game_mode = self.next_game_mode
        self.next_game_mode = None