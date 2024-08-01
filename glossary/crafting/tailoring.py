from glossary.crafting.craftable import Craftable
from glossary.items.cloth import cloth
from glossary.items.clothing import clothing
from glossary.items.tools import tools
from utils.gumps import GumpSelection

tailName = "Tailoring"
tailGump = 949095101
tailTools = [tools["sewing kit"]]


tailCraftables = {
    ### Hats: Gump Button 1 ###
    "skullcap": Craftable(
        Name="skullcap",
        Item=clothing["skullcap"],
        RetainsMark=True,
        RetainsColor=True,
        MinSkill=0.0,
        ResourcesNeeded={cloth["folded cloth"]: 2},
        GumpPath=(GumpSelection(tailGump, 1), GumpSelection(tailGump, 2)),
    ),
    "bandana": Craftable(
        Name="bandana",
        Item=clothing["bandana"],
        RetainsMark=True,
        RetainsColor=True,
        MinSkill=0.0,
        ResourcesNeeded={cloth["folded cloth"]: 2},
        GumpPath=(GumpSelection(tailGump, 1), GumpSelection(tailGump, 9)),
    ),
}
