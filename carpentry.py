# WIP
# SCRIPT: carpentry.py
# Author: Talik Starr
# IN:RISEN
# Skill: Carpentry

from glossary.colors import colors
from utils.actions import Bank, VendorSell
from utils.items import MoveItemsByCount, RestockAgent
from utils.magery import Recall
from utils.status import Overweight

# --- PARAMETERS ---
bankRune = 0x400BAAB7

restockWeight = 75
weightLimit = Player.MaxWeight + 30

backpack = Player.Backpack.Serial
itemBag = 0x40054709

goldID = 0x0EED
hammerID = 0x102A
club_ID = 0x13B4
blankScroll_ID = 0x0EF3
boardID = 0x1BD7

gumpDelay = 5000
carpentryGump = 949095101


bankDeposit = [
    (blankScroll_ID, -1),
    (goldID, -1),
]


# ---------------------------------------------------------------------
def Build(itemID):
    wood = Items.FindByID(boardID, -1, Player.Backpack.Serial)
    if wood:
        woodAmount = wood.Amount
    else:
        Misc.SendMessage(">> no boards", colors["error"])
        return False

    hammer = Items.FindByID(hammerID, -1, Player.Backpack.Serial)
    if hammer:
        Items.UseItem(hammer.Serial)
    else:
        Misc.SendMessage(">> no hammers", colors["error"])
        return False

    if itemID == club_ID:
        if woodAmount < 3:
            Misc.SendMessage(">> not enough wood", colors["error"])
            return False
        Gumps.WaitForGump(carpentryGump, gumpDelay)
        Gumps.SendAction(carpentryGump, 29)
        Gumps.WaitForGump(carpentryGump, gumpDelay)
        Gumps.SendAction(carpentryGump, 2)
        Gumps.WaitForGump(carpentryGump, gumpDelay)
    elif itemID == blankScroll_ID:
        if woodAmount < 1:
            Misc.SendMessage(">> not enough wood", colors["error"])
            return False
        Gumps.WaitForGump(carpentryGump, gumpDelay)
        Gumps.SendAction(carpentryGump, 1)
        Gumps.WaitForGump(carpentryGump, gumpDelay)
        Gumps.SendAction(carpentryGump, 9)
        Gumps.WaitForGump(carpentryGump, gumpDelay)

    return True


def Clubs():
    craftItem = club_ID

    if Player.Weight <= restockWeight:
        Recall(bankRune)
        Bank(bankX, bankY)
        RestockAgent("recall")
        RestockAgent("carpentry")

    if Overweight(weightLimit):
        amount = Items.BackpackCount(craftItem)
        Misc.SendMessage(">> " + str(amount) + " items to sell", colors["status"])
        while Items.BackpackCount(craftItem) > 1:
            VendorSell(vendorX, vendorY)
            Misc.Pause(500)

    if not Build(craftItem):
        while Items.BackpackCount(craftItem) > 1:
            VendorSell(vendorX, vendorY)
            Misc.Pause(500)
        Misc.SendMessage(">> no items could be built", colors["error"])
        Misc.Beep()
        return False

    return True


def Scrolls():
    craftItem = blankScroll_ID

    if Player.Weight <= restockWeight:
        Misc.SendMessage(">> within restock threshold", colors["error"])
        return False

    if Overweight(weightLimit):
        Misc.SendMessage(">> player overweight", colors["error"])
        return False

    if not Build(craftItem):
        Misc.SendMessage(">> no items could be built", colors["error"])
        Misc.Beep()
        return False

    return True


# ---------------------------------------------------------------------
# main process

while Player.GetRealSkillValue("Carpentry") < 100:
    if Player.GetSkillValue("Carpentry") < 70:
        if not Clubs():
            break
    elif Player.GetSkillValue("Carpentry") >= 70:
        if not Scrolls():
            Bank(bankX, bankY)
            MoveItemsByCount(bankDeposit, backpack, itemBag)
            Misc.Pause(3000)
            RestockAgent("carpentry")
            Misc.Pause(3000)
