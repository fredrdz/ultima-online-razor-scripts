# WIP
# SCRIPT: carpentry.py
# Author: Talik Starr
# IN:RISEN
# Skill: Carpentry

# --- PARAMETERS ---
weightLimit = Player.MaxWeight + 30
hammerID = 0x102A
clubID = 0x13B4
blankScrollID = None
logID = 0x1BDD
boardID = 0x1BD7
gumpDelay = 5000
axeList = [0x0F49, 0x13FB, 0x0F47, 0x1443, 0x0F45, 0x0F4B, 0x0F43]
carpentryGump = 949095101


# ---------------------------------------------------------------------
def Overweight():
    if Player.Weight >= weightLimit:
        Misc.Beep()
        return True


# ---------------------------------------------------------------------
def Build(itemID):
    wood = Items.FindByID(boardID, -1, Player.Backpack.Serial)
    if wood:
        woodAmount = wood.Amount
    else:
        Misc.SendMessage(">> no boards", 35)
        return False

    hammer = Items.FindByID(hammerID, -1, Player.Backpack.Serial)
    if hammer:
        Items.UseItem(hammer.Serial)
    else:
        Misc.SendMessage(">> no hammers", 35)
        return False

    if itemID == clubID:
        if woodAmount < 3:
            Misc.SendMessage(">> not enough wood", 35)
            return False
        Gumps.WaitForGump(carpentryGump, gumpDelay)
        Gumps.SendAction(carpentryGump, 29)
        Gumps.WaitForGump(carpentryGump, gumpDelay)
        Gumps.SendAction(carpentryGump, 2)
        Gumps.WaitForGump(carpentryGump, gumpDelay)
    elif itemID == blankScrollID:
        if woodAmount < 1:
            Misc.SendMessage(">> not enough wood", 35)
            return False
        Gumps.WaitForGump(carpentryGump, gumpDelay)
        Gumps.SendAction(carpentryGump, 1)
        Gumps.WaitForGump(carpentryGump, gumpDelay)
        Gumps.SendAction(carpentryGump, 9)
        Gumps.WaitForGump(carpentryGump, gumpDelay)

    return True


# ---------------------------------------------------------------------
# main script loop
while Player.GetRealSkillValue("Carpentry") < 100:
    if Player.GetRealSkillValue("Carpentry") < 70:
        craftItem = clubID
    elif Player.GetRealSkillValue("Carpentry") >= 70:
        craftItem = blankScrollID

    if not Build(craftItem):
        Misc.SendMessage(">> no items could be built", 35)
        Misc.Beep()
        break

    if Overweight():
        break
