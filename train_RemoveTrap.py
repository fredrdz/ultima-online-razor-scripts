"""
SCRIPT: train_Poisoning.py
Author: Talik Starr
IN:RISEN
Skill: Poisoning
"""

# custom RE packages
import Gumps, Items, Player, Misc, Target
from config import shardLatency
from glossary.colors import colors
from glossary.items.tools import tools
from glossary.items.potions import potions
from utils.items import FindItem, FindNumberOfItems, MoveItemsByCount

# ---------------------------------------------------------------------
# init
skillName = "Remove Trap"
poisonBottle = potions["lesser poison potion"]
poisonBottleID = poisonBottle.itemID
tinkerTool = tools["tinker's tools"]
tinkerToolID = tinkerTool.itemID
backpack = Player.Backpack
trapTarget = 0x40033DEE  # wooden box serial
restockContainer = 0x40125C18  # restock container serial
restockList = [(poisonBottleID, 100)]
# ---------------------------------------------------------------------


# use remove trap skill on target
def RemoveTrap(trapTarget):
    Player.UseSkill(skillName, False)
    Target.WaitForTarget(2000 + shardLatency, False)
    Target.TargetExecute(trapTarget)


def TrainRemoveTrap(trapTarget, restockContainer):
    """
    Trains Remove Trap to the skill cap
    """
    # init
    Journal.Clear()

    # check poison trap target and it's locking key
    if not trapTarget:
        trapTarget = Target.PromptTarget(
            ">> Select the container you will be trapping:", colors["notice"]
        )

    # check restock container
    if not restockContainer:
        restockContainer = Target.PromptTarget(
            ">> Select your restocking container:", colors["notice"]
        )

    # get container as an item class
    restock_container = Items.FindBySerial(restockContainer)
    if not restock_container:
        Misc.SendMessage(">> restocking container not found", colors["fatal"])
        return

    # open the container to load contents into memory
    if restock_container.IsContainer:
        Items.UseItem(restock_container)

    # loop until skill cap
    while not Player.IsGhost:
        # short pause to avoid high cpu usage
        Misc.Pause(100)

        # stop loop if gm
        if Player.GetRealSkillValue(skillName) == Player.GetSkillCap(skillName):
            Misc.SendMessage(f">> {skillName} training complete!", colors["success"])
            break

        # tinker tool
        tinker_tool = FindItem(tinkerToolID, backpack)

        if not tinker_tool:
            Misc.SendMessage(
                f">> {tinkerTool.name} not found in backpack, exiting..",
                colors["status"],
            )
            break

        # poison bottle in restock container
        poison_bottle = FindItem(poisonBottleID, restock_container)

        # stop if no poison in restock container
        if not poison_bottle:
            Misc.SendMessage(
                f">> {poisonBottle.name} not found in restock container",
                colors["status"],
            )
            break

        # check poison bottle count in player backpack
        poison_bottle_count = FindNumberOfItems(poisonBottleID, backpack)
        if poison_bottle_count[poisonBottleID] <= 0:
            MoveItemsByCount(restockList, restock_container.Serial, backpack.Serial)

        # apply poison trap
        tinker_gump = 949095101
        Items.UseItem(tinker_tool)
        Gumps.WaitForGump(tinker_gump, 10000)
        Gumps.SendAction(tinker_gump, 50)  # click Traps
        Gumps.WaitForGump(tinker_gump, 10000)
        Gumps.SendAction(tinker_gump, 9)  # click Poison Trap
        # restart loop if we encounter issues
        Target.WaitForTarget(5000 + shardLatency, False)
        if not Journal.WaitJournal("What would you like to set a trap on?", 5000):
            Journal.Clear()
            Gumps.CloseGump(tinker_gump)
            continue
        # no issues so trap container
        Target.TargetExecute(trapTarget)  # select container
        Gumps.WaitForGump(tinker_gump, 10000)
        gump_text_options = Gumps.LastGumpGetLineList()
        if gump_text_options:
            gump_text_options = [str(line) for line in gump_text_options]

            if (
                "You failed to create the item, and some of your materials are lost."
                in gump_text_options
            ):
                Gumps.CloseGump(tinker_gump)
                Misc.SendMessage(
                    ">> failed to set the trap, going again...", colors["fail"]
                )
                continue
            elif "Trap is disabled until you lock the chest." in gump_text_options:
                Gumps.CloseGump(tinker_gump)
            elif (
                "You can only place one trap on an object at a time."
                in gump_text_options
            ):
                Gumps.CloseGump(tinker_gump)

        # journal checks
        if Journal.Search("What would you like to set a trap on?"):
            Journal.Clear()
            Target.TargetExecute(trapTarget)

        while not Journal.Search("You successfully render the trap harmless."):
            if Journal.Search("That doesn't appear to be trapped."):
                Journal.Clear()
                break
            RemoveTrap(trapTarget)
            Misc.Pause(6000 + shardLatency)


# Start Poisoning training
TrainRemoveTrap(trapTarget, restockContainer)
