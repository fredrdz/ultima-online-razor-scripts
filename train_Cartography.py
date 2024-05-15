"""
SCRIPT: train_Cartography.py
Author: Talik Starr
IN:RISEN
Skill: Cartography
"""

from glossary.items.containers import FindTrashBarrel
from glossary.items.miscellaneous import miscellaneous
from glossary.crafting.cartography import cartographyTools, cartographyCraftables
from glossary.colors import colors
from utils.items import FindItem, FindNumberOfItems, MoveItem
from utils.status import Overweight
from utils.actions import Sell_items


def FindTool(container):
    """
    Searches for a mapmaking tool in the specified container
    """

    # find the tool to craft with
    for tool in cartographyTools:
        tool = FindItem(tool.itemID, container)
        if tool is not None:
            return tool


def TrainCartography(throwAwayMaps=True):
    """
    Trains Cartography to its skill cap
    """

    if Player.GetRealSkillValue("Cartography") == Player.GetSkillCap("Cartography"):
        Misc.SendMessage(">> maxed out cartography skill", colors["notice"])
        return

    tool = FindTool(Player.Backpack)
    if tool is None:
        Misc.SendMessage(">> no tools to train with", colors["fatal"])
        return

    if throwAwayMaps:
        trashBarrel = FindTrashBarrel(Items)
        if trashBarrel is None:
            Misc.SendMessage(">> no trash barrel nearby...", colors["fatal"])
            Misc.SendMessage(
                ">> move closer to one to throw away maps", colors["fatal"]
            )
            return

    while not Player.IsGhost and Player.GetRealSkillValue("Cartography") < 95.5:
        # make sure the tool isn't broken. If it is broken, this will return None
        tool = Items.FindBySerial(tool.Serial)
        if tool is None:
            tool = FindTool(Player.Backpack)
            if tool is None:
                Misc.SendMessage(">> no tools to train with", colors["fatal"])
                return

        # select the item to craft
        itemToCraft = None
        if Player.GetSkillValue("Cartography") < 50.0:
            itemToCraft = cartographyCraftables["local map"]
        elif Player.GetSkillValue("Cartography") < 65.0:
            itemToCraft = cartographyCraftables["city map"]
        elif Player.GetSkillValue("Cartography") < 100:
            itemToCraft = cartographyCraftables["world map"]

        blankScrolls = FindNumberOfItems(
            miscellaneous["blank scroll"].itemID, Player.Backpack, 0x0000
        )
        if (
            blankScrolls[miscellaneous["blank scroll"].itemID]
            < itemToCraft.resourcesNeeded["blank scroll"]
        ):
            Misc.SendMessage(">> out of resources", colors["fatal"])
            return

        Items.UseItem(tool)
        for path in itemToCraft.gumpPath:
            Gumps.WaitForGump(path.gumpID, 2000)
            Gumps.SendAction(path.gumpID, path.buttonID)

        # wait for crafting to finish and close the gump
        Gumps.WaitForGump(949095101, 2000)
        Gumps.SendAction(949095101, 0)

        if not throwAwayMaps and Overweight(Player.MaxWeight + 30):
            Sell_items(miscellaneous["map"].itemID)
        else:
            map = FindItem(miscellaneous["map"].itemID, Player.Backpack)
            if map is not None and throwAwayMaps:
                MoveItem(Items, Misc, map, trashBarrel)


# Start Cartography training
TrainCartography(throwAwayMaps=True)
