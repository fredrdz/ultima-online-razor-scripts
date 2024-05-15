"""
SCRIPT: train_Carpentry.py
Author: Talik Starr
IN:RISEN
Skill: Carpentry
"""

import config
from glossary.colors import colors
from glossary.crafting.carpentry import FindCarpentryTool, carpentryCraftables
from glossary.items.containers import FindTrashBarrel
from utils.items import FindItem, FindNumberOfItems, MoveItem

# Set to serial of bag or 'pet' for the mount that you are on
# Set to None if you don't want to keep slayers
slayerBag = "pet"
petName = "Packy"


def FindPet(name):
    """
    Finds pet to use for storage
    """

    petFilter = Mobiles.Filter()
    petFilter.Enabled = True
    petFilter.RangeMin = 0
    petFilter.RangeMax = 1
    petFilter.Name = name

    pet = Mobiles.ApplyFilter(petFilter)[0]
    return pet


def TrainCarpentry():
    """
    Trains Carpentry to its skill cap
    """

    if Player.GetRealSkillValue("Carpentry") == Player.GetSkillCap("Carpentry"):
        Misc.SendMessage(">> maxed out carpentry skill", colors["notice"])
        return

    tool = FindCarpentryTool(Player.Backpack)
    if tool is None:
        Misc.SendMessage(">> no tools to train with", colors["fatal"])
        return

    trashBarrel = FindTrashBarrel(Items)
    if trashBarrel is None:
        Misc.SendMessage(">> no trash barrel nearby...", colors["fatal"])
        Misc.SendMessage(">> move closer to one to throw away maps", colors["fatal"])
        return

    Journal.Clear()
    while not Player.IsGhost and Player.GetRealSkillValue(
        "Carpentry"
    ) < Player.GetSkillCap("Carpentry"):
        # make sure the tool isn't broken. If it is broken, this will return None
        tool = Items.FindBySerial(tool.Serial)
        if tool is None:
            tool = FindCarpentryTool(Player.Backpack)
            if tool is None:
                Misc.SendMessage(">> no tools to train with", colors["fatal"])
                break

        # select the item to craft
        itemToCraft = None
        if Player.GetRealSkillValue("Carpentry") < 40.0:
            Misc.SendMessage(">> skill too low...", colors["fatal"])
            Misc.SendMessage(">> use gold to train with an NPC", colors["fatal"])
            break
        elif Player.GetRealSkillValue("Carpentry") < 70.0:
            itemToCraft = carpentryCraftables["club"]
        elif Player.GetRealSkillValue("Carpentry") < 100.0:
            itemToCraft = carpentryCraftables["blank scroll"]

        enoughResourcesToCraftWith = True
        numberOfItems = {}
        for resource in itemToCraft.resourcesNeeded:
            if resource == "boards":
                numberOfBoards = FindNumberOfItems(0x1BD7, Player.Backpack, 0x0000)[
                    0x1BD7
                ]
                numberOfBoards += FindNumberOfItems(0x1BDD, Player.Backpack, 0x0000)[
                    0x1BDD
                ]
                if numberOfBoards < itemToCraft.resourcesNeeded["boards"]:
                    enoughResourcesToCraftWith = False
                    break
            elif resource == "cloth":
                numberOfItems["cloth"] = FindNumberOfItems(
                    0x1766, Player.Backpack, 0x0000
                )[0x1766]
                if numberOfItems["cloth"] < itemToCraft.resourcesNeeded["cloth"]:
                    enoughResourcesToCraftWith = False
                    break
            elif resource == "spider's silk":
                numberOfItems["spider's silk"] = FindNumberOfItems(
                    0x0F8D, Player.Backpack, 0x0000
                )[0x0F8D]
                if (
                    numberOfItems["spider's silk"]
                    < itemToCraft.resourcesNeeded["spider's silk"]
                ):
                    enoughResourcesToCraftWith = False
                    break

        if not enoughResourcesToCraftWith:
            Misc.SendMessage(">> out of resources", colors["fatal"])
            return

        Items.UseItem(tool)
        for path in itemToCraft.gumpPath:
            Gumps.WaitForGump(path.gumpID, 2000)
            Gumps.SendAction(path.gumpID, path.buttonID)

        # close the Carpentry gump (signals that crafting has completed, since the gump will have reopened)
        Gumps.WaitForGump(itemToCraft.gumpPath[0].gumpID, 5000)
        Gumps.SendAction(itemToCraft.gumpPath[0].gumpID, 0)

        # wait a moment for the item to appear in the player's backpack
        Misc.Pause(200)

        # move the item out of the player's backpack
        itemType = None
        if itemToCraft.name == "club":
            itemType = 0x13B4
        elif itemToCraft.name == "blank scroll":
            itemType = 0x0EF3
        item = FindItem(itemType, Player.Backpack)

        if item is None:
            if slayerBag != None and Journal.SearchByType(
                "You have successfully crafted a slayer", "Regular"
            ):
                Journal.Clear()
                if slayerBag == "pet":
                    pet = FindPet()
                    MoveItem(Items, Misc, item, pet.Backpack)
                    Misc.Pause(config.dragDelayMilliseconds)
                else:
                    MoveItem(Items, Misc, item, slayerBag)
            else:
                MoveItem(Items, Misc, item, trashBarrel)


# start Carpentry training
TrainCarpentry()
