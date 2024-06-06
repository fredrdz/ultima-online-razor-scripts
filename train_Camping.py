# system packages
import sys

# custom RE packages
import Items, Misc, Player
import config
from glossary.items.miscellaneous import miscellaneous
from glossary.colors import colors
from utils.items import MoveItemsByCount

# init
restockContainer = 0x40125C18
kindling = miscellaneous["kindling"]

# get container as an item class
containerItem = Items.FindBySerial(restockContainer)
if not containerItem:
    Misc.SendMessage(">> restocking container not found", colors["fatal"])
    sys.exit()

# open the container to load contents into memory
if containerItem.IsContainer:
    Items.UseItem(containerItem)

while not Player.IsGhost and Player.GetRealSkillValue("Camping") < Player.GetSkillCap(
    "Camping"
):
    # reduce cpu usage
    Misc.Pause(100)

    # restock kindling if none found in player backpack
    if Items.BackpackCount(kindling.itemID) <= 0:
        Misc.SendMessage(">> kindling not found", colors["fail"])
        Misc.SendMessage(">> restocking...", colors["status"])
        restock = [(kindling.itemID, 100)]
        MoveItemsByCount(restock, containerItem.Serial, Player.Backpack.Serial)

    # get kindling item
    kindlingItem = Items.FindByID(kindling.itemID, -1, Player.Backpack.Serial)
    # if found use it
    if kindling:
        Items.UseItem(kindlingItem)
        Misc.Pause(1000 + config.shardLatency)

    # stop script if skill maxed out
    if Player.GetRealSkillValue("Camping") >= Player.GetSkillCap("Camping"):
        Misc.SendMessage(">> maxed out Camping skill", colors["notice"])
        break
