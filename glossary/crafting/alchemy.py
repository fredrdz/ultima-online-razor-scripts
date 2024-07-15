from glossary.crafting.craftable import Craftable
from glossary.items.miscellaneous import miscellaneous
from glossary.items.tools import tools
from glossary.items.reagents import reagents
from glossary.items.potions import potions
from utils.gumps import GumpSelection

alchName = "Alchemy"
alchGump = 949095101
alchTools = [
    tools["mortar and pestle"],
]


alchCraftables = {
    ### Other: Gump Button 36 ###
    "lesser poison": Craftable(
        Name="lesser poison",
        Item=potions["lesser poison potion"],
        RetainsMark=False,
        RetainsColor=True,
        MinSkill={"Alchemy": 0.0},
        ResourcesNeeded={reagents["Nightshade"]: 1, miscellaneous["empty bottle"]: 1},
        GumpPath=(GumpSelection(alchGump, 36), GumpSelection(alchGump, 2)),
    ),
}
