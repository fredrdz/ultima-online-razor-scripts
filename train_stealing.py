"""
SCRIPT: train_stealing.py
Author: Talik Starr
IN:RISEN
Skill: Stealing
"""

from glossary.colors import colors
from stealing import stealing_run_once_targeted
from utils.items import MoveItemsByCount
from utils.item_actions.common import equip_hands, unequip_hands

packhorse_serial = 0x00004207
garlic_id = 0x0F84
backpack = Player.Backpack.Serial
return_items_list = [
    (garlic_id, -1),
]


def train_stealing_run_continuously(mobile_serial, item_to_steal):
    """
    Trains Stealing to the skill cap
    """

    if Player.GetRealSkillValue("Stealing") == Player.GetSkillCap("Stealing"):
        Misc.SendMessage(">> maxed out stealing skill", colors["notice"])
        return

    target_mobile = Mobiles.FindBySerial(mobile_serial)
    if target_mobile:
        Mobiles.Message(
            target_mobile,
            colors["notice"],
            "Selected mobile target for training Stealing",
        )
    else:
        mobile_serial = Target.PromptTarget("Select mobile target to train on")
        train_stealing_run_continuously(mobile_serial)

    while not Player.IsGhost and Player.GetRealSkillValue(
        "Stealing"
    ) < Player.GetSkillCap("Stealing"):
        left_item, right_item = unequip_hands()
        stealing_run_once_targeted(target_mobile)
        if left_item or right_item:
            equip_hands(left_item, right_item)

        if Items.BackpackCount(item_to_steal) > 0:
            MoveItemsByCount(return_items_list, backpack, target_mobile.Serial)


Misc.SendMessage(">> train stealing starting up...", colors["notice"])
train_stealing_run_continuously(packhorse_serial, garlic_id)
