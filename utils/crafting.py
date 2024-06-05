# system packages
import sys
from System.Collections.Generic import List

# custom RE packages
import config
import Items, Player, Gumps, Misc
from glossary.items.containers import FindTrashBarrel
from glossary.colors import colors
from utils.items import (
    FindItem,
    FindNumberOfItems,
    MoveItem,
    MoveItemsByCount,
)
from utils.status import Overweight
from utils.actions import Chat_on_position, Sell_items
from utils.item_actions.common import RecallBank, use_runebook
from utils.pathing import IsPosition, RazorPathing


def FindTool(tools=[], container=Player.Backpack) -> None:
    """
    Searches for a crafting tool in the specified container
    """

    # find the tool to craft with
    for tool in tools:
        tool = FindItem(tool.itemID, container)
        if tool is not None:
            return tool


def GetCraftable(itemName="", craftables={}) -> None:
    if not craftables:
        Misc.SendMessage(">> no craft list found", colors["fatal"])
        return None

    craftable = craftables.get(itemName)
    if not craftable:
        Misc.SendMessage(">> no such item in craft list", colors["fatal"])
        return None
    return craftable


def HasResources(itemName, craftables={}, resourceBag=Player.Backpack) -> bool:
    if not craftables:
        Misc.SendMessage(">> no craft list found", colors["fatal"])
        return False

    craftable = craftables.get(itemName)
    if not craftable:
        Misc.SendMessage(">> no such item in craft list", colors["fatal"])
        return False

    # find current resources
    resourcesNeeded = craftable.ResourcesNeeded
    for resource, amountNeeded in resourcesNeeded.items():
        resourceName = resource.name
        resourceID = resource.itemID
        currentResources = FindNumberOfItems(resourceID, resourceBag, 0x0000)

        if currentResources.get(resourceID, 0) < amountNeeded:
            Misc.SendMessage(">> out of resource: %s" % resourceName, colors["fail"])
            Misc.SendMessage(
                ">> out of resources for item: %s" % craftable.Name, colors["fail"]
            )
            return False
    return True


def GetResourcesNeededAsItemIDs(itemName, craftables={}) -> List[int]:
    if not craftables:
        Misc.SendMessage(">> no craft list found", colors["fatal"])
        return [int]

    craftable = craftables.get(itemName)
    if not craftable:
        Misc.SendMessage(">> no such item in craft list", colors["fatal"])
        return [int]

    return [resource.itemID for resource in craftable.ResourcesNeeded.keys()]


def VendorSell(craftItemID, vendorName, sellX, sellY, runebook, runeSlot):
    if not IsPosition(sellX, sellY):
        use_runebook(runebook, runeSlot)
        Misc.Pause(config.recallDelay + config.shardLatency)

    # wait a second for NPCs to load
    Misc.Pause(1000)

    if Sell_items(vendorName, craftItemID) is False:
        Misc.SendMessage(">> encountered an error", colors["fatal"])
        sys.exit()


def Bank(runebook, bankRune, x=0, y=0):
    # recall to bank area
    if not IsPosition(x, y):
        RecallBank(runebook, bankRune)

    # path to bank if not at bank calling coordinates
    if IsPosition(x, y) is False:
        if RazorPathing(x, y) is False:
            Misc.SetSharedValue("pathFindingOverride", (x, y))
            Misc.ScriptRun("pathfinding.py")

    # use bank via chat; only does it if on bank coordinates
    Chat_on_position("bank", (x, y))


def Restock(itemList, src, dst=Player.Backpack.Serial) -> bool:
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


def DepositAndRestockForItem(
    itemName,
    skillCraftables,
    depositItems,
    containerInBank,
    restockContainer,
    runebook,
    bankRune,
    x=0,
    y=0,
):
    # use bank if enabled
    if containerInBank is not None:
        Bank(runebook, bankRune, x, y)

    # get container as an item class
    containerItem = Items.FindBySerial(restockContainer)
    if not containerItem:
        Misc.SendMessage(">> restocking container not found", colors["fatal"])
        sys.exit()

    # open the container to load contents into memory
    if containerItem.IsContainer:
        Items.UseItem(containerItem)

    # deposit items in container
    MoveItemsByCount(depositItems, Player.Backpack.Serial, restockContainer)

    # check for craftable resources in restocking container
    if HasResources(itemName, skillCraftables, containerItem) is False:
        Misc.SendMessage(">> out of resources in restocking container", colors["fatal"])
        sys.exit()
    else:
        needed = GetResourcesNeededAsItemIDs(itemName, skillCraftables)
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
    containerInBank = craftConfig.get("containerInBank", 0)
    restockContainer = craftConfig.get("restockContainer", 0)
    sellItems = craftConfig.get("sellItems", False)
    throwAwayItems = craftConfig.get("throwAwayItems", False)
    depositItems = craftConfig.get("depositItems", [])
    playerBag = craftConfig.get("playerBag", Player.Backpack)
    runebook = craftConfig.get("runebook", 0)
    bankRune = craftConfig.get("bank_rune", 1)
    houseRune = craftConfig.get("house_rune", 2)  # not in use
    vendorRune = craftConfig.get("vendor_rune", 3)
    skillName = craftConfig.get("skillName", "")
    skillGump = craftConfig.get("skillGump", 0)
    skillTools = craftConfig.get("skillTools", [])
    skillCraftables = craftConfig.get("skillCraftables", {})
    bX, bY = craftConfig.get("bankPosition", (0, 0))
    vendorName = craftConfig.get("vendorName", "")
    sX, sY = craftConfig.get("vendorPosition", (0, 0))

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
        craftable = GetCraftable(itemName, skillCraftables)
        if not craftable:
            sys.exit()

        craftItem = craftable.Item
        craftItemID = craftItem.itemID
        craftItemWeight = craftItem.weight
        craftItemMaxCountByWeight = Player.MaxWeight - 30 // craftItemWeight

        # check if we have enough resources in player bag
        if HasResources(itemName, skillCraftables, playerBag) is False:
            Misc.SendMessage(">> out of resources in player bag", colors["fail"])
            if sellItems and Items.BackpackCount(craftItemID) > 0:
                VendorSell(craftItemID, vendorName, sX, sY, runebook, vendorRune)
            DepositAndRestockForItem(
                itemName,
                skillCraftables,
                depositItems,
                containerInBank,
                restockContainer,
                runebook,
                bankRune,
                bX,
                bY,
            )

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
                VendorSell(craftItemID, vendorName, sX, sY, runebook, vendorName)
            else:
                DepositAndRestockForItem(
                    itemName,
                    skillCraftables,
                    depositItems,
                    containerInBank,
                    restockContainer,
                    runebook,
                    bankRune,
                    bX,
                    bY,
                )

        if throwAwayItems:
            # trash the crafted item if found
            foundItem = FindItem(craftItemID, Player.Backpack)
            if foundItem is not None:
                MoveItem(Items, Misc, foundItem, trashBarrel)

    if Player.GetRealSkillValue(skillName) == Player.GetSkillCap(skillName):
        Misc.SendMessage(f">> maxed out {skillName} skill", colors["notice"])
        return
