# system packages
import sys

# custom RE packages
import Items, Misc, Player, Target
import config
from glossary.items.furniture import furniture, FindForge
from glossary.items.food import food
from glossary.colors import colors
from utils.items import MoveItemsByCount

# ---------------------------------------------------------------------
# init
restockContainer = 0x40125C18
raw_fish_steak = food["raw fish steak"]
fish_steak = food["fish steak"]

# ---------------------------------------------------------------------
# find forge
forge = FindForge(furniture)
if not forge:
    Misc.SendMessage(">> forge not found", colors["fatal"])
    sys.exit()

# get container as an item class
containerItem = Items.FindBySerial(restockContainer)
if not containerItem:
    Misc.SendMessage(">> restocking container not found", colors["fatal"])
    sys.exit()

# open the container to load contents into memory
if containerItem.IsContainer:
    Items.UseItem(containerItem)

# ---------------------------------------------------------------------
while not Player.IsGhost and Player.GetRealSkillValue("Cooking") < Player.GetSkillCap(
    "Cooking"
):
    # reduce cpu usage
    Misc.Pause(100)

    # deposit fish steak if found in player backpack
    if Items.BackpackCount(fish_steak.itemID) >= 100:
        Misc.SendMessage(">> fish steak found", colors["status"])
        Misc.SendMessage(">> depositing...", colors["status"])
        stock = [(fish_steak.itemID, -1)]
        MoveItemsByCount(
            stock,
            Player.Backpack.Serial,
            containerItem.Serial,
        )

    # get raw fish steak item
    raw_item = Items.FindByID(raw_fish_steak.itemID, -1, restockContainer)

    # if found use it
    if raw_item:
        Items.UseItem(raw_item)
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(forge)
        Misc.Pause(2500 + config.shardLatency)

    # stop script if skill maxed out
    if Player.GetRealSkillValue("Cooking") >= Player.GetSkillCap("Cooking"):
        Misc.SendMessage(">> maxed out Cooking skill", colors["notice"])
        break
