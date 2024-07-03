# System packages
from System import Int32
from System.Collections.Generic import List

# custom RE packages
from utils.items import myItem
import Items

furniture = {
    "anvil": myItem("anvil", 0x0FB0, 0x0000, "furniture", None),
    "broken chair": myItem("broken chair", 0x0C1B, 0x0000, "furniture", None),
    "crystal workbench": myItem("crystal workbench", 0x2DF3, 0x0B93, "furniture", None),
    "forge": myItem("forge", 0x0FB1, 0x0000, "furniture", None),
    "map storage cabinet": myItem(
        "map storage cabinet", 0x285C, 0x0000, "furniture", None
    ),
    "skill scroll storage bookshelf": myItem(
        "skill scroll storage bookshelf", 0x0A9A, 0x0501, "furniture", None
    ),
    "stone chair": myItem("stone chair", 0x121A, 0x0000, "furniture", None),
    "table": myItem("table", 0x0B34, 0x0000, "furniture", None),
    "throne": myItem("throne", 0x0B33, 0x0000, "furniture", None),
    "wooden bench (east/west)": myItem(
        "wooden bench", 0x0B2C, 0x0000, "furniture", None
    ),
    "wooden bench (north/south)": myItem(
        "wooden bench", 0x0B2D, 0x0000, "furniture", None
    ),
}


# ---------------------------------------------------------------------
def FindForge(furniture=furniture):
    """
    Locates a forge within reach.
    """

    forgeFilter = Items.Filter()
    forgeFilter.OnGround = 1
    forgeFilter.Movable = False
    forgeFilter.RangeMax = 0
    forgeFilter.RangeMax = 2
    forgeFilter.Graphics = List[Int32]([furniture["forge"].itemID])

    forge = Items.ApplyFilter(forgeFilter)

    if len(forge) == 0:
        return None
    else:
        return forge[0]
