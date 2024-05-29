"""
SCRIPT: train_Fletching.py
Author: Talik Starr
IN:RISEN
Skill: Fletching
"""

# system packages
import sys

# custom RE packages
import config
import Items, Player, Gumps, Misc, Target
from glossary.items.containers import FindTrashBarrel
from glossary.crafting.fletching import (
    HasResources,
    GetCraftable,
    fletchingTools,
    fletchingGump,
)
from glossary.colors import colors
from utils.items import (
    FindItem,
    FindNumberOfItems,
    MoveItem,
    MoveItemsByCount,
    RestockAgent,
    EnableSellingAgent,
)
from utils.status import Overweight
from utils.actions import Chat_on_position, Sell_items
from utils.item_actions.common import RecallBank, use_runebook
from utils.pathing import IsPosition, RazorPathing

# ---------------------------------------------------------------------
# script configuration; modify these per your requirements

# map x/y coordinates
vendorName = "Lazarus"
sellX = 1470
sellY = 1581
bankX = 1424
bankY = 1683

# slot number in runebook, 1 of 16
bank_rune = 1
vendor_rune = 3

# bank restocking and depositing config
playerBag = Player.Backpack.Serial
bankBag = 0x40054709
goldID = 0x0EED
bankDepositItems = [
    (goldID, -1),
]

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


def VendorSell(craftItemID):
    if not IsPosition(sellX, sellY):
        use_runebook(runebook_serial, vendor_rune)
        Misc.Pause(config.recallDelay + config.shardLatency)

    # wait a second for NPCs to load
    Misc.Pause(1000)

    if Sell_items(vendorName, craftItemID) is False:
        Misc.SendMessage(">> encountered an error", colors["fatal"])
        sys.exit()


def Bank(x=0, y=0):
    if IsPosition(x, y) is False:
        if RazorPathing(x, y) is False:
            Misc.SetSharedValue("pathFindingOverride", (x, y))
            Misc.ScriptRun("pathfinding.py")

    Chat_on_position("bank", (x, y))


def Restock():
    RestockAgent("fletching")
    RestockAgent("recall")


def BankDepositAndRestockForItem(itemName, x=0, y=0):
    # go to the bank
    if not IsPosition(x, y):
        RecallBank(runebook_serial, bank_rune)
    # use bank
    Bank(bankX, bankY)
    # deposit items in bank bag
    MoveItemsByCount(bankDepositItems, playerBag, bankBag)
    # get bank bag as an item class
    bankBagAsItem = Items.FindBySerial(bankBag)
    if bankBagAsItem.IsInBank is False:
        Misc.SendMessage(">> bank bag not in bank", colors["fatal"])
        sys.exit()
    # check for craftable item resources in bank bag; restock
    if HasResources(itemName, bankBagAsItem) is False:
        Misc.SendMessage(">> out of resources in bank bag", colors["fatal"])
        sys.exit()
    else:
        Restock()


def TrainFletching(throwAwayItems=True):
    """
    Trains Fletching to its skill cap
    """

    tool = FindTool(Player.Backpack)
    if tool is None:
        Misc.SendMessage(">> no tools to train with", colors["fatal"])
        return

    trashBarrel = None
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
        itemName = str("")
        if Player.GetSkillValue("Fletching") < 60.0:
            itemName = str("bow")
        elif Player.GetSkillValue("Fletching") < 80.0:
            itemName = str("crossbow")
        elif Player.GetSkillValue("Fletching") < 100:
            itemName = str("heavy crossbow")

        # set craftable item parameters
        craftable = GetCraftable(itemName)
        craftItem = craftable.Item
        craftItemID = craftItem.itemID
        craftItemWeight = craftItem.weight
        craftItemMaxCountByWeight = Player.MaxWeight - 30 // craftItemWeight

        # check if we have enough resources in player backpack
        if HasResources(itemName) is False:
            Misc.SendMessage(">> out of resources in player bag", colors["fail"])
            if Items.BackpackCount(craftItemID) > 0:
                VendorSell(craftItemID)
            BankDepositAndRestockForItem(itemName, bankX, bankY)

        Items.UseItem(tool)

        # craft the item
        for path in craftable.GumpPath:
            Gumps.WaitForGump(path.GumpID, 5000)
            Gumps.SendAction(path.GumpID, path.ButtonID)

        # wait for crafting to finish and close the gump
        Gumps.WaitForGump(fletchingGump, 5000)
        Gumps.SendAction(fletchingGump, 0)

        itemCount = FindNumberOfItems(craftItemID, Player.Backpack)
        if not throwAwayItems:
            if (
                Overweight(Player.MaxWeight + 30)
                or itemCount[craftItemID] > craftItemMaxCountByWeight
            ):
                VendorSell(craftItemID)
        else:
            foundItem = FindItem(craftItemID, Player.Backpack)
            if foundItem is not None:
                MoveItem(Items, Misc, foundItem, trashBarrel)

    if Player.GetRealSkillValue("Fletching") == Player.GetSkillCap("Fletching"):
        Misc.SendMessage(">> maxed out fletching skill", colors["notice"])
        return


# Start Cartography training
EnableSellingAgent("fletching")
TrainFletching(throwAwayItems=False)
