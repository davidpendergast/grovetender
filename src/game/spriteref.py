import src.engine.spritesheets as spritesheets
import src.utils.util as util
import src.engine.sprites as sprites


LAYER_SCENE_BG = "scene_bg"
LAYER_SCENE_ENVIRONMENT = "scene_env"
LAYER_SCENE_FG = "scene_fg"

LAYER_UI_BG = "ui_bg"
LAYER_UI_FG = "ui_fg"
LAYER_UI_TOOLTIP = "ui_tooltip"


class MainSheet(spritesheets.SpriteSheet):

    def __init__(self):
        spritesheets.SpriteSheet.__init__(self, "main_sheet", util.Utils.resource_path("assets/spritesheet.png"))

        # TODO - add sprite definitions

    def draw_to_atlas(self, atlas, sheet, start_pos=(0, 0)):
        super().draw_to_atlas(atlas, sheet, start_pos=start_pos)
