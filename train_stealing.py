"""
SCRIPT: train_stealing.py
Author: Talik Starr
IN:RISEN
Skill: Stealing
"""

import config
from glossary.colors import colors
from stealing import stealing_run_once_targeted
from utils.item_actions.common import unequip_hands

mobile_serial = 0x00004207  # pack horse
item_to_steal = 0x0F84  # garlic


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

    unequip_hands()

    while not Player.IsGhost and Player.GetRealSkillValue(
        "Stealing"
    ) < Player.GetSkillCap("Stealing"):
        stealing_run_once_targeted(target_mobile)

        if Items.BackpackCount(item_to_steal) > 0:
            item = Items.FindByID(item_to_steal, -1, Player.Backpack.Serial)
            Items.Move(item, mobile_serial, -1, 0, 0)
            Misc.Pause(config.dragDelayMilliseconds)


Misc.SendMessage(">> train stealing starting up...", colors["notice"])
train_stealing_run_continuously(mobile_serial, item_to_steal)
