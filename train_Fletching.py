"""
SCRIPT: train_Fletching.py
Author: Talik Starr
IN:RISEN
Skill: Fletching
"""

import config
import Items, Player, Gumps, Misc, Target
from glossary.items.containers import FindTrashBarrel
from glossary.crafting.fletching import (
    CheckResources,
    GetCraftable,
    fletchingTools,
    fletchingGump,
)
from glossary.colors import colors
from utils.items import FindItem, FindNumberOfItems, MoveItem, RestockAgent
from utils.status import Overweight
from utils.actions import Chat_on_position, Sell_items
from utils.item_actions.common import RecallBank, use_runebook
from utils.pathing import Position, RazorPathing, get_position

# ---------------------------------------------------------------------
# script configuration; modify these per your requirements

# map x/y coordinates
vendorName = "Vendor"
sellX = None
sellY = None
bankX = None
bankY = None

# slot number in runebook, 1 of 16
bank_rune = 1
vendor_rune = 4

# ---------------------------------------------------------------------
# do not edit below this line
if not Misc.CheckSharedValue("young_runebook"):
    Misc.ScriptRun("_startup.py")

if Misc.CheckSharedValue("young_runebook"):
    runebook_serial = Misc.ReadSharedValue("young_runebook")
else:
    runebook_serial = Target.PromptTarget(">> target your runebook", colors["notice"])


def FindTool(container):
    """
    Searches for a fletching tool in the specified container
    """

    # find the tool to craft with
    for tool in fletchingTools:
        tool = FindItem(tool.itemID, container)
        if tool is not None:
            return tool


def Bank(x=0, y=0):
    if x == 0 or y == 0:
        bank_position = get_position("no bank configured...")
    else:
        bank_position = Position(int(x), int(y))

    if not RazorPathing(bank_position.X, bank_position.Y):
        Misc.SetSharedValue("pathFindingOverride", (bank_position.X, bank_position.Y))
        Misc.ScriptRun("pathfinding.py")
    Chat_on_position("bank", bank_position)


def Restock():
    RestockAgent("fletching")
    Misc.Pause(3000)

    RestockAgent("recall")
    Misc.Pause(3000)


def TrainFletching(throwAwayItems=True):
    """
    Trains Fletching to its skill cap
    """

    tool = FindTool(Player.Backpack)
    if tool is None:
        Misc.SendMessage(">> no tools to train with", colors["fatal"])
        return

    if throwAwayItems:
        trashBarrel = FindTrashBarrel()
        if trashBarrel is None:
            Misc.SendMessage(">> no trash barrel nearby...", colors["fatal"])
            Misc.SendMessage(
                ">> move closer to one to throw away maps", colors["fatal"]
            )
            return

    while not Player.IsGhost and Player.GetRealSkillValue("Fletching") < 100.0:
        # make sure the tool isn't broken. If it is broken, this will return None
        tool = Items.FindBySerial(tool.Serial)
        if tool is None:
            tool = FindTool(Player.Backpack)
            if tool is None:
                Misc.SendMessage(">> no tools to train with", colors["fatal"])
                return

        # select the item to craft
        if Player.GetSkillValue("Fletching") < 50.0:
            itemName = "shafts"
        elif Player.GetSkillValue("Fletching") < 65.0:
            itemName = "bow"
        elif Player.GetSkillValue("Fletching") < 100:
            itemName = "xbow"

        # check if we have enough resources to craft the item
        if CheckResources(itemName) is False:
            return

        Items.UseItem(tool)
        for path in itemToCraft.gumpPath:
            Gumps.WaitForGump(path.gumpID, 2000)
            Gumps.SendAction(path.gumpID, path.buttonID)

        # wait for crafting to finish and close the gump
        Gumps.WaitForGump(fletchingGump, 2000)
        Gumps.SendAction(fletchingGump, 0)

        craftItemID = GetCraftable(itemName).Item.itemID
        itemCount = FindNumberOfItems(craftItemID, Player.Backpack)
        if not throwAwayItems:
            if Overweight(Player.MaxWeight) or itemCount[craftItemID] > 100:
                use_runebook(runebook_serial, vendor_rune)
                Misc.Pause(config.recallDelay + config.shardLatency)
                Sell_items(vendorName, craftItemID, sellX, sellY)
                RecallBank(runebook_serial, bank_rune)
                Bank(bankX, bankY)
                Restock()
        else:
            foundItem = FindItem(craftItemID, Player.Backpack)
            if foundItem is not None:
                MoveItem(Items, Misc, foundItem, trashBarrel)

    if Player.GetRealSkillValue("Fletching") == Player.GetSkillCap("Fletching"):
        Misc.SendMessage(">> maxed out fletching skill", colors["notice"])
        return


# Start Cartography training
TrainFletching(throwAwayItems=False)
