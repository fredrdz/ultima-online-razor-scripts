"""
SCRIPT: train_Alchemy.py
Author: Talik Starr
IN:RISEN
Skill: Alchemy
"""

# custom RE packages
import Items, Player, Misc, Target
from glossary.crafting.alchemy import (
    alchName,
    alchGump,
    alchTools,
    alchCraftables,
)
from glossary.items.potions import potions
from glossary.colors import colors
from utils.crafting import TrainCraftSkill
from utils.items import EnableSellingAgent

# ---------------------------------------------------------------------
# script configuration; modify these per your requirements

# setting a secure container will disable bank restocking
# will restock from here instead; useful for crafting in house
secureContainer = 0x40125C18
# will toss successful crafts into trash barrel
throwAwayItems = False
# will vendor sell after full backpack or if overweight
sellItems = False

# vendor selling parameters
vendorName = "Slade"
sellX = 1470
sellY = 1581

# slot number in runebook, 1 of 16
bank_rune = 1
house_rune = 2
vendor_rune = 3

# bank parameters
# only use bank from this x,y coordinate
bankX = 1424
bankY = 1683
# disabled if secure container in use
containerInBank = 0x40054709

# items to deposit in bank bag or secure container
# a list of tuples containing itemID and count
depositItems = [
    (0x0EED, -1),  # gold
    (potions["greater mana potion"].itemID, -1),
    (potions["lesser poison potion"].itemID, -1),
    (potions["deadly poison potion"].itemID, -1),
]

# ---------------------------------------------------------------------
# do not edit below this line

# init
# check for runebook
if not Misc.CheckSharedValue("young_runebook"):
    Misc.ScriptRun("_startup.py")
if Misc.CheckSharedValue("young_runebook"):
    runebook_serial = Misc.ReadSharedValue("young_runebook")
else:
    runebook_serial = Target.PromptTarget(
        ">> target the runebook with th bank, house, and vendor rune", colors["notice"]
    )

# check what type of restock container we're using;
# only one instance of secureContainer or containerInBank may exist;
# not both; one will be set to None
if secureContainer is not None:
    # secure container was specified; use it
    restockContainer = secureContainer
    containerInBank = None
elif containerInBank is not None:
    # container in bank was specified; use it
    restockContainer = containerInBank
else:
    # no container was specified; prompt for one
    restockContainer = Target.PromptTarget(
        ">> target your restocking container", colors["notice"]
    )
    containerAsItem = Items.FindBySerial(restockContainer)
    # check if container is in bank
    if containerAsItem.IsInBank is False:
        Misc.SendMessage(f">> {containerAsItem.Name} was not in bank", colors["status"])
        secureContainer = restockContainer
        containerInBank = None
    else:
        Misc.SendMessage(f">> {containerAsItem.Name} was in bank", colors["status"])
        containerInBank = restockContainer
        secureContainer = None


craftConfig = {
    # script flags
    "sellItems": sellItems,
    "throwAwayItems": throwAwayItems,
    # container settings
    "containerInBank": containerInBank,
    "restockContainer": restockContainer,
    "depositItems": depositItems,
    # player settings
    "playerBag": Player.Backpack,
    "runebook": runebook_serial,
    "house_rune": house_rune,
    # bank settings
    "bank_rune": bank_rune,
    "bankPosition": (bankX, bankY),
    # vendor settings
    "vendor_rune": vendor_rune,
    "vendorName": vendorName,
    "vendorPosition": (sellX, sellY),
    # skill settings
    "skillName": alchName,
    "skillGump": alchGump,
    "skillTools": alchTools,
    "skillCraftables": alchCraftables,
    # skill path to use: "skill" or "profit"
    "usePath": "profit",
    # a dictionary of skill paths and their values
    # define what item names to craft and up to which maximum skill value
    "paths": {
        "skill": {
            "lesser poison": 100.0,
        },
        "profit": {
            "deadly poison": 100.0,
            "greater mana": 120.0,
        },
    },
}


# ---------------------------------------------------------------------
# script functions
def TrainAlchemySkill(
    craftConfig={},
):
    """
    Trains Alchemy skill to its skill cap
    """
    TrainCraftSkill(craftConfig)
    return


# ---------------------------------------------------------------------
# main script process

EnableSellingAgent("alchemy")
TrainAlchemySkill(craftConfig)
