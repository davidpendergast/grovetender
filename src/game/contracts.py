import random
import math

import src.game.spriteref as spriteref


class ContractState:

    def __init__(self, resource_reqs, payout, vp_reward, blight_punishment, time_limit, bg_sprite):
        self.resource_reqs = resource_reqs  # ResourceType -> int
        self.payout = payout
        self.vp_reward = vp_reward
        self.blight_punishment = blight_punishment
        self.time_limit = time_limit
        self.days_active = 1

        self.bg_sprite = bg_sprite

    def get_time_limit_pcnt(self):
        return min(1.0, self.days_active / self.time_limit)


def gen_contract(day):
    from src.game.gamestate import ResourceTypes

    if day < 10:
        max_types = 1
    elif day < 20:
        max_types = 2
    else:
        max_types = 3

    REQ_TYPES = [ResourceTypes.FRUIT, ResourceTypes.VEG, ResourceTypes.MUSHROOM, ResourceTypes.FLOWER]

    QUANTITY_SCALES = {
        ResourceTypes.FRUIT: 5,
        ResourceTypes.VEG: 7,
        ResourceTypes.MUSHROOM: 2,
        ResourceTypes.FLOWER: 3
    }

    # required quantity grows exponentially, to ensure the player eventually loses
    QUANT_GROWTH_MULT_PER_DAY = 0.1
    QUANT_GROWTH_EXP_PER_DAY = 0.05

    DIFFICULTY_WEIGHTS = {
        ResourceTypes.FRUIT: 5,
        ResourceTypes.VEG: 2,
        ResourceTypes.MUSHROOM: 10,
        ResourceTypes.FLOWER: 7
    }

    n_types_for_res = 1 + int(random.random() * max_types)

    req_types_for_res = random.choices(REQ_TYPES, [QUANTITY_SCALES[t] for t in REQ_TYPES], k=n_types_for_res)

    res_reqs = {}
    for res_type in req_types_for_res:
        max_quant = math.ceil(QUANTITY_SCALES[res_type] * (1 + QUANT_GROWTH_MULT_PER_DAY * day) ** (1 + QUANT_GROWTH_EXP_PER_DAY * day))
        min_quant = max(1, int(max_quant * 0.33))
        quant = min_quant + int(random.random() * (max_quant + 1 - min_quant))

        res_reqs[res_type] = quant

    difficulty_val = 0
    for res_type in res_reqs:
        difficulty_val += res_reqs[res_type] * DIFFICULTY_WEIGHTS[res_type]

    MONEY_SCALE = 8 - (3 * min(100, day)/100)

    res_payout = math.ceil(MONEY_SCALE * math.sqrt(difficulty_val))

    VP_SCALE = 1

    res_vps = math.ceil(VP_SCALE * math.sqrt(difficulty_val))

    PUNISHMENT_GROWTH_PER_DAY = 0.05

    max_punishment = min(20, 1 + math.ceil(PUNISHMENT_GROWTH_PER_DAY * day))
    res_punishment = math.ceil((0.5 + random.random() / 2) * max_punishment)

    TIME_LIMIT_LOG_SCALE = 2
    res_time_limit = 4 + TIME_LIMIT_LOG_SCALE * math.log(difficulty_val, math.e)

    req_types_for_res.sort(key=lambda typ: res_reqs[typ] * DIFFICULTY_WEIGHTS[typ], reverse=True)

    primary_type = req_types_for_res[0]
    if primary_type == ResourceTypes.FRUIT:
        bg_sprite = spriteref.MAIN_SHEET.contract_panel_fruit
    elif primary_type == ResourceTypes.VEG:
        bg_sprite = spriteref.MAIN_SHEET.contract_panel_veg
    elif primary_type == ResourceTypes.MUSHROOM:
        bg_sprite = spriteref.MAIN_SHEET.contract_panel_mushroom
    else:
        bg_sprite = spriteref.MAIN_SHEET.contract_panel_flower

    return ContractState(res_reqs, res_payout, res_vps, res_punishment, res_time_limit, bg_sprite)
