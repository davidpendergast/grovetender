import src.engine.sprites as sprites

import src.game.spriteref as spriteref
import src.game.colors as colors


class TowerType:

    def __init__(self, identifier, color, is_utility=False):
        self.identifier = identifier
        self.color = color
        self.is_util = is_utility

    def get_color(self):
        return self.color

    def is_utility(self):
        return self.is_util

    def __eq__(self, other):
        if isinstance(other, TowerType):
            return self.identifier == other.identifier
        else:
            return False

    def __hash__(self):
        return hash(self.identifier)


class TowerTypes:

    FRUIT = TowerType("FRUIT", colors.FRUIT_COLOR)
    VEG = TowerType("VEG", colors.VEG_COLOR)
    MUSHROOM = TowerType("MUSHROOM", colors.MUSHROOM_COLOR)
    FLOWER = TowerType("FLOWER", colors.FLOWER_COLOR)
    BLIGHT = TowerType("BLIGHT", colors.BLIGHT_COLOR)

    SHOVEL = TowerType("SHOVEL", colors.DIRT_LIGHT_COLOR, is_utility=True)
    BIN = TowerType("BIN", colors.WHITE, is_utility=True)
    ROCK = TowerType("ROCK", colors.WHITE, is_utility=True)
    PURIFIER = TowerType("PURIFIER", colors.WHITE, is_utility=True)


class TowerStatType:

    def __init__(self, identifier, desc, color=colors.WHITE, neg_desc=None, hidden=False, is_prod=False):
        self.identifier = identifier
        self.desc = desc
        self.color = color
        self.neg_desc = neg_desc
        self.hidden = hidden
        self.is_prod = is_prod

    def is_production(self):
        return self.is_prod

    def is_hidden(self):
        return self.hidden

    def get_color(self):
        return self.color

    def get_desc(self, number):
        if number < 0 and self.neg_desc is not None:
            count = self.neg_desc.count("{}")
            if count == 0:
                return self.neg_desc
            elif count == 1:
                return self.neg_desc.format(number)
            elif count == 2:
                return self.neg_desc.format(number, number)
        else:
            count = self.desc.count("{}")
            if count == 0:
                return self.desc
            elif count == 1:
                return self.desc.format(number)
            elif count == 2:
                return self.desc.format(number, number)


class TowerStatTypes:

    CYCLE_LENGTH = TowerStatType("CYCLE_LENGTH", "Activates every {} days.")

    FRUIT_PRODUCTION = TowerStatType("FRUIT_PROD", "Produces {} fruit per activation.", is_prod=True, color=colors.FRUIT_COLOR)
    VEG_PRODUCTION = TowerStatType("VEG_PROD", "Produces {} vegetable(s) per activation.", is_prod=True, color=colors.VEG_COLOR)
    MUSHROOM_PRODUCTION = TowerStatType("MUSHROOM_PROD", "Produces {} mushroom(s) per activation.", is_prod=True, color=colors.MUSHROOM_COLOR)
    FLOWER_PRODUCTION = TowerStatType("FLOWER_PROD", "Produces {} flower(s) per activation.", is_prod=True, color=colors.FLOWER_COLOR)
    MONEY_PRODUCTION = TowerStatType("MONEY_PROD", "Gives ${} per activation")  # doesn't count as production

    MUSHROOM_HARVEST = TowerStatType("MUSHROOM_HARVEST", "Gives {} mushroom(s) when sold.")

    BLIGHT_PRODUCTION = TowerStatType("BLIGHT_PROD", "Produces {} blight per activation.", is_prod=True, color=colors.BLIGHT_COLOR)

    UPGRADING = TowerStatType("UPGRADING", "Has a {}% chance to upgrade per activation.")
    SPREADING = TowerStatType("SPREADING", "Has a {}% chance to spread per activation.")
    GROWING = TowerStatType("GROWTH", "Gives +{} production to all adjacent tiles.")
    SLOWING = TowerStatType("SLOWING", "Gives +{} day(s) per activation to all adjacent tiles.")
    WITHERING = TowerStatType("WITHER", "Gives -{} production to all adjacent tiles.")

    DIG = TowerStatType("DIG", "Converts rock to dirt.")
    STORAGE = TowerStatType("STORAGE", "Increases storage of all resources by {}.")
    PURIFYING = TowerStatType("PURIFYING", "Removes blight from up to {} adjacent tile(s).")

    NON_ACTIVATING = TowerStatType("NO_ACTIVATE", "Does not activate.")
    SELF_DESTRUCT = TowerStatType("SELF_DESTRUCT", "Removed after activating.")

    SELL_TO_BUY_RATIO = TowerStatType("SELL_RATIO", "Sells for {}% of purchase price.", hidden=True)


class TowerSpec:

    def __init__(self, name, tower_type, level, icon, stats, cost):
        self.name = name
        self.tower_type = tower_type
        self.level = level
        self.icon = icon
        self.stats = stats
        self.cost = cost

    def get_icon(self):
        return self.icon

    def can_sell(self):
        return self.cost >= 0

    def get_sell_price(self):
        ratio = self.stat_value(TowerStatTypes.SELL_TO_BUY_RATIO)
        return max(0, int(ratio * self.cost / 100))

    def get_color(self):
        return self.tower_type.get_color()

    def stat_value(self, stat_type):
        if stat_type not in self.stats:
            if stat_type == TowerStatTypes.SELL_TO_BUY_RATIO:
                return 50
            elif stat_type == TowerStatTypes.CYCLE_LENGTH:
                return 1
            else:
                return 0
        else:
            return self.stats[stat_type]

    def stat_value_in_world(self, stat_type, game_state, xy):
        base_val = self.stat_value(stat_type)
        if base_val > 0:
            return base_val + game_state.additional_stat_value_at(stat_type, xy)
        else:
            return base_val

    def get_hover_text(self, game_state=None, xy=None):
        res = sprites.TextBuilder()
        res.add(self.name, self.get_color())

        if game_state is not None and xy is not None:
            if self.stat_value_in_world(TowerStatTypes.NON_ACTIVATING, game_state, xy) <= 0:
                # we activate
                energy = max(0, game_state.get_activation_energy_at(xy))
                cycle_len = max(0, self.stat_value_in_world(TowerStatTypes.CYCLE_LENGTH, game_state, xy))
                energy = min(cycle_len, energy)
                if cycle_len > 0 and energy > 0:
                    bar_text = "cycle: [{}]".format("X" * energy + "-" * (cycle_len - energy))
                    n_spaces = max(20 - len(res.text), 1)
                    res.add(" " * n_spaces)
                    res.add(bar_text, color=colors.YELLOW)

        if self.can_sell():
            n_spaces = max(50 - len(res.text), 1)
            res.add(" " * n_spaces)

            if xy is None:
                # we're looking at it in the shop
                res.addLine("cost: ${}".format(self.cost))
            else:
                res.addLine("sell: ${}".format(self.get_sell_price()))
        else:
            res.addLine(" ")  # finish the line

        # the ordering works out because python happens to use linked hash maps
        for stat_type in self.stats:
            if stat_type.is_hidden():
                continue

            if game_state is not None and xy is not None:
                stat_val = self.stat_value_in_world(stat_type, game_state, xy)
            else:
                stat_val = self.stat_value(stat_type)

            if stat_val <= 0:
                continue
            res.addLine(stat_type.get_desc(stat_val), color=stat_type.get_color())

        n_lines = res.text.count("\n") - 1
        if self.can_sell() and game_state is not None and xy is not None and n_lines <= 3:
            if n_lines < 3:
                res.add("\n" * (3 - n_lines))  # want this to be at the bottom
            res.addLine("Right-click to sell.", color=colors.GRAY)

        return res

    def is_utility(self):
        return self.tower_type.is_utility()

    def is_blight(self):
        return self.tower_type == TowerTypes.BLIGHT


FRUIT_1 = None
FRUIT_2 = None
FRUIT_3 = None

VEG_1 = None
VEG_2 = None
VEG_3 = None

MUSHROOM_1 = None
MUSHROOM_2 = None
MUSHROOM_3 = None

FLOWER_1 = None
FLOWER_2 = None
FLOWER_3 = None

SHOVEL = None
BIN = None
GROWING_ROCK = None
PURIFICATION_TABLET = None

BLIGHT_1 = None
BLIGHT_2 = None
BLIGHT_3 = None


def init_towers():
    # TODO - make it possible to statically initialize objects that refer to sprites...
    global FRUIT_1, FRUIT_1, FRUIT_2, FRUIT_3, VEG_1, VEG_2, VEG_3, MUSHROOM_1, MUSHROOM_2, MUSHROOM_3, FLOWER_1, FLOWER_2, FLOWER_3
    global SHOVEL, GROWING_ROCK, PURIFICATION_TABLET, BIN, BLIGHT_1, BLIGHT_2, BLIGHT_3

    FRUIT_1 = TowerSpec("Fruit Vine", TowerTypes.FRUIT, 1, spriteref.MAIN_SHEET.fruit_icons[0],
                        {
                            TowerStatTypes.CYCLE_LENGTH: 3,
                            TowerStatTypes.FRUIT_PRODUCTION: 1,
                        }, 10)

    FRUIT_2 = TowerSpec("Fruit Bush", TowerTypes.FRUIT, 2, spriteref.MAIN_SHEET.fruit_icons[1],
                        {
                            TowerStatTypes.CYCLE_LENGTH: 4,
                            TowerStatTypes.FRUIT_PRODUCTION: 2,
                        }
                        , 25)
    FRUIT_3 = TowerSpec("Fruit Tree", TowerTypes.FRUIT, 3, spriteref.MAIN_SHEET.fruit_icons[2],
                        {
                            TowerStatTypes.CYCLE_LENGTH: 4,
                            TowerStatTypes.FRUIT_PRODUCTION: 6
                        }
                        , 60)

    VEG_1 = TowerSpec("Root Vegetable", TowerTypes.VEG, 1, spriteref.MAIN_SHEET.veg_icons[0],
                      {
                          TowerStatTypes.CYCLE_LENGTH: 1,
                          TowerStatTypes.VEG_PRODUCTION: 1
                      }, 6)
    VEG_2 = TowerSpec("Leafy Vegetable", TowerTypes.VEG, 2, spriteref.MAIN_SHEET.veg_icons[1],
                      {
                          TowerStatTypes.CYCLE_LENGTH: 2,
                          TowerStatTypes.VEG_PRODUCTION: 3
                      }, 15)
    VEG_3 = TowerSpec("Vegetable Stalk", TowerTypes.VEG, 3, spriteref.MAIN_SHEET.veg_icons[2],
                      {
                          TowerStatTypes.CYCLE_LENGTH: 2,
                          TowerStatTypes.VEG_PRODUCTION: 4,
                          TowerStatTypes.WITHERING: 1
                      }
                      , 45)

    MUSHROOM_1 = TowerSpec("Tiny Mushroom", TowerTypes.MUSHROOM, 1, spriteref.MAIN_SHEET.mushroom_icons[0],
                           {
                               TowerStatTypes.CYCLE_LENGTH: 5,
                               TowerStatTypes.MUSHROOM_HARVEST: 1,
                               TowerStatTypes.SPREADING: 30,
                               TowerStatTypes.UPGRADING: 20,
                               TowerStatTypes.SELL_TO_BUY_RATIO: 33
                           }, 18)
    MUSHROOM_2 = TowerSpec("Shelf Mushroom", TowerTypes.MUSHROOM, 2, spriteref.MAIN_SHEET.mushroom_icons[1],
                           {
                               TowerStatTypes.CYCLE_LENGTH: 5,
                               TowerStatTypes.MUSHROOM_HARVEST: 2,
                               TowerStatTypes.SPREADING: 30,
                               TowerStatTypes.UPGRADING: 20,
                               TowerStatTypes.SELL_TO_BUY_RATIO: 33
                           }, 36)
    MUSHROOM_3 = TowerSpec("Cluster Mushroom", TowerTypes.MUSHROOM, 3, spriteref.MAIN_SHEET.mushroom_icons[2],
                           {
                               TowerStatTypes.CYCLE_LENGTH: 5,
                               TowerStatTypes.MUSHROOM_HARVEST: 5,
                               TowerStatTypes.SPREADING: 50,
                               TowerStatTypes.SELL_TO_BUY_RATIO: 33
                           }, 72)

    FLOWER_1 = TowerSpec("Ok Flowers", TowerTypes.FLOWER, 1, spriteref.MAIN_SHEET.flower_icons[0],
                         {
                             TowerStatTypes.CYCLE_LENGTH: 4,
                             TowerStatTypes.FLOWER_PRODUCTION: 2,
                             TowerStatTypes.UPGRADING: 25,
                             TowerStatTypes.SELL_TO_BUY_RATIO: 75
                         }, 12)
    FLOWER_2 = TowerSpec("Nice Flowers", TowerTypes.FLOWER, 2, spriteref.MAIN_SHEET.flower_icons[1],
                         {
                             TowerStatTypes.CYCLE_LENGTH: 4,
                             TowerStatTypes.FLOWER_PRODUCTION: 2,
                             TowerStatTypes.UPGRADING: 25,
                             TowerStatTypes.SELL_TO_BUY_RATIO: 75
                         }
                         , 24)
    FLOWER_3 = TowerSpec("Awesome Flowers", TowerTypes.FLOWER, 3, spriteref.MAIN_SHEET.flower_icons[2],
                         {
                             TowerStatTypes.CYCLE_LENGTH: 4,
                             TowerStatTypes.FLOWER_PRODUCTION: 2,
                             TowerStatTypes.SPREADING: 10,
                             TowerStatTypes.SELL_TO_BUY_RATIO: 75
                         }
                         , 48)

    SHOVEL = TowerSpec("Shovel", TowerTypes.SHOVEL, 1, spriteref.MAIN_SHEET.shovel_icon,
                       {
                           TowerStatTypes.CYCLE_LENGTH: 1,
                           TowerStatTypes.DIG: 1,
                           TowerStatTypes.SELF_DESTRUCT: 1
                       }, 25)
    BIN = TowerSpec("Storage Bin", TowerTypes.BIN, 1, spriteref.MAIN_SHEET.storage_bin_icon,
                    {
                        TowerStatTypes.STORAGE: 5,
                        TowerStatTypes.NON_ACTIVATING: 1
                    }, 25)
    GROWING_ROCK = TowerSpec("Growing Rock", TowerTypes.ROCK, 1, spriteref.MAIN_SHEET.growing_rock_icon,
                             {
                                 TowerStatTypes.GROWING: 1,
                                 TowerStatTypes.SLOWING: 1,
                                 TowerStatTypes.NON_ACTIVATING: 1
                             }, 30)
    PURIFICATION_TABLET = TowerSpec("Purification Tablet", TowerTypes.PURIFIER, 1, spriteref.MAIN_SHEET.tombstone_icon,
                                    {
                                        TowerStatTypes.CYCLE_LENGTH: 2,
                                        TowerStatTypes.PURIFYING: 3,
                                        TowerStatTypes.SELF_DESTRUCT: 1
                                    }, 50)

    BLIGHT_1 = TowerSpec("Blighted Terrain", TowerTypes.BLIGHT, 1, spriteref.MAIN_SHEET.blight_icons[0],
                         {
                            TowerStatTypes.CYCLE_LENGTH: 3,
                            TowerStatTypes.UPGRADING: 30,
                            TowerStatTypes.SPREADING: 10,
                         }, -1)
    BLIGHT_2 = TowerSpec("Blighted Growth", TowerTypes.BLIGHT, 2, spriteref.MAIN_SHEET.blight_icons[1],
                         {
                             TowerStatTypes.CYCLE_LENGTH: 2,
                             TowerStatTypes.UPGRADING: 30,
                             TowerStatTypes.SPREADING: 20,
                             TowerStatTypes.BLIGHT_PRODUCTION: 1,
                         }, -1)
    BLIGHT_3 = TowerSpec("Blighted Abomination", TowerTypes.BLIGHT, 3, spriteref.MAIN_SHEET.blight_icons[2],
                         {
                             TowerStatTypes.CYCLE_LENGTH: 1,
                             TowerStatTypes.SPREADING: 30,
                             TowerStatTypes.BLIGHT_PRODUCTION: 2,
                         }
                         , -1)


def all_basic_towers():
    return [FRUIT_1, FRUIT_2, FRUIT_3,
            VEG_1, VEG_2, VEG_3,
            MUSHROOM_1, MUSHROOM_2, MUSHROOM_3,
            FLOWER_1, FLOWER_2, FLOWER_3]


def all_utility_towers():
    return [SHOVEL, GROWING_ROCK, PURIFICATION_TABLET, BIN]


def all_towers():
    blight_towers = [BLIGHT_1, BLIGHT_2, BLIGHT_3]
    return all_basic_towers() + all_utility_towers() + blight_towers


def get_spec_to_spread(tower_spec):
    if tower_spec is None:
        return None
    tower_type = tower_spec.tower_type
    if tower_type == TowerTypes.FRUIT:
        return FRUIT_1
    elif tower_type == TowerTypes.VEG:
        return VEG_1
    elif tower_type == TowerTypes.MUSHROOM:
        return MUSHROOM_1
    elif tower_type == TowerTypes.FLOWER:
        return FLOWER_1
    elif tower_type == TowerTypes.BLIGHT:
        return BLIGHT_1
    else:
        return None


def get_spec_to_upgrade_to(tower_spec):
    if tower_spec is None:
        return None
    tower_type = tower_spec.tower_type
    tower_level = tower_spec.level

    for ts in all_towers():
        if ts.tower_type == tower_type and ts.level == tower_level + 1:
            return ts

    return None

