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

        self.ui_panel_bg = None

        self.ui_blight_bar_bg = None
        self.ui_blight_bar = None

        self.giant_rock = None

        self.fruit_icons = []
        self.veg_icons = []
        self.mushroom_icons = []
        self.flower_icons = []

        self.shovel_icon = None
        self.growing_rock_icon = None
        self.tombstone_icon = None
        self.storage_bin_icon = None

        self.icon_outline = None
        self.no_icon = None
        self.yes_icon = None
        self.question_icon = None

        self.next_day_button = None
        self.next_day_outline = None

        self.tile_empty = None
        self.tile_dirt = None
        self.blight_icon = None

        self.vp_symbol = None
        self.money_symbol = None

        self.fruit_symbol = None
        self.veg_symbol = None
        self.mushroom_symbol = None
        self.flower_symbol = None
        self.blight_symbol = None

        self.contract_panels = []
        self.contract_panel_fruit = None
        self.contract_panel_veg = None
        self.contract_panel_mushroom = None
        self.contract_panel_flower = None

        self.contract_panel_bar = None
        self.contract_panel_bar_endcap = None

        self.box_borders = []

    def draw_to_atlas(self, atlas, sheet, start_pos=(0, 0)):
        super().draw_to_atlas(atlas, sheet, start_pos=start_pos)

        self.ui_panel_bg = sprites.ImageModel(0, 0, 112, 300, offset=start_pos)

        self.ui_blight_bar_bg = sprites.ImageModel(128, 224, 288, 16, offset=start_pos)
        self.ui_blight_bar = sprites.ImageModel(176, 240, 16, 16, offset=start_pos)

        self.giant_rock = sprites.ImageModel(0, 320, 320, 208, offset=start_pos)

        self.fruit_icons = [sprites.ImageModel(128 + i * 16, 0, 16, 16, offset=start_pos) for i in range(0, 3)]
        self.veg_icons = [sprites.ImageModel(128 + i * 16, 16, 16, 16, offset=start_pos) for i in range(0, 3)]
        self.mushroom_icons = [sprites.ImageModel(128 + i * 16, 32, 16, 16, offset=start_pos) for i in range(0, 3)]
        self.flower_icons = [sprites.ImageModel(128 + i * 16, 48, 16, 16, offset=start_pos) for i in range(0, 3)]

        self.shovel_icon = sprites.ImageModel(176, 0, 16, 16, offset=start_pos)
        self.growing_rock_icon = sprites.ImageModel(176, 16, 16, 16, offset=start_pos)
        self.tombstone_icon = sprites.ImageModel(176, 32, 16, 16, offset=start_pos)
        self.storage_bin_icon = sprites.ImageModel(176, 48, 16, 16, offset=start_pos)

        self.icon_outline = sprites.ImageModel(208, 16, 16, 16, offset=start_pos)
        self.no_icon = sprites.ImageModel(208, 32, 16, 16, offset=start_pos)
        self.yes_icon = sprites.ImageModel(224, 32, 16, 16, offset=start_pos)
        self.question_icon = sprites.ImageModel(208, 48, 16, 16, offset=start_pos)

        self.next_day_button = sprites.ImageModel(128, 80, 68, 16, offset=start_pos)
        self.next_day_outline = sprites.ImageModel(128, 96, 68, 16, offset=start_pos)

        self.tile_empty = sprites.ImageModel(208, 80, 16, 16, offset=start_pos)
        self.tile_dirt = sprites.ImageModel(224, 80, 16, 16, offset=start_pos)
        self.blight_icon = sprites.ImageModel(240, 80, 16, 16, offset=start_pos)

        self.vp_symbol = sprites.ImageModel(272, 80, 17, 9, offset=start_pos)
        self.money_symbol = sprites.ImageModel(272, 96, 12, 13, offset=start_pos)

        self.fruit_symbol = sprites.ImageModel(304, 80, 8, 8, offset=start_pos)
        self.veg_symbol = sprites.ImageModel(312, 80, 8, 8, offset=start_pos)
        self.mushroom_symbol = sprites.ImageModel(320, 80, 8, 8, offset=start_pos)
        self.flower_symbol = sprites.ImageModel(328, 80, 8, 8, offset=start_pos)
        self.blight_symbol = sprites.ImageModel(336, 80, 12, 11, offset=start_pos)

        self.contract_panels = [sprites.ImageModel(128 + i * 80, 128, 80, 69, offset=start_pos) for i in range(0, 4)]
        self.contract_panel_fruit = self.contract_panels[0]
        self.contract_panel_veg = self.contract_panels[1]
        self.contract_panel_mushroom = self.contract_panels[2]
        self.contract_panel_flower = self.contract_panels[3]

        self.contract_panel_bar = sprites.ImageModel(128, 208, 16, 2, offset=start_pos)
        self.contract_panel_bar_endcap = sprites.ImageModel(144, 208, 1, 2, offset=start_pos)  # not used

        self.box_borders = [sprites.ImageModel(120 + (i % 3) * 8, 248 + (i // 3) * 8, 8, 8, offset=start_pos) for i in range(0, 9)]


MAIN_SHEET = MainSheet()
