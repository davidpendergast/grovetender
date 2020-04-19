
BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
RED = (1, 0, 0)
GRAY = (0.5, 0.5, 0.5)
YELLOW = (1, 1, 0)
OFF_WHITE = (0.953, 0.953, 0.953)

FRUIT_COLOR = (243 / 255, 125 / 255, 147 / 255)
VEG_COLOR = (166 / 255, 231 / 255, 119 / 255)
MUSHROOM_COLOR = (220 / 255, 220 / 255, 220 / 255) # (196 / 255, 196 / 255, 196 / 255)
FLOWER_COLOR = (255 / 255, 205 / 255, 117 / 255)
BLIGHT_COLOR = (228 / 255, 127 / 255, 253 / 255)

DIRT_COLOR = (131 / 255, 108 / 255, 67 / 255)
DIRT_LIGHT_COLOR = (174 / 255, 153 / 255, 115 / 255)

def darker(color, pcnt=0.3):
    res = []
    for i in range(0, 3):
        c = color[i]
        res.append(max(0, min(1, c * (1 - pcnt))))
    return tuple(res)
