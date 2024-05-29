"""
SCRIPT: train_Stealing.py
Author: Talik Starr
IN:RISEN
Skill: Stealing
"""

import config
import Items, Player, Misc, Mobiles, Target
from glossary.colors import colors
from skill_Stealing import stealing_run_once_targeted
from utils.item_actions.common import unequip_hands

mobile_serial = 0x00004207  # pack horse
item_to_steal = 0x0F84
# 0x0F84 garlic
# 0x0F43 hatchet
# 0x0123 pack horse


def train_stealing_run_continuously(target_mobile, target_item):
    """
    Trains Stealing to the skill cap
    """
    Misc.SendMessage(">> train stealing starting up...", colors["notice"])

    # setup target mobile
    tar_mobile = Mobiles.FindBySerial(target_mobile)
    if tar_mobile:
        Misc.SendMessage(
            ">> stealing mobile target: " + tar_mobile.Name, colors["info"]
        )
        Mobiles.Message(
            tar_mobile,
            colors["notice"],
            "Selected mobile for Stealing",
        )
    else:
        tar_mobile = Target.PromptTarget(
            "Select mobile target to train on:", colors["notice"]
        )
        train_stealing_run_continuously(tar_mobile, target_item)

    # setup target item
    tar_item = Items.FindByID(target_item, -1, Player.Backpack.Serial)
    if not tar_item:
        tar_item = Items.FindByID(target_item, -1, tar_mobile.Backpack.Serial)

    if tar_item:
        Misc.SendMessage(">> stealing item target: " + tar_item.Name, colors["info"])
    else:
        tar_item = Target.PromptTarget("Select item to train on:", colors["notice"])
        # Misc.SendMessage(">> debug: " + str(tar_item), colors["debug"])
        item = Items.FindBySerial(tar_item)
        train_stealing_run_continuously(tar_mobile.Serial, item.ItemID)

    # prep our hands
    unequip_hands()

    while not Player.IsGhost and Player.GetRealSkillValue(
        "Stealing"
    ) < Player.GetSkillCap("Stealing"):
        stealing_run_once_targeted(tar_mobile, tar_item.ItemID)

        if Items.BackpackCount(tar_item.ItemID) > 0:
            return_item = Items.FindByID(tar_item.ItemID, -1, Player.Backpack.Serial)
            Items.Move(return_item, tar_mobile, -1, 0, 0)
            Misc.Pause(config.dragDelayMilliseconds)

    if Player.GetRealSkillValue("Stealing") == Player.GetSkillCap("Stealing"):
        Misc.SendMessage(">> maxed out stealing skill", colors["notice"])
        return


train_stealing_run_continuously(mobile_serial, item_to_steal)
