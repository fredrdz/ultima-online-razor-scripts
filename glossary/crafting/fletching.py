from glossary.colors import colors
from glossary.crafting.craftable import Craftable
from glossary.items import weapons
from utils.items import FindItem, FindNumberOfItems
from glossary.items.tools import tools
from glossary.items.boards import boards
from glossary.items.logs import logs
from utils.gumps import GumpSelection

fletchingGump = None
fletchingTools = [tools["tinker's tools"], tools["tool kit"]]


def FindFletchingTool(container):
    """
    Searches for a fletching tool in the specified container
    """

    global fletchingTools

    # Find the tool to craft with
    for tool in fletchingTools:
        tool = FindItem(tool.itemID, container)
        if tool is not None:
            return tool


class FletchingCraftable(Craftable):
    def __init__(
        self, Name, Item, RetainsMark, RetainsColor, MinSkill, ResourcesNeeded, GumpPath
    ):
        self.Name = Name
        self.Item = Item
        self.RetainsMark = RetainsMark
        self.RetainsColor = RetainsColor
        self.MinSkill = MinSkill
        self.ResourcesNeeded = ResourcesNeeded
        self.GumpPath = GumpPath

        # call the parent class's constructor using super()
        super().__init__(Name, MinSkill, ResourcesNeeded, GumpPath)


def GetCraftable(itemName):
    itemToCraft = fletchingCraftables[itemName]
    if itemToCraft is None:
        Misc.SendMessage(">> no such item in craft list", colors["fatal"])
        return None
    return itemToCraft


def CheckResources(itemName):
    itemToCraft = fletchingCraftables[itemName]
    if itemToCraft is None:
        Misc.SendMessage(">> no such item in craft list", colors["fatal"])
        return False

    # find current resources
    resourcesNeeded = itemToCraft.ResourcesNeeded
    for resource, amountNeeded in resourcesNeeded.items():
        itemID = resource.itemID
        currentResources = FindNumberOfItems(itemID, Player.Backpack, 0x0000)

        if currentResources.get(itemID, 0) < amountNeeded:
            Misc.SendMessage(
                ">> out of resources for %s" % itemToCraft.Name, colors["fatal"]
            )
            return False
    return True


fletchingCraftables = {
    ### Weapons: Gump Button 1 ###
    "bow": FletchingCraftable(
        Name="bow",
        Item=weapons["bow"],
        RetainsMark=True,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={boards["ordinary board"]: 4},
        GumpPath=(GumpSelection(fletchingGump, 1), GumpSelection(fletchingGump, 2)),
    ),
}
