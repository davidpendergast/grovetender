

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


class GlobalState:

    def __init__(self):
        self.tick_count = 0
        self.px_scale = 0
        self.px_scale_options = [0, 1, 2, 3]

    def is_dev(self):
        return True

    def update_all(self):
        pass
