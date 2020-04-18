import src.game.spriteref as spriteref
import src.game.colors as colors


class TowerType:

    def __init__(self, identifier, color):
        self.identifier = identifier
        self.color = color

    def get_color(self):
        return self.color

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

    SHOVEL = TowerType("SHOVEL", colors.WHITE)
    BIN = TowerType("BIN", colors.WHITE)
    ROCK = TowerType("ROCK", colors.WHITE)
    PURIFIER = TowerType("PURIFIER", colors.WHITE)


class TowerStatType:
    pass


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

    def get_color(self):
        return self.tower_type.get_color()


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

    FRUIT_1 = TowerSpec("Fruit Vine", TowerTypes.FRUIT, 1, spriteref.MAIN_SHEET.fruit_icons[0], {}, 10)
    FRUIT_2 = TowerSpec("Fruit Bush", TowerTypes.FRUIT, 2, spriteref.MAIN_SHEET.fruit_icons[1], {}, 25)
    FRUIT_3 = TowerSpec("Fruit Tree", TowerTypes.FRUIT, 3, spriteref.MAIN_SHEET.fruit_icons[2], {}, 60)

    VEG_1 = TowerSpec("Root Vegetable", TowerTypes.VEG, 1, spriteref.MAIN_SHEET.veg_icons[0], {}, 6)
    VEG_2 = TowerSpec("Leafy Vegetable", TowerTypes.VEG, 2, spriteref.MAIN_SHEET.veg_icons[1], {}, 15)
    VEG_3 = TowerSpec("Vegetable Stalk", TowerTypes.FRUIT, 3, spriteref.MAIN_SHEET.veg_icons[2], {}, 45)

    MUSHROOM_1 = TowerSpec("Tiny Mushroom", TowerTypes.MUSHROOM, 1, spriteref.MAIN_SHEET.mushroom_icons[0], {}, 18)
    MUSHROOM_2 = TowerSpec("Shelf Mushroom", TowerTypes.MUSHROOM, 2, spriteref.MAIN_SHEET.mushroom_icons[1], {}, 36)
    MUSHROOM_3 = TowerSpec("Cluster Mushroom", TowerTypes.MUSHROOM, 3, spriteref.MAIN_SHEET.mushroom_icons[2], {}, 72)

    FLOWER_1 = TowerSpec("Ok Flowers", TowerTypes.FLOWER, 1, spriteref.MAIN_SHEET.flower_icons[0], {}, 12)
    FLOWER_2 = TowerSpec("Nice Flowers", TowerTypes.FLOWER, 1, spriteref.MAIN_SHEET.flower_icons[0], {}, 24)
    FLOWER_3 = TowerSpec("Awesome Flowers", TowerTypes.FLOWER, 1, spriteref.MAIN_SHEET.flower_icons[0], {}, 48)

    SHOVEL = TowerSpec("Shovel", TowerTypes.SHOVEL, 1, spriteref.MAIN_SHEET.shovel_icon, {}, 25)
    BIN = TowerSpec("Storage Bin", TowerTypes.BIN, 1, spriteref.MAIN_SHEET.storage_bin_icon, {}, 15)
    GROWING_ROCK = TowerSpec("Growing Rock", TowerTypes.ROCK, 1, spriteref.MAIN_SHEET.growing_rock_icon, {}, 50)
    PURIFICATION_TABLET = TowerSpec("Purification Tablet", TowerTypes.PURIFIER, 1, spriteref.MAIN_SHEET.tombstone_icon, {}, 20)

    BLIGHT_1 = TowerSpec("Blighted Soil", TowerTypes.BLIGHT, 1, spriteref.MAIN_SHEET.blight_icon, {}, -1)
    BLIGHT_2 = TowerSpec("Blighted Growth", TowerTypes.BLIGHT, 2, spriteref.MAIN_SHEET.blight_icon, {}, -1)
    BLIGHT_3 = TowerSpec("Blighted Abomination", TowerTypes.BLIGHT, 3, spriteref.MAIN_SHEET.blight_icon, {}, -1)


def all_basic_towers():
    return [FRUIT_1, FRUIT_2, FRUIT_3,
            VEG_1, VEG_2, VEG_3,
            MUSHROOM_1, MUSHROOM_2, MUSHROOM_3,
            FLOWER_1, FLOWER_2, FLOWER_3]


def all_utility_towers():
    return [SHOVEL, GROWING_ROCK, PURIFICATION_TABLET, BIN]

