import Player, Misc
from glossary.colors import colors
from glossary.crafting.craftable import Craftable
from glossary.items.weapons import weapons
from glossary.items.miscellaneous import miscellaneous
from utils.items import FindItem, FindNumberOfItems
from glossary.items.tools import tools
from glossary.items.boards import boards
from glossary.items.logs import logs
from utils.gumps import GumpSelection

fletchingGump = 949095101
fletchingTools = [tools["arrow fletching"]]


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


def GetCraftable(itemName=str("")):
    craftable = fletchingCraftables[itemName]
    if craftable is None:
        Misc.SendMessage(">> no such item in craft list", colors["fatal"])
        return None
    return craftable


def HasResources(itemName, resourceBag=Player.Backpack):
    craftable = fletchingCraftables[itemName]
    if craftable is None:
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


fletchingCraftables = {
    ### Materials: Gump Button 1 ###
    "kindling": FletchingCraftable(
        Name="kindling",
        Item=None,
        RetainsMark=False,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={boards["ordinary board"]: 1},
        GumpPath=(GumpSelection(fletchingGump, 1), GumpSelection(fletchingGump, 2)),
    ),
    "shaft": FletchingCraftable(
        Name="shaft",
        Item=None,
        RetainsMark=False,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={boards["ordinary board"]: 1},
        GumpPath=(GumpSelection(fletchingGump, 1), GumpSelection(fletchingGump, 9)),
    ),
    ### Ammunition: Gump Button 8 ###
    "arrow": FletchingCraftable(
        Name="arrow",
        Item=None,
        RetainsMark=False,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={miscellaneous["arrow shaft"]: 1, miscellaneous["feather"]: 1},
        GumpPath=(GumpSelection(fletchingGump, 8), GumpSelection(fletchingGump, 2)),
    ),
    "crossbow bolt": FletchingCraftable(
        Name="crossbow bolt",
        Item=None,
        RetainsMark=False,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={miscellaneous["arrow shaft"]: 1, miscellaneous["feather"]: 1},
        GumpPath=(GumpSelection(fletchingGump, 8), GumpSelection(fletchingGump, 9)),
    ),
    ### Weapons: Gump Button 15 ###
    "crossbow": FletchingCraftable(
        Name="crossbow",
        Item=weapons["crossbow"],
        RetainsMark=True,
        RetainsColor=False,
        MinSkill={"fletching": 60.0},
        ResourcesNeeded={boards["ordinary board"]: 7},
        GumpPath=(GumpSelection(fletchingGump, 15), GumpSelection(fletchingGump, 2)),
    ),
    "bow": FletchingCraftable(
        Name="bow",
        Item=weapons["bow"],
        RetainsMark=True,
        RetainsColor=False,
        MinSkill={"fletching": 30.0},
        ResourcesNeeded={boards["ordinary board"]: 7},
        GumpPath=(GumpSelection(fletchingGump, 15), GumpSelection(fletchingGump, 9)),
    ),
    "heavy crossbow": FletchingCraftable(
        Name="heavy crossbow",
        Item=weapons["heavy crossbow"],
        RetainsMark=True,
        RetainsColor=False,
        MinSkill={"fletching": 80.0},
        ResourcesNeeded={boards["ordinary board"]: 10},
        GumpPath=(GumpSelection(fletchingGump, 15), GumpSelection(fletchingGump, 16)),
    ),
}
