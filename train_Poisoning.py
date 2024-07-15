"""
SCRIPT: train_Poisoning.py
Author: Talik Starr
IN:RISEN
Skill: Poisoning
"""

# custom RE packages
import Items, Player, Misc, Target
from config import shardLatency
from glossary.colors import colors
from glossary.items.potions import potions
from glossary.items.miscellaneous import miscellaneous
from utils.items import FindItem, FindNumberOfItems, MoveItemsByCount

# ---------------------------------------------------------------------
# init
skillName = "Poisoning"
poisonBottle = potions["lesser poison potion"]
poisonBottleID = poisonBottle.itemID
emptyBottle = miscellaneous["empty bottle"]
emptyBottleID = emptyBottle.itemID
backpack = Player.Backpack
poisonTarget = 0x40011E60
restockContainer = 0x40125C18
depositList = [(emptyBottleID, -1)]
# ---------------------------------------------------------------------


def TrainPoisoning(poisonTarget, restockContainer):
    """
    Trains Poisoning to the skill cap
    """

    # check poison target
    if not poisonTarget:
        poisonTarget = Target.PromptTarget(
            ">> Select the item to poison:", colors["notice"]
        )

    # check restock container
    if not restockContainer:
        restockContainer = Target.PromptTarget(
            ">> target your restocking container", colors["notice"]
        )

    # get container as an item class
    containerItem = Items.FindBySerial(restockContainer)
    if not containerItem:
        Misc.SendMessage(">> restocking container not found", colors["fatal"])
        return

    # open the container to load contents into memory
    if containerItem.IsContainer:
        Items.UseItem(containerItem)

    while not Player.IsGhost:
        # short pause to avoid high cpu usage
        Misc.Pause(100)

        # stop loop if gm
        if Player.GetRealSkillValue(skillName) == Player.GetSkillCap(skillName):
            Misc.SendMessage(f">> {skillName} training complete!", colors["success"])
            break

        # poison bottle
        poison_bottle = FindItem(poisonBottleID, containerItem)

        # use alchemy if no poison bottle
        if not poison_bottle:
            Misc.SendMessage(
                f">> {poisonBottle.name} not found in container", colors["status"]
            )
            Misc.SendMessage(">> attempting to create more", colors["status"])
            if Misc.ScriptStatus("train_Alchemy") is False:
                Misc.ScriptRun("train_Alchemy")
                while Misc.ScriptStatus("train_Alchemy") is True:
                    Misc.Pause(1000)
                    # break out if over 10k poison bottles
                    poison_bottle_count = FindNumberOfItems(poisonBottleID, backpack)
                    if poison_bottle_count[poisonBottleID] >= 10000:
                        break

        # apply poison
        Player.UseSkill(skillName, False)
        Target.WaitForTarget(200 + shardLatency, False)
        Target.TargetExecute(poison_bottle)
        Target.WaitForTarget(200 + shardLatency, False)
        Target.TargetExecute(poisonTarget)
        Misc.Pause(5750 + shardLatency)

        # deposit empty bottle
        empty_bottle_count = FindNumberOfItems(emptyBottleID, backpack)
        if empty_bottle_count[emptyBottleID] > 100:
            MoveItemsByCount(depositList, backpack.Serial, containerItem.Serial)


# Start Poisoning training
TrainPoisoning(poisonTarget, restockContainer)
