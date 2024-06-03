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
    GetResourcesNeededAsItemIDs,
    HasResources,
    GetCraftable,
    fletchName,
    fletchingGump,
    fletchingTools,
)
from glossary.colors import colors
from utils.items import (
    FindItem,
    FindNumberOfItems,
    MoveItem,
    MoveItemsByCount,
    EnableSellingAgent,
)
from utils.status import Overweight
from utils.actions import Chat_on_position, Sell_items
from utils.item_actions.common import RecallBank, use_runebook
from utils.pathing import IsPosition, RazorPathing

# ---------------------------------------------------------------------
# script configuration; modify these per your requirements

# setting a secure container will disable bank restocking
# will restock from here instead
secureContainer = 0x40125C18
throwAwayItems = False
sellItems = False

# vendor selling parameters
vendorName = "Slade"
sellX = 1470
sellY = 1581

# slot number in runebook, 1 of 16
bank_rune = 1
house_rune = 2
vendor_rune = 3

# bank parameters
bankX = 1424
bankY = 1683
containerInBank = 0x40054709

# items to deposit in bank bag or secure container
# a list of tuples containing itemID and count
depositItems = [
    (0x0EED, -1),  # gold
    (0x0DE1, -1),  # kindling
]

craftConfig = {
    "sellItems": sellItems,
    "throwAwayItems": throwAwayItems,
    "bankPosition": (bankX, bankY),
    "vendorName": vendorName,
    "vendorPosition": (sellX, sellY),
    # skill settings
    "skillName": fletchName,
    "skillGump": fletchingGump,
    "skillTools": fletchingTools,
    # skill path to use: "skill" or "profit"
    "usePath": "skill",
    # a dictionary of skill paths and their values
    # define what item names to craft and up to which maximum skill value
    "paths": {
        "skill": {"kindling": 100.0},
        "profit": {
            "bow": 60.0,
            "crossbow": 80.0,
            "heavy crossbow": 100.0,
        },
    },
}

# ---------------------------------------------------------------------
# do not edit below this line

# init
playerBag = Player.Backpack.Serial

# check for runebook
if not Misc.CheckSharedValue("young_runebook"):
    Misc.ScriptRun("_startup.py")
if Misc.CheckSharedValue("young_runebook"):
    runebook_serial = Misc.ReadSharedValue("young_runebook")
else:
    runebook_serial = Target.PromptTarget(">> target your runebook", colors["notice"])

# check what type of restock container we're using;
# only one instance of secureContainer or containerInBank may exist;
# not both; one will be set to None
if secureContainer is not None:
    # secure container was specified; use it
    restockContainer = secureContainer
    containerInBank = None
elif containerInBank is not None:
    # container in bank was specified; use it
    restockContainer = containerInBank
else:
    # no container was specified; prompt for one
    restockContainer = Target.PromptTarget(
        ">> target your restocking container", colors["notice"]
    )
    containerAsItem = Items.FindBySerial(restockContainer)
    # check if container is in bank
    if containerAsItem.IsInBank is False:
        Misc.SendMessage(f">> {containerAsItem.Name} was not in bank", colors["status"])
        secureContainer = restockContainer
        containerInBank = None
    else:
        Misc.SendMessage(f">> {containerAsItem.Name} was in bank", colors["status"])
        containerInBank = restockContainer
        secureContainer = None


# ---------------------------------------------------------------------
# script functions


def FindTool(tools=[], container=Player.Backpack):
    """
    Searches for a crafting tool in the specified container
    """

    # find the tool to craft with
    for tool in tools:
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
    # recall to bank area
    if not IsPosition(x, y):
        RecallBank(runebook_serial, bank_rune)

    # path to bank if not at bank calling coordinates
    if IsPosition(x, y) is False:
        if RazorPathing(x, y) is False:
            Misc.SetSharedValue("pathFindingOverride", (x, y))
            Misc.ScriptRun("pathfinding.py")

    # use bank via chat; only does it if on bank coordinates
    Chat_on_position("bank", (x, y))


def Restock(itemList, src, dst=Player.Backpack.Serial):
    if not itemList:
        Misc.Message(">> no items requested for restock", colors["fatal"])
        return False

    if src is None or not isinstance(src, int):
        Misc.Message(">> no source container specified", colors["fatal"])
        return False

    difference = []
    for id, required_count in itemList:
        src_count = Items.ContainerCount(src, id)
        if src_count < required_count:
            return False

        dst_count = Items.BackpackCount(id)
        if dst_count < required_count:
            difference.append((id, required_count - dst_count))

    if not difference:
        Misc.Message(">> no items need restocking", colors["success"])
        return True

    MoveItemsByCount(difference, src, dst)
    return True


def DepositAndRestockForItem(itemName, x=0, y=0):
    # use bank if enabled
    if containerInBank is not None:
        Bank(x, y)

    # get container as an item class
    containerItem = Items.FindBySerial(restockContainer)
    if not containerItem:
        Misc.SendMessage(">> restocking container not found", colors["fatal"])
        sys.exit()

    # open the container to load contents into memory
    if containerItem.IsContainer:
        Items.UseItem(containerItem)

    # deposit items in container
    MoveItemsByCount(depositItems, playerBag, restockContainer)

    # check for craftable resources in restocking container
    if HasResources(itemName, containerItem) is False:
        Misc.SendMessage(">> out of resources in restocking container", colors["fatal"])
        sys.exit()
    else:
        needed = GetResourcesNeededAsItemIDs(itemName)
        restockItems = []
        for itemID in needed:
            restockItems.append((itemID, 100))
        if Restock(restockItems, restockContainer) is False:
            Misc.SendMessage(">> failed to restock necessary items", colors["fatal"])
            sys.exit()


def TrainCraftSkill(
    craftConfig={},
):
    """
    Trains a craft skill to its skill cap
    """
    sellItems = craftConfig.get("sellItems", False)
    throwAwayItems = craftConfig.get("throwAwayItems", False)
    skillName = craftConfig.get("skillName", "")
    skillGump = craftConfig.get("skillGump", 0)
    skillTools = craftConfig.get("skillTools", [])
    bX, bY = craftConfig.get("bankPosition", (0, 0))

    tool = FindTool(skillTools, Player.Backpack)
    if tool is None:
        Misc.SendMessage(f">> no {skillName} tools to train with", colors["fatal"])
        return

    trashBarrel = None
    if throwAwayItems:
        trashBarrel = FindTrashBarrel()
        if trashBarrel is None:
            Misc.SendMessage(">> no trash barrel nearby...", colors["fatal"])
            Misc.SendMessage(
                ">> move closer to one to throw away crafted items", colors["fatal"]
            )
            return

    while not Player.IsGhost and Player.GetRealSkillValue(
        skillName
    ) < Player.GetSkillCap(skillName):
        # make sure the tool isn't broken. If it is broken, this will return None
        tool = Items.FindBySerial(tool.Serial)
        if tool is None:
            tool = FindTool(skillTools, Player.Backpack)
            if tool is None:
                Misc.SendMessage(
                    f">> no {skillName} tools to train with", colors["fatal"]
                )
                return

        # set item name to craft based on the skill path chosen and current skill value
        itemName = ""
        currentSkillValue = Player.GetSkillValue(skillName)

        pathName = craftConfig["usePath"]

        if pathName in craftConfig["paths"]:
            for name, maxSkill in craftConfig["paths"][pathName].items():
                if currentSkillValue < maxSkill:
                    itemName = name
                    break

        # set craftable item parameters
        craftable = GetCraftable(itemName)
        if not craftable:
            sys.exit()

        craftItem = craftable.Item
        craftItemID = craftItem.itemID
        craftItemWeight = craftItem.weight
        craftItemMaxCountByWeight = Player.MaxWeight - 30 // craftItemWeight

        # check if we have enough resources in player backpack
        if HasResources(itemName) is False:
            Misc.SendMessage(">> out of resources in player bag", colors["fail"])
            if sellItems and Items.BackpackCount(craftItemID) > 0:
                VendorSell(craftItemID)
            DepositAndRestockForItem(itemName, bX, bY)

        Items.UseItem(tool)

        # craft the item
        for path in craftable.GumpPath:
            Gumps.WaitForGump(path.GumpID, 3000)
            Gumps.SendAction(path.GumpID, path.ButtonID)

        # wait for crafting to finish and close the gump
        Gumps.WaitForGump(skillGump, 10000)
        Gumps.SendAction(skillGump, 0)

        itemCount = FindNumberOfItems(craftItemID, Player.Backpack)
        # sell the crafted item if player is overweight or has too many
        if (
            Overweight(Player.MaxWeight + 30)
            or itemCount[craftItemID] > craftItemMaxCountByWeight
        ):
            if sellItems:
                VendorSell(craftItemID)
            else:
                DepositAndRestockForItem(itemName, bX, bY)

        if throwAwayItems:
            # trash the crafted item if found
            foundItem = FindItem(craftItemID, Player.Backpack)
            if foundItem is not None:
                MoveItem(Items, Misc, foundItem, trashBarrel)

    if Player.GetRealSkillValue(skillName) == Player.GetSkillCap(skillName):
        Misc.SendMessage(f">> maxed out {skillName} skill", colors["notice"])
        return


# ---------------------------------------------------------------------
# main script process

EnableSellingAgent("fletching")
TrainCraftSkill(craftConfig)
