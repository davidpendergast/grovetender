import src.game.spriteref as spriteref

class TowerType:
    FRUIT = "FRUIT"
    VEG = "VEG"
    MUSHROOM = "MUSHROOM"
    FLOWER = "FLOWER"
    BLIGHT = "BLIGHT"

    SHOVEL = "SHOVEL"
    BIN = "BIN"
    ROCK = "ROCK"
    PURIFIER = "PURIFIER"


class TowerStatType:
    pass


class TowerSpec:

    def __init__(self, name, tower_type, level, icon, stats, cost):
        self.name = name
        self.tower_type = tower_type
        self.level = level
        self.icon = icon
        self.stats = {}
        self.cost = cost

    def can_sell(self):
        return self.cost >= 0


FRUIT_1 = TowerSpec("Fruit Vine", TowerType.FRUIT, 1, spriteref.MAIN_SHEET.fruit_icons[0], {}, 10)
FRUIT_2 = TowerSpec("Fruit Bush", TowerType.FRUIT, 2, spriteref.MAIN_SHEET.fruit_icons[1], {}, 25)
FRUIT_3 = TowerSpec("Fruit Tree", TowerType.FRUIT, 3, spriteref.MAIN_SHEET.fruit_icons[2], {}, 60)

VEG_1 = TowerSpec("Root Vegetable", TowerType.VEG, 1, spriteref.MAIN_SHEET.veg_icons[0], {}, 6)
VEG_2 = TowerSpec("Leafy Vegetable", TowerType.VEG, 2, spriteref.MAIN_SHEET.veg_icons[1], {}, 15)
VEG_3 = TowerSpec("Vegetable Stalk", TowerType.FRUIT, 3, spriteref.MAIN_SHEET.veg_icons[2], {}, 45)

MUSHROOM_1 = TowerSpec("Tiny Mushroom", TowerType.MUSHROOM, 1, spriteref.MAIN_SHEET.mushroom_icons[0], {}, 18)
MUSHROOM_2 = TowerSpec("Shelf Mushroom", TowerType.MUSHROOM, 2, spriteref.MAIN_SHEET.mushroom_icons[1], {}, 36)
MUSHROOM_3 = TowerSpec("Cluster Mushroom", TowerType.MUSHROOM, 3, spriteref.MAIN_SHEET.mushroom_icons[2], {}, 72)

FLOWER_1 = TowerSpec("Ok Flowers", TowerType.FLOWER, 1, spriteref.MAIN_SHEET.flower_icons[0], {}, 12)
FLOWER_2 = TowerSpec("Nice Flowers", TowerType.FLOWER, 1, spriteref.MAIN_SHEET.flower_icons[0], {}, 24)
FLOWER_3 = TowerSpec("Awesome Flowers", TowerType.FLOWER, 1, spriteref.MAIN_SHEET.flower_icons[0], {}, 48)

SHOVEL = TowerSpec("Shovel", TowerType.SHOVEL, 1, spriteref.MAIN_SHEET.shovel_icon, {}, 25)
BIN = TowerSpec("Storage Bin", TowerType.BIN, 1, spriteref.MAIN_SHEET.storage_bin_icon, {}, 15)
GROWING_ROCK = TowerSpec("Growing Rock", TowerType.ROCK, 1, spriteref.MAIN_SHEET.growing_rock_icon, {}, 50),
PURIFICATION_TABLET = TowerSpec("Purification Tablet", TowerType.PURIFIER, 1, spriteref.MAIN_SHEET.tombstone_icon, {}, 20)

BLIGHT_1 = TowerSpec("Blighted Soil", TowerType.BLIGHT, 1, spriteref.MAIN_SHEET.blight_icon, {}, -1)
BLIGHT_2 = TowerSpec("Blighted Growth", TowerType.BLIGHT, 2, spriteref.MAIN_SHEET.blight_icon, {}, -1)
BLIGHT_3 = TowerSpec("Blighted Abomination", TowerType.BLIGHT, 3, spriteref.MAIN_SHEET.blight_icon, {}, -1)