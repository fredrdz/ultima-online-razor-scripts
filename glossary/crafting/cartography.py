from glossary.crafting.craftable import Craftable
from glossary.items.miscellaneous import miscellaneous
from glossary.items.tools import tools
from utils.gumps import GumpSelection

cartName = "Cartography"
cartGump = 949095101
cartTools = [tools["mapmaker's pen"], tools["pen and ink"]]


cartCraftables = {
    "local map": Craftable(
        Name="local map",
        Item=miscellaneous["map"],
        RetainsMark=False,
        RetainsColor=False,
        MinSkill=10.0,
        ResourcesNeeded={miscellaneous["blank scroll"]: 1},
        GumpPath=(GumpSelection(cartGump, 1), GumpSelection(cartGump, 2)),
    ),
    "city map": Craftable(
        Name="city map",
        Item=miscellaneous["map"],
        RetainsMark=False,
        RetainsColor=False,
        MinSkill=25.0,
        ResourcesNeeded={miscellaneous["blank scroll"]: 1},
        GumpPath=(GumpSelection(cartGump, 1), GumpSelection(cartGump, 9)),
    ),
    "sea map": Craftable(
        Name="sea map",
        Item=miscellaneous["map"],
        RetainsMark=False,
        RetainsColor=False,
        MinSkill=35.0,
        ResourcesNeeded={miscellaneous["blank scroll"]: 1},
        GumpPath=(GumpSelection(cartGump, 1), GumpSelection(cartGump, 16)),
    ),
    "world map": Craftable(
        Name="world map",
        Item=miscellaneous["map"],
        RetainsMark=False,
        RetainsColor=False,
        MinSkill=39.5,
        ResourcesNeeded={miscellaneous["blank scroll"]: 1},
        GumpPath=(GumpSelection(cartGump, 1), GumpSelection(cartGump, 23)),
    ),
}
