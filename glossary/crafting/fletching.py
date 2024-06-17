from glossary.crafting.craftable import Craftable
from glossary.items.weapons import weapons
from glossary.items.miscellaneous import miscellaneous
from glossary.items.tools import tools
from glossary.items.boards import boards
from utils.gumps import GumpSelection

fletchName = "Fletching"
fletchGump = 949095101
fletchTools = [tools["arrow fletching"]]

fletchCraftables = {
    ### Materials: Gump Button 1 ###
    "kindling": Craftable(
        Name="kindling",
        Item=miscellaneous["kindling"],
        RetainsMark=False,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={boards["ordinary board"]: 1},
        GumpPath=(GumpSelection(fletchGump, 1), GumpSelection(fletchGump, 2)),
    ),
    "shaft": Craftable(
        Name="shaft",
        Item=None,
        RetainsMark=False,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={boards["ordinary board"]: 1},
        GumpPath=(GumpSelection(fletchGump, 1), GumpSelection(fletchGump, 9)),
    ),
    ### Ammunition: Gump Button 8 ###
    "arrow": Craftable(
        Name="arrow",
        Item=None,
        RetainsMark=False,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={miscellaneous["arrow shaft"]: 1, miscellaneous["feather"]: 1},
        GumpPath=(GumpSelection(fletchGump, 8), GumpSelection(fletchGump, 2)),
    ),
    "crossbow bolt": Craftable(
        Name="crossbow bolt",
        Item=None,
        RetainsMark=False,
        RetainsColor=False,
        MinSkill={"fletching": 0.0},
        ResourcesNeeded={miscellaneous["arrow shaft"]: 1, miscellaneous["feather"]: 1},
        GumpPath=(GumpSelection(fletchGump, 8), GumpSelection(fletchGump, 9)),
    ),
    ### Weapons: Gump Button 15 ###
    "crossbow": Craftable(
        Name="crossbow",
        Item=weapons["crossbow"],
        RetainsMark=True,
        RetainsColor=False,
        MinSkill={"fletching": 60.0},
        ResourcesNeeded={boards["ordinary board"]: 7},
        GumpPath=(GumpSelection(fletchGump, 15), GumpSelection(fletchGump, 2)),
    ),
    "bow": Craftable(
        Name="bow",
        Item=weapons["bow"],
        RetainsMark=True,
        RetainsColor=False,
        MinSkill={"fletching": 30.0},
        ResourcesNeeded={boards["ordinary board"]: 7},
        GumpPath=(GumpSelection(fletchGump, 15), GumpSelection(fletchGump, 9)),
    ),
    "heavy crossbow": Craftable(
        Name="heavy crossbow",
        Item=weapons["heavy crossbow"],
        RetainsMark=True,
        RetainsColor=False,
        MinSkill={"fletching": 80.0},
        ResourcesNeeded={boards["ordinary board"]: 10},
        GumpPath=(GumpSelection(fletchGump, 15), GumpSelection(fletchGump, 16)),
    ),
    ### Materials: Gump Button 22 ###
    "elven bow": Craftable(
        Name="elven bow",
        Item=weapons["elven bow"],
        RetainsMark=True,
        RetainsColor=True,
        MinSkill={"fletching": 89.5},
        ResourcesNeeded={boards["oak board"]: 7},
        GumpPath=(GumpSelection(fletchGump, 22), GumpSelection(fletchGump, 2)),
    ),
}
