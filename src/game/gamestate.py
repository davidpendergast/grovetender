import src.engine.renderengine as renderengine
import src.engine.sprites as sprites
import src.utils.util as util

import src.game.worldstate as worldstate
import src.game.spriteref as spriteref
import src.game.globalstate as gs
import src.game.colors as colors
import src.game.towers as towers


class ResourceType:
    FRUIT = "FRUIT"
    VEG = "VEG"
    MUSHROOM = "MUSHROOM"
    FLOWER = "FLOWER"
    BLIGHT = "BLIGHT"
    MONEY = "MONEY"
    VP = "VP"


class GameState:

    def __init__(self):
        self.renderer = Renderer()

        self.basic_towers_in_shop = towers.all_basic_towers()
        self.utility_towers_in_shop = towers.all_utility_towers()

        self.trying_to_buy = None  # spec that the user has clicked

        self.max_blight = 100  # you lose when you hit this

        self.resources = {
            ResourceType.FRUIT: 0,
            ResourceType.VEG: 0,
            ResourceType.MUSHROOM: 0,
            ResourceType.FLOWER: 0,
            ResourceType.BLIGHT: 0,
            ResourceType.MONEY: 30,
            ResourceType.VP: 0
        }

    def get_resources(self, res_type):
        return self.resources[res_type]

    def is_trying_to_buy(self):
        return self.trying_to_buy is not None

    def get_blight_pcnt(self):
        return util.Utils.bound(self.get_resources(ResourceType.BLIGHT) / self.max_blight, 0, 1)

    def update(self):
        self.renderer.update(self)


class Renderer:

    def __init__(self):
        self.ui_main_panel = MainPanelElement((0, 0))
        self.ui_blight_bar = BlightBarElement((0, 0))

    def all_sprites(self):
        for spr in self.ui_main_panel.all_sprites():
            yield spr
        for spr in self.ui_blight_bar.all_sprites():
            yield spr

    def update(self, game_state):
        self._update_ui(game_state)

        for sprite in self.all_sprites():
            renderengine.get_instance().update(sprite)

    def _update_ui(self, game_state):
        self.ui_main_panel.update(game_state)
        self.ui_blight_bar.update(game_state)


class UiElement:

    def __init__(self, xy, parent=None):
        self.parent = parent
        self.xy = xy

        self._hover_tick = -5

    def get_size(self):
        return (0, 0)

    def set_xy(self, xy, local=True):
        if local or self.parent is None:
            self.xy = xy
        else:
            abs_xy = self.get_xy(local=False)
            rel_xy = self.get_xy(local=True)
            self.set_xy((
                rel_xy[0] + (xy[0] - abs_xy[0]),
                rel_xy[1] + (xy[1] - abs_xy[1])
            ), local=True)

    def all_children(self):
        return []

    def get_xy(self, local=False):
        if local or self.parent is None:
            return self.xy
        else:
            px, py = self.parent.get_xy()
            return px + self.xy[0], py + self.xy[1]

    def get_rect(self, local=False):
        xy = self.get_xy(local=local)
        size = self.get_size()
        return [xy[0], xy[1], size[0], size[1]]

    def all_sprites(self):
        yield

    def update(self, game_state):
        pass

    def can_be_hovered(self):
        return False

    def get_element_for_hover(self, pos):
        for child in self.all_children():
            if child.can_be_hovered() and util.Utils.rect_contains(child.get_rect(local=False), pos):
                return child
        if self.can_be_hovered() and util.Utils.rect_contains(self.get_rect(local=False), pos):
            return self
        else:
            return None

    def do_hover(self):
        self._hover_tick = gs.get_instance().tick_count

    def is_hovered(self):
        return gs.get_instance().tick_count - self._hover_tick <= 1

    def get_hover_text(self):
        return None

    def can_be_clicked(self):
        return False

    def get_element_for_click(self, pos):
        for child in self.all_children():
            if child.can_be_clicked() and util.Utils.rect_contains(child.get_rect(local=False), pos):
                return child
        if self.can_be_clicked() and util.Utils.rect_contains(self.get_rect(local=False), pos):
            return self
        else:
            return None

    def do_click(self):
        pass


class MainPanelElement(UiElement):

    def __init__(self, xy, parent=None):
        UiElement.__init__(self, xy, parent=parent)
        self.panel_sprite = None

        self.basic_tower_buttons = []
        self.utility_tower_buttons = []

    def can_be_clicked(self):
        return True

    def can_be_hovered(self):
        return True

    def all_sprites(self):
        if self.panel_sprite is not None:
            yield self.panel_sprite
        for butt in self.basic_tower_buttons:
            if butt is not None:
                for spr in butt.all_sprites():
                    yield spr
        for butt in self.utility_tower_buttons:
            if butt is not None:
                for spr in butt.all_sprites():
                    yield spr

    def all_children(self):
        for butt in self.basic_tower_buttons:
            if butt is not None:
                yield butt

        for butt in self.utility_tower_buttons:
            if butt is not None:
                yield butt

    def update(self, game_state):
        game_size = renderengine.get_instance().get_game_size()

        ui_panel_model = spriteref.MAIN_SHEET.ui_panel_bg
        self.set_xy((game_size[0] - ui_panel_model.width() * 2, 0), local=False)

        if self.panel_sprite is None:
            self.panel_sprite = sprites.ImageSprite.new_sprite(spriteref.LAYER_UI_BG, scale=2)

        self.panel_sprite = self.panel_sprite.update(new_model=ui_panel_model,
                                                     new_x=self.get_xy(local=False)[0],
                                                     new_y=self.get_xy(local=False)[1], new_scale=2)

        xy_start = (18, 18)  # sheet dims
        button_spacing = (18, 18)

        for i in range(0, len(game_state.basic_towers_in_shop)):
            tower_spec = game_state.basic_towers_in_shop[i]
            if len(self.basic_tower_buttons) <= i:
                self.basic_tower_buttons.append(None)

            if self.basic_tower_buttons[i] is None:
                self.basic_tower_buttons[i] = TowerBuyButton(tower_spec, xy_start, spriteref.LAYER_UI_FG, parent=self)

            self.basic_tower_buttons[i].tower_spec = tower_spec
            x = xy_start[0] + (i % 3) * button_spacing[0]
            y = xy_start[1] + (i // 3) * button_spacing[1]
            self.basic_tower_buttons[i].set_xy((x * 2, y * 2), local=True)

        xy_start = (78, 18)  # sheet dims

        for i in range(0, len(game_state.utility_towers_in_shop)):
            tower_spec = game_state.utility_towers_in_shop[i]
            if len(self.utility_tower_buttons) <= i:
                self.utility_tower_buttons.append(None)

            if self.utility_tower_buttons[i] is None:
                self.utility_tower_buttons[i] = TowerBuyButton(tower_spec, xy_start, spriteref.LAYER_UI_FG, parent=self)

            self.utility_tower_buttons[i].tower_spec = tower_spec
            y = xy_start[1] + (i * button_spacing[1])
            self.utility_tower_buttons[i].set_xy((xy_start[0] * 2, y * 2))

        for child in self.all_children():
            child.update(game_state)


class TowerIconElement(UiElement):

    def __init__(self, tower_spec, xy, layer_id, parent=None):
        UiElement.__init__(self, xy, parent=parent)
        self.tower_spec = tower_spec
        self.layer_id = layer_id

        self.icon_sprite = None
        self.icon_outline_sprite = None

    def get_size(self):
        if self.icon_sprite is None:
            return super().get_size()
        else:
            return self.icon_sprite.size()

    def get_outline_color(self):
        return colors.WHITE

    def get_icon_model(self):
        if self.tower_spec is not None:
            return self.tower_spec.get_icon()
        else:
            return spriteref.MAIN_SHEET.question_icon

    def get_outline_model(self):
        return spriteref.MAIN_SHEET.icon_outline

    def all_sprites(self):
        if self.icon_sprite is not None:
            yield self.icon_sprite
        if self.icon_outline_sprite is not None:
            yield self.icon_outline_sprite

    def update(self, game_state):
        icon_model = self.get_icon_model()
        if self.icon_sprite is None:
            self.icon_sprite = sprites.ImageSprite.new_sprite(self.layer_id, scale=2, depth=10)
        abs_xy = self.get_xy(local=False)
        self.icon_sprite = self.icon_sprite.update(new_model=icon_model, new_x=abs_xy[0], new_y=abs_xy[1])

        outline_model = self.get_outline_model()
        outline_color = self.get_outline_color()
        if self.icon_outline_sprite is None:
            self.icon_outline_sprite = sprites.ImageSprite.new_sprite(self.layer_id, scale=2, depth=15)  # on top
        self.icon_outline_sprite = self.icon_outline_sprite.update(new_model=outline_model,
                                                                   new_x=abs_xy[0], new_y=abs_xy[1],
                                                                   new_color=outline_color)


class TowerBuyButton(TowerIconElement):

    def __init__(self, tower_spec, xy, layer_id, parent=None):
        TowerIconElement.__init__(self, tower_spec, xy, layer_id, parent=parent)

    def get_outline_color(self):
        if self.is_hovered():
            return colors.RED
        else:
            return super().get_outline_color()

    def can_be_hovered(self):
        return True

    def get_hover_text(self):
        # TODO - implement TextBuilder
        pass

    def can_be_clicked(self):
        return True


class BlightBarElement(UiElement):

    def __init__(self, xy, parent=None):
        UiElement.__init__(self, xy, parent=parent)
        self.bg_sprite = None

        self.blight_text = ": 0%"
        self.blight_text_sprite = None

        self.bar_sprite = None

    def get_size(self):
        if self.bg_sprite is None:
            return super().get_size()
        else:
            return self.bg_sprite.size()

    def all_sprites(self):
        if self.bg_sprite is not None:
            yield self.bg_sprite
        if self.blight_text_sprite is not None:
            for spr in self.blight_text_sprite.all_sprites():
                yield spr
        if self.bar_sprite is not None:
            yield self.bar_sprite

    def update(self, game_state):
        game_size = renderengine.get_instance().get_game_size()
        ui_blight_bar_model = spriteref.MAIN_SHEET.ui_blight_bar_bg

        abs_xy = (0, game_size[1] - ui_blight_bar_model.height() * 2)
        self.set_xy(abs_xy, local=False)

        if self.bg_sprite is None:
            self.bg_sprite = sprites.ImageSprite.new_sprite(spriteref.LAYER_UI_BG, scale=2)
        self.bg_sprite = self.bg_sprite.update(new_model=ui_blight_bar_model, new_x=abs_xy[0], new_y=abs_xy[1])

        blight_pcnt = game_state.get_blight_pcnt()

        blight_pcnt = (gs.get_instance().tick_count // 10) % 100 / 100  # TODO just for fun

        self.blight_text = "{}%".format(int(blight_pcnt * 100))
        if self.blight_text_sprite is None:
            self.blight_text_sprite = sprites.TextSprite(spriteref.LAYER_UI_FG, 0, 0, self.blight_text)
        self.blight_text_sprite = self.blight_text_sprite.update(new_text=self.blight_text, new_scale=1)
        text_xy = (abs_xy[0] + 16 * 2, 1 + abs_xy[1] + self.get_size()[1] // 2 - self.blight_text_sprite.get_size()[1] // 2)
        self.blight_text_sprite = self.blight_text_sprite.update(new_x=text_xy[0], new_y=text_xy[1], new_color=colors.BLACK)

        bar_start_x = 40  # in sheet dims
        bar_end_x = 272

        if self.bar_sprite is None:
            self.bar_sprite = sprites.ImageSprite.new_sprite(spriteref.LAYER_UI_FG, scale=2)
        bar_model = spriteref.MAIN_SHEET.ui_blight_bar
        max_bar_width = bar_end_x - bar_start_x
        bar_ratio = (blight_pcnt * max_bar_width / bar_model.width(), 1)
        self.bar_sprite = self.bar_sprite.update(new_model=bar_model, new_ratio=bar_ratio,
                                                 new_x=abs_xy[0] + 2 * bar_start_x,
                                                 new_y=abs_xy[1])




