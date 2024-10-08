import Items
from System import Int32
from System.Collections.Generic import List
from utils.items import myItem

containers = {
    "backpack": myItem("backpack", 0x0E75, 0x0000, "container", 1),
    "bag": myItem("bag", 0x0E76, 0x0000, "container", 1),
    "barrel": myItem("barrel", 0x0E77, 0x0000, "container", 1),
    "crate": myItem("crate", 0x0E7E, 0x0000, "container", 1),
    "hatch": myItem("hatch", 0x3E65, 0x0000, "container", None),  # Can't be carried
    "metal chest (east/west)": myItem("metal chest", 0x0E7C, 0x0000, "container", 1),
    "metal chest (north/south)": myItem("metal chest", 0x2DF3, 0x0000, "container", 1),
    "ornate elven chest": myItem("ornate elven chest", 0x0E79, 0x0000, "container", 1),
    "pouch": myItem("pouch", 0x0E79, 0x0000, "container", 1),
    "trash barrel": myItem("trash barrel", 0x0E77, 0x03B2, "container", 1),
    "wooden box": myItem("wooden box", 0x0E7D, 0x0000, "container", 1),
    "wooden chest": myItem("wooden chest", 0x0E43, 0x0000, "container", 1),
}


def FindTrashBarrel():
    """
    Locates a trash barrel within reach.
    """

    global containers

    trashBarrelFilter = Items.Filter()
    trashBarrelFilter.OnGround = 1
    trashBarrelFilter.Movable = False
    trashBarrelFilter.RangeMin = 0
    trashBarrelFilter.RangeMax = 2
    trashBarrelFilter.Graphics = List[Int32]([containers["trash barrel"].itemID])
    trashBarrelFilter.Hues = List[Int32]([containers["trash barrel"].color])

    trashBarrel = Items.ApplyFilter(trashBarrelFilter)

    if len(trashBarrel) == 0:
        return None
    else:
        return trashBarrel[0]


def FindHatch():
    """
    Locates a hatch within reach.
    """

    global containers

    hatchFilter = Items.Filter()
    hatchFilter.OnGround = 1
    hatchFilter.Movable = False
    hatchFilter.RangeMin = 0
    hatchFilter.RangeMax = 2
    hatchFilter.Graphics = List[Int32]([containers["hatch"].itemID])

    hatch = Items.ApplyFilter(hatchFilter)

    if len(hatch) == 0:
        return None
    else:
        return hatch[0]
