

class WorldState:
    """Keeps track of everything in the world"""

    def __init__(self):
        self. tile_grid = {}  # (x, y) -> TileInfo


class TileInfo:

    def __init__(self, x, y, valid=True):
        self.tower = None
        self._is_valid = valid

    def is_valid(self):
        return self._is_valid


class WorldRenderer:

    def __init__(self):
        self.rock_sprite = None
        self.rock_pos = (0, 96 * 2)

        self.grid_pos = (0, 96 * 2)
        self.grid_tiles = []

    def render_world(self, worldstate):
        pass
