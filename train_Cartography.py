"""
SCRIPT: train_Cartography.py
Author: Talik Starr
IN:RISEN
Skill: Cartography
TODO: use new utils/glossary changes, currently broken
"""

import config
import Gumps, Items, Player, Misc
from glossary.items.containers import FindTrashBarrel
from glossary.items.miscellaneous import miscellaneous
from glossary.crafting.cartography import cartographyTools, cartographyCraftables
from glossary.colors import colors
from utils.items import FindItem, FindNumberOfItems, MoveItem, RestockAgent
from utils.status import Overweight
from utils.actions import Chat_on_position, Sell_items
from utils.item_actions.common import RecallBank, use_runebook
from utils.pathing import Position, RazorPathing, Get_position

character_name = "Talik Starr"
young_runebook_serial = config.characters[character_name]["young_runebook"]["serial"]
bank_rune = config.characters[character_name]["young_runebook"]["bank_rune_slot"]
vendor_rune = 4  # slot number in runebook, 1 of 16

# map x/y coordinates
vendorName = "Gage"
sellX = 1417
sellY = 1755
bankX = 3699
bankY = 2520


def FindTool(container):
    """
    Searches for a mapmaking tool in the specified container
    """

    # find the tool to craft with
    for tool in cartographyTools:
        tool = FindItem(tool.itemID, container)
        if tool is not None:
            return tool


def Bank(x=0, y=0):
    if x == 0 or y == 0:
        bank_position = Get_position("no bank configured...")
    else:
        bank_position = Position(int(x), int(y))

    if not RazorPathing(bank_position.X, bank_position.Y):
        Misc.SetSharedValue("pathFindingOverride", (bank_position.X, bank_position.Y))
        Misc.ScriptRun("pathfinding.py")
    Chat_on_position("bank", bank_position)


def Restock():
    RestockAgent("cartography")
    Misc.Pause(3000)

    RestockAgent("recall")
    Misc.Pause(3000)


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

    trashBarrel = None
    if throwAwayMaps:
        trashBarrel = FindTrashBarrel()
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
        for path in itemToCraft.GumpPath:
            Gumps.WaitForGump(path.GumpID, 2000)
            Gumps.SendAction(path.GumpID, path.ButtonID)

        # wait for crafting to finish and close the gump
        Gumps.WaitForGump(949095101, 2000)
        Gumps.SendAction(949095101, 0)

        mapID = miscellaneous["map"].itemID
        items = FindNumberOfItems(mapID, Player.Backpack)
        if not throwAwayMaps:
            if Overweight(Player.MaxWeight) or items[mapID] > 100:
                # use_runebook(young_runebook_serial, vendor_rune)
                # Misc.Pause(config.recallDelay + config.shardLatency)
                Sell_items((sellX, sellY), vendorName, mapID)
                # RecallBank(young_runebook_serial, bank_rune)
                # Bank(bankX, bankY)
                # Restock()
        else:
            map = FindItem(mapID, Player.Backpack)
            if map is not None and throwAwayMaps:
                MoveItem(Items, Misc, map, trashBarrel)


# Start Cartography training
TrainCartography(throwAwayMaps=False)
