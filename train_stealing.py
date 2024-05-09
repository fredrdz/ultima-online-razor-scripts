"""
SCRIPT: train_stealing.py
Author: Talik Starr
IN:RISEN
Skill: Stealing
"""

from glossary.colors import colors
from stealing import stealing_run_once_targeted
from utils.items import MoveItemsByCount

garlic = 0x0F84
backpack = Player.Backpack.Serial
return_items_list = [
    (garlic, -1),
]


def train_stealing_run_continuously():
    """
    Trains Stealing to the skill cap
    """
    if Player.GetRealSkillValue("Stealing") == Player.GetSkillCap("Stealing"):
        Misc.SendMessage(">> maxed out stealing skill", colors["notice"])
        return

    pack_horse_serial = Target.PromptTarget("Select pack horse to train on")
    pack_horse_mobile = Mobiles.FindBySerial(pack_horse_serial)
    Mobiles.Message(
        pack_horse_mobile, colors["notice"], "Selected pack horse for Stealing training"
    )

    while not Player.IsGhost and Player.GetRealSkillValue(
        "Stealing"
    ) < Player.GetSkillCap("Stealing"):
        stealing_run_once_targeted(pack_horse_mobile)
        if Items.BackpackCount(garlic) > 0:
            MoveItemsByCount(return_items_list, backpack, pack_horse_mobile.Serial)


Misc.SendMessage(">> train stealing starting up...", colors["notice"])
train_stealing_run_continuously()
