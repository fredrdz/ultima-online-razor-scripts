import config
from glossary.gumps import gumps

# ---------------------------------------------------------------------


def unequip_hands():
    return unequip_left_hand(), unequip_right_hand()


def unequip_left_hand():
    """
    Unequip the left hand and return item class.
    If no item was equipped, nothing will happen and it will return None type.
    Drag Delay set via Config.
    """
    if Player.CheckLayer("LeftHand"):
        left_item = Player.GetItemOnLayer("LeftHand")
        Player.UnEquipItemByLayer("LeftHand", True)
        Misc.Pause(config.dragDelayMilliseconds)
        return left_item
    else:
        return None


def unequip_right_hand():
    """
    Unequip the right hand and return item class.
    If no item was equipped, nothing will happen and it will return None type.
    Drag Delay set via Config.
    """
    if Player.CheckLayer("RightHand"):
        right_item = Player.GetItemOnLayer("RightHand")
        Player.UnEquipItemByLayer("RightHand", True)
        Misc.Pause(config.dragDelayMilliseconds)
        return right_item
    else:
        return None


def equip_hands(left_item, right_item):
    return equip_left_hand(left_item), equip_right_hand(right_item)


def equip_left_hand(left_item):
    """
    Equip the left hand with the provided item ID or SERIAL.
    If no valid ID or SERIAL is provided, nothing will happen.
    Drag Delay set via Config.
    """
    if left_item:
        Player.EquipItem(left_item)
        Misc.Pause(config.dragDelayMilliseconds)


def equip_right_hand(right_item):
    """
    Equip the right hand with the provided item ID or SERIAL.
    If no valid ID or SERIAL is provided, nothing will happen.
    Drag Delay set via Config.
    """
    if right_item:
        Player.EquipItem(right_item)
        Misc.Pause(config.dragDelayMilliseconds)


# ---------------------------------------------------------------------


def use_runebook(runebook_serial, slot_number=1):
    slot = "Slot %i" % slot_number
    runebook = gumps["runebook"]
    Gumps.ResetGump()
    Items.UseItem(runebook_serial)
    Gumps.WaitForGump(runebook.Id, 1500)
    Gumps.SendAction(runebook.Id, runebook.Options[slot].Id)
    Gumps.CloseGump(runebook.Id)


def RecallNext(runebook, tree_rune=1, MIN_TREE_RUNE=1, MAX_TREE_RUNE=16):
    # calculates the next tree_rune, wrapping around if it exceeds MAX_TREE_RUNE
    next_tree_rune = MIN_TREE_RUNE + (tree_rune + 1 - MIN_TREE_RUNE) % (
        MAX_TREE_RUNE - MIN_TREE_RUNE + 1
    )
    Misc.SendMessage(">> recalling to next zone", colors["notice"])
    use_runebook(runebook, next_tree_rune)
    Misc.Pause(config.recallDelay + config.shardLatency)


def RecallCurrent(runebook, tree_rune=1):
    Misc.SendMessage(">> recalling to current zone", colors["notice"])
    use_runebook(runebook, tree_rune)
    Misc.Pause(config.recallDelay + config.shardLatency)


def RecallPrevious(runebook, tree_rune=1, MIN_TREE_RUNE=1, MAX_TREE_RUNE=16):
    # calculates the previous tree_rune, wrapping around if it goes below MIN_TREE_RUNE
    previous_tree_rune = MAX_TREE_RUNE - (MAX_TREE_RUNE - tree_rune + 1) % (
        MAX_TREE_RUNE - MIN_TREE_RUNE + 1
    )
    Misc.SendMessage(">> recalling to previous zone", colors["notice"])
    use_runebook(runebook, previous_tree_rune)
    Misc.Pause(config.recallDelay + config.shardLatency)


def RecallBank(runebook, bank_rune=1):
    use_runebook(runebook, bank_rune)
    Misc.Pause(config.recallDelay + config.shardLatency)
