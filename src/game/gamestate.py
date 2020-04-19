import pygame

import src.engine.renderengine as renderengine
import src.engine.sprites as sprites
import src.utils.util as util
import src.engine.inputs as inputs

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


class GroundType:
    ROCK = "ROCK"
    DIRT = "DIRT"
    INACCESSIBLE = "INACCESSIBLE"


class GameState:

    def __init__(self):
        self.renderer = Renderer()

        self.basic_towers_in_shop = towers.all_basic_towers()
        self.utility_towers_in_shop = towers.all_utility_towers()

        self.trying_to_buy = None  # spec that the user has clicked
        self.current_hover_obj = None  # the thing you're hovering over

        self.max_blight = 100  # you lose when you hit this

        self.resources = {
            ResourceType.FRUIT: 0,
            ResourceType.VEG: 0,
            ResourceType.MUSHROOM: 0,
            ResourceType.FLOWER: 0,
            ResourceType.BLIGHT: 0,
            ResourceType.MONEY: 3000,
            ResourceType.VP: 0
        }

        self.world_tiles = {}  # (x, y) -> TileInfo
        self._populate_initial_world_tiles()

    def get_resources(self, res_type):
        return self.resources[res_type]

    def inc_resources(self, res_type, val):
        self.resources[res_type] += val
        if self.resources[res_type] < 0:
            print("WARN: resource {} is less than zero ({}), correcting".format(res_type, self.resources[res_type]))
            self.resources[res_type] = 0
        return self.resources[res_type]

    def set_trying_to_buy(self, tower_spec):
        self.trying_to_buy = tower_spec

    def can_build_at(self, pos):
        if self.trying_to_buy is None or pos not in self.world_tiles:
            return False
        else:
            tileinfo = self.world_tiles[pos]
            if tileinfo is None:
                return False
            elif tileinfo.tower_spec is not None:
                return False  # already a tower there
            elif tileinfo.ground_type == GroundType.INACCESSIBLE:
                return False
            elif self.trying_to_buy.cost < 0 or self.trying_to_buy.cost > self.get_resources(ResourceType.MONEY):
                return False
            elif tileinfo.ground_type == GroundType.ROCK and not self.trying_to_buy.is_utility():
                return False

        # we can do it!
        return True

    def try_to_build_at(self, pos):
        if self.can_build_at(pos):
            self.inc_resources(ResourceType.MONEY, -self.trying_to_buy.cost)
            self.world_tiles[pos].tower_spec = self.trying_to_buy
            print("INFO: placed tower {} at {}".format(self.trying_to_buy.name, pos))
            return True
        else:
            return False

    def try_to_sell_at(self, pos):
        print("trying to sell at {}".format(pos))
        return False

    def should_show_empty_tiles(self):
        return self.trying_to_buy is not None and self.trying_to_buy.is_utility()

    def get_blight_pcnt(self):
        return util.Utils.bound(self.get_resources(ResourceType.BLIGHT) / self.max_blight, 0, 1)

    def get_tile_info(self, xy):
        if xy in self.world_tiles:
            return self.world_tiles[xy]
        else:
            return None

    def screen_pos_to_world_cell_and_snapped_coords(self, xy):
        element_at = self._get_hover_obj_at(xy)
        if element_at is not None and isinstance(element_at, CellInWorldButton):
            return element_at.xy_in_world, element_at.get_xy(local=False)  # ok this is pretty bad lol

        return None, None

    def _populate_initial_world_tiles(self):
        inaccessible = [(0, i) for i in range(4, 8)]        # the rock is kinda irregular
        inaccessible.extend([(i, 7) for i in range(1, 9)])
        inaccessible.extend([(0, 0), (1, 0)])
        inaccessible.extend([(4 + i, i) for i in range(0, 4)])
        inaccessible.extend([(14, 7), (15, 7), (16, 7)])
        inaccessible.extend([(10, 2), (11, 3), (12, 3), (13, 3)])
        inaccessible.extend([(9, 0), (9, 1)])

        dirt = []
        for x in range(2, 5):
            for y in range(2, 4):
                dirt.append((x, y))
        for x in range(10, 14):
            for y in range(5, 7):
                dirt.append((x, y))

        for x in range(0, 17):
            for y in range(0, 8):
                xy = (x, y)
                if xy in inaccessible:
                    self.world_tiles[xy] = TileInfo(GroundType.INACCESSIBLE)
                elif xy in dirt:
                    self.world_tiles[xy] = TileInfo(GroundType.DIRT)
                else:
                    self.world_tiles[xy] = TileInfo(GroundType.ROCK)

    def update(self):
        self.handle_user_inputs()

        self.renderer.update(self)

    def set_hover_element(self, obj):
        self.current_hover_obj = obj

    def handle_user_inputs(self):
        input_state = inputs.get_instance()

        if not input_state.mouse_in_window():
            self.set_hover_element(None)
        else:
            mouse_pos = input_state.mouse_pos()
            hover_obj = self._get_hover_obj_at(mouse_pos)
            self.set_hover_element(hover_obj)

            mb1_was_pressed = input_state.mouse_was_pressed(button=1)
            mb3_was_pressed = input_state.mouse_was_pressed(button=3)
            if mb1_was_pressed or mb3_was_pressed:
                clicked_obj = self._get_clicked_obj_at(mouse_pos)
                if clicked_obj is not None:
                    clicked_obj.do_click(1 if mb1_was_pressed else 3, self)
                else:
                    self.set_trying_to_buy(None)

    def _get_hover_obj_at(self, game_pos):
        uis_to_check = [self.renderer.ui_main_panel,
                        self.renderer.ui_blight_bar,
                        self.renderer.world_scene]
                        # TODO add contracts
        for ui in uis_to_check:
            obj = ui.get_element_for_hover(game_pos)
            if obj is not None:
                return obj
        return None

    def _get_clicked_obj_at(self, game_pos):
        uis_to_check = [self.renderer.ui_main_panel,
                        self.renderer.ui_blight_bar,
                        self.renderer.world_scene]
        # TODO add contracts
        for ui in uis_to_check:
            obj = ui.get_element_for_click(game_pos)
            if obj is not None:
                return obj
        return None

    def handle_mouse_press(self, button, pos):
        pass

    def get_current_hover_text(self):
        if self.trying_to_buy is not None:
            return self.trying_to_buy.get_hover_text(self)
        elif self.current_hover_obj is not None:
            return self.current_hover_obj.get_hover_text(self)
        else:
            return None

    def get_current_hover_obj(self):
        return self.current_hover_obj


class TileInfo:

    def __init__(self, ground_type):
        self.tower_spec = None
        self.ground_type = ground_type

    def get_tower_spec(self):
        return self.tower_spec

    def get_ground_type(self):
        return self.ground_type


class Renderer:

    def __init__(self):
        self.ui_main_panel = MainPanelElement()
        self.ui_blight_bar = BlightBarElement()
        self.ui_hover_info_box = HoverInfoBox()

        self.world_scene = WorldSceneElement()

        self.cursor_icon = CursorIconElement()

    def all_sprites(self):
        for spr in self.ui_main_panel.all_sprites():
            yield spr
        for spr in self.ui_blight_bar.all_sprites():
            yield spr
        for spr in self.ui_hover_info_box.all_sprites():
            yield spr
        for spr in self.world_scene.all_sprites():
            yield spr
        for spr in self.cursor_icon.all_sprites():
            yield spr

    def update(self, game_state):
        self._update_ui(game_state)

        for sprite in self.all_sprites():
            renderengine.get_instance().update(sprite)

    def _update_ui(self, game_state):
        self.ui_main_panel.update(game_state)
        self.ui_blight_bar.update(game_state)
        self.ui_hover_info_box.update(game_state)
        self.cursor_icon.update(game_state)

        self.world_scene.update(game_state)


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

    def get_rect_for_hover_test(self):
        return self.get_rect(local=False)

    def all_sprites(self):
        yield

    def update(self, game_state):
        pass

    def can_be_hovered(self):
        return False

    def get_element_for_hover(self, pos):
        for child in self.all_children():
            if child.can_be_hovered() and util.Utils.rect_contains(child.get_rect_for_hover_test(), pos):
                return child
        if self.can_be_hovered() and util.Utils.rect_contains(self.get_rect_for_hover_test(), pos):
            return self
        else:
            return None

    def do_hover(self):
        self._hover_tick = gs.get_instance().tick_count

    def is_hovered(self):
        return gs.get_instance().tick_count - self._hover_tick <= 1

    def get_hover_text(self, game_state):
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

    def do_click(self, button, game_state):
        print("clicked ui element: {}".format(type(self).__name__))


class MainPanelElement(UiElement):

    def __init__(self):
        UiElement.__init__(self, (0, 0), parent=None)
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


class TowerIconElement(UiElement):  # this can really be merged w/ TowerBuyButton

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

    def get_outline_color(self, game_state):
        return colors.WHITE

    def get_icon_model(self):
        if self.tower_spec is not None:
            return self.tower_spec.get_icon()
        else:
            return spriteref.MAIN_SHEET.question_icon

    def get_outline_model(self):
        return spriteref.MAIN_SHEET.icon_outline

    def can_be_hovered(self):
        return True

    def get_hover_text(self, game_state):
        if self.tower_spec is None:
            return None
        else:
            return self.tower_spec.get_hover_text(game_state=game_state)

    def can_be_clicked(self):
        return True

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
        outline_color = self.get_outline_color(game_state)
        if self.icon_outline_sprite is None:
            self.icon_outline_sprite = sprites.ImageSprite.new_sprite(self.layer_id, scale=2, depth=5)  # on top
        self.icon_outline_sprite = self.icon_outline_sprite.update(new_model=outline_model,
                                                                   new_x=abs_xy[0], new_y=abs_xy[1],
                                                                   new_color=outline_color)


class TowerBuyButton(TowerIconElement):

    def __init__(self, tower_spec, xy, layer_id, parent=None):
        TowerIconElement.__init__(self, tower_spec, xy, layer_id, parent=parent)

    def get_outline_color(self, game_state):
        if game_state.trying_to_buy is None and game_state.get_current_hover_obj() == self:
            return colors.RED
        elif game_state.trying_to_buy is not None and game_state.trying_to_buy == self.tower_spec:
            return colors.RED
        else:
            return super().get_outline_color(game_state)

    def get_rect_for_hover_test(self):
        base_rect = self.get_rect(local=False)
        if base_rect[2] > 0 and base_rect[3] > 0:
            return util.Utils.rect_expand(base_rect, left_expand=2, right_expand=2, up_expand=2, down_expand=2)
        else:
            return super().get_rect_for_hover_test()

    def can_be_hovered(self):
        return True

    def can_be_clicked(self):
        return True

    def do_click(self, button, game_state):
        if button == 1:
            if game_state.trying_to_buy is not None and game_state.trying_to_buy == self.tower_spec:
                game_state.set_trying_to_buy(None)  # toggle it back off
            else:
                game_state.set_trying_to_buy(self.tower_spec)


class HoverInfoBox(UiElement):

    def __init__(self):
        UiElement.__init__(self, (0, 0), parent=None)
        self.box_bg_sprite = None
        self.text_sprite = None

    def get_size(self):
        if self.box_bg_sprite is None:
            return super().get_size()
        else:
            return self.box_bg_sprite.size()

    def all_sprites(self):
        if self.box_bg_sprite is not None:
            for spr in self.box_bg_sprite.all_sprites():
                yield spr
        if self.text_sprite is not None:
            for spr in self.text_sprite.all_sprites():
                yield spr

    def update(self, game_state):
        hover_text = game_state.get_current_hover_text()
        if hover_text is None:
            if self.text_sprite is not None:
                renderengine.get_instance().remove(self.text_sprite)
                self.text_sprite = None
            if self.box_bg_sprite is not None:
                renderengine.get_instance().remove(self.box_bg_sprite)
                self.box_bg_sprite = None
        else:
            if isinstance(hover_text, str):
                hover_text = sprites.TextBuilder().add(hover_text)

            # it always goes on top of this bar
            # so why not make it a child of the bar? we could
            blight_bar_model = ui_blight_bar_model = spriteref.MAIN_SHEET.ui_blight_bar_bg
            game_size = renderengine.get_instance().get_game_size()
            border = 4  # sheet dims
            box_height = 36
            inner_rect = [border * 2,
                          game_size[1] - ui_blight_bar_model.height() * 2 - box_height * 2 - border * 2,
                          ui_blight_bar_model.width() * 2 - border * 4,
                          box_height * 2]
            if self.box_bg_sprite is None:
                self.box_bg_sprite = sprites.BorderBoxSprite(spriteref.LAYER_UI_BG, inner_rect, scale=2, all_borders=spriteref.MAIN_SHEET.box_borders)
            self.box_bg_sprite = self.box_bg_sprite.update(new_rect=inner_rect)

            if self.text_sprite is None:
                self.text_sprite = sprites.TextSprite(spriteref.LAYER_UI_FG, 0, 0, "abc", scale=1)
            self.text_sprite = self.text_sprite.update(new_x=inner_rect[0], new_y=inner_rect[1],
                                                       new_text=hover_text.text, new_color_lookup=hover_text.colors)


class BlightBarElement(UiElement):

    def __init__(self):
        UiElement.__init__(self, (0, 0), parent=None)
        self.bg_sprite = None

        self.blight_text = ": 0%"
        self.blight_text_sprite = None

        self.bar_sprite = None

    def get_size(self):
        if self.bg_sprite is None:
            return super().get_size()
        else:
            return self.bg_sprite.size()

    def can_be_hovered(self):
        return True

    def get_hover_text(self, game_state):
        first_line = "Blight at {}/{}".format(game_state.get_resources(ResourceType.BLIGHT), game_state.max_blight)
        return sprites.TextBuilder()\
                .addLine(first_line, color=colors.BLIGHT_COLOR)\
                .addLine("When it fills completely, the garden dies and you lose.")

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


class CellInWorldButton(UiElement):

    def __init__(self, xy, xy_in_world, parent=None):
        UiElement.__init__(self, xy, parent=parent)
        self.xy_in_world = xy_in_world

        self.icon_sprite = None
        self.icon_outline_sprite = None

    def get_size(self):
        if self.icon_sprite is not None:
            return self.icon_sprite.size()
        else:
            return super().get_size()

    def can_be_hovered(self):
        return True

    def get_hover_text(self, game_state):
        tileinfo = game_state.get_tile_info(self.xy_in_world)
        if tileinfo is None:
            return None
        else:
            if tileinfo.tower_spec is not None:
                return tileinfo.tower_spec.get_hover_text(game_state=game_state, xy=self.xy_in_world)
            elif tileinfo.ground_type == GroundType.DIRT:
                res = sprites.TextBuilder().addLine("Dirt", color=colors.DIRT_LIGHT_COLOR)
                res.addLine("Perfect for any plant or fungus.")
                return res
            elif tileinfo.ground_type == GroundType.ROCK and game_state.should_show_empty_tiles():
                res = sprites.TextBuilder().addLine("Rock")
                res.addLine("Use the Shovel to turn this into Dirt.")
                return res

    def can_be_clicked(self):
        return True

    def do_click(self, button, game_state):
        if game_state.trying_to_buy is not None:
            if button == 1:
                game_state.try_to_build_at(self.xy_in_world)
            game_state.set_trying_to_buy(None)
        elif button != 1:
            game_state.try_to_sell_at(self.xy_in_world)

    def set_xy_in_world(self, xy):
        self.xy_in_world = xy

    def all_sprites(self):
        if self.icon_sprite is not None:
            yield self.icon_sprite
        if self.icon_outline_sprite is not None:
            yield self.icon_outline_sprite

    def update(self, game_state):
        tileinfo = game_state.get_tile_info(self.xy_in_world)
        icon_model = None
        outline_color = None

        if tileinfo is None:
            pass  # just destroy it
        else:
            tower_spec = tileinfo.get_tower_spec()
            ground_type = tileinfo.get_ground_type()

            if tower_spec is not None:
                icon_model = tower_spec.get_icon()
                if ground_type == GroundType.DIRT:
                    outline_color = colors.DIRT_COLOR
                else:
                    outline_color = colors.WHITE
            else:
                if ground_type == GroundType.ROCK:
                    if game_state.should_show_empty_tiles():
                        icon_model = spriteref.MAIN_SHEET.tile_empty
                    else:
                        pass  # just destroy
                elif ground_type == GroundType.DIRT:
                    icon_model = spriteref.MAIN_SHEET.tile_dirt

        xy_abs = self.get_xy(local=False)

        if icon_model is not None:
            if self.icon_sprite is None:
                self.icon_sprite = sprites.ImageSprite.new_sprite(spriteref.LAYER_SCENE_FG, scale=2, depth=10)
            self.icon_sprite = self.icon_sprite.update(new_model=icon_model, new_x=xy_abs[0], new_y=xy_abs[1])
        else:
            if self.icon_sprite is not None:
                renderengine.get_instance().remove(self.icon_sprite)
                self.icon_sprite = None

        if outline_color is not None:
            if self.icon_outline_sprite is None:
                self.icon_outline_sprite = sprites.ImageSprite.new_sprite(spriteref.LAYER_SCENE_FG, scale=2, depth=5)
            self.icon_outline_sprite = self.icon_outline_sprite.update(new_model=spriteref.MAIN_SHEET.icon_outline,
                                                                       new_x=xy_abs[0], new_y=xy_abs[1],
                                                                       new_color=outline_color)
        else:
            if self.icon_outline_sprite is not None:
                renderengine.get_instance().remove(self.icon_outline_sprite)
                self.icon_outline_sprite = None


class CursorIconElement(UiElement):

    def __init__(self):
        UiElement.__init__(self, (0, 0), parent=None)

        self.icon_sprite = None
        self.icon_outline_sprite = None

    def all_sprites(self):
        if self.icon_sprite is not None:
            yield self.icon_sprite
        if self.icon_outline_sprite is not None:
            yield self.icon_outline_sprite

    def update(self, game_state):
        mouse_pos = inputs.get_instance().mouse_pos()
        if mouse_pos is None or game_state.trying_to_buy is None:
            if self.icon_sprite is not None:
                renderengine.get_instance().remove(self.icon_sprite)
                self.icon_sprite = None
            if self.icon_outline_sprite is not None:
                renderengine.get_instance().remove(self.icon_outline_sprite)
                self.icon_outline_sprite = None
        else:
            icon_model = game_state.trying_to_buy.get_icon()
            if self.icon_sprite is None:
                self.icon_sprite = sprites.ImageSprite.new_sprite(spriteref.LAYER_UI_TOOLTIP, scale=2, depth=10)

            outline_color = None
            x = mouse_pos[0] - icon_model.width() * 2 // 2
            y = mouse_pos[1] - icon_model.height() * 2 // 2

            xy_in_world, snapped_coords = game_state.screen_pos_to_world_cell_and_snapped_coords(mouse_pos)

            if xy_in_world is not None and game_state.can_build_at(xy_in_world):
                tileinfo = game_state.get_tile_info(xy_in_world)
                outline_color = colors.DIRT_COLOR if tileinfo.ground_type == GroundType.DIRT else colors.WHITE
                x = snapped_coords[0]
                y = snapped_coords[1]

            self.icon_sprite = self.icon_sprite.update(new_model=icon_model, new_x=x, new_y=y)

            if outline_color is None:
                if self.icon_outline_sprite is not None:
                    renderengine.get_instance().remove(self.icon_outline_sprite)
                    self.icon_outline_sprite = None
            else:
                if self.icon_outline_sprite is None:
                    self.icon_outline_sprite = sprites.ImageSprite.new_sprite(spriteref.LAYER_UI_TOOLTIP, scale=2, depth=5)
                self.icon_outline_sprite = self.icon_outline_sprite.update(new_model=spriteref.MAIN_SHEET.icon_outline,
                                                                           new_x=x, new_y=y,
                                                                           new_color=outline_color)


class WorldSceneElement(UiElement):

    def __init__(self):
        UiElement.__init__(self, (0, 0), parent=None)

        self.big_rock_sprite = None
        self.cells = {}  # (x, y) -> CellInWorldButton

    def all_sprites(self):
        if self.big_rock_sprite is not None:
            yield self.big_rock_sprite

        for key in self.cells:
            butt = self.cells[key]
            for spr in butt.all_sprites():
                yield spr

    def all_children(self):
        for key in self.cells:
            yield self.cells[key]

    def update(self, game_state):
        if self.big_rock_sprite is None:
            self.big_rock_sprite = sprites.ImageSprite.new_sprite(spriteref.LAYER_SCENE_ENVIRONMENT, scale=2)

        game_size = renderengine.get_instance().get_game_size()
        self.set_xy((0, game_size[1] - 204 * 2), local=False)

        abs_xy = self.get_xy(local=False)
        rock_model = spriteref.MAIN_SHEET.giant_rock

        self.big_rock_sprite = self.big_rock_sprite.update(new_model=rock_model,
                                                           new_x=abs_xy[0], new_y=abs_xy[1])

        no_longer_exist = set()  # shouldn't be needed
        for xy in self.cells:
            no_longer_exist.add(xy)

        for xy in game_state.world_tiles:
            tileinfo = game_state.get_tile_info(xy)
            if tileinfo is not None and xy not in self.cells:
                self.cells[xy] = CellInWorldButton((0, 0), xy, parent=self)
            if xy in no_longer_exist:
                no_longer_exist.remove(xy)

        for xy in no_longer_exist:  # again, there's no reason why a cell would disappear from the game state
            button = self.cells[xy]
            for spr in button.all_sprites():
                renderengine.get_instance().remove(spr)
            del self.cells[xy]

        for xy in self.cells:
            button = self.cells[xy]
            render_xy = (16 * 2 * (xy[0] + 1),
                         16 * 2 * (xy[1] + 1))
            button.set_xy(render_xy, local=True)
            button.set_xy_in_world(xy)
            button.update(game_state)









