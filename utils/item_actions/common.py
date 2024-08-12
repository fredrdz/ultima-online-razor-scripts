# custom RE packages
import config
import Gumps, Items, Player, Misc
from glossary.gumps import gumps
from glossary.colors import colors

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


def equip_left_hand(left_item, delay=config.dragDelayMilliseconds):
    """
    Equip the left hand with the provided item ID or SERIAL.
    If no valid ID or SERIAL is provided, nothing will happen.
    Drag Delay set via Config.
    """
    if not isinstance(delay, int):
        delay = config.dragDelayMilliseconds

    if not Player.CheckLayer("LeftHand"):
        if left_item:
            Player.EquipItem(left_item)
            Misc.Pause(delay)


def equip_right_hand(right_item, delay=config.dragDelayMilliseconds):
    """
    Equip the right hand with the provided item ID or SERIAL.
    If no valid ID or SERIAL is provided, nothing will happen.
    Drag Delay set via Config.
    """
    if not isinstance(delay, int):
        delay = config.dragDelayMilliseconds

    if not Player.CheckLayer("RightHand"):
        if right_item:
            Player.EquipItem(right_item)
            Misc.Pause(delay)


# ---------------------------------------------------------------------


def use_runebook(runebook_serial, slot_number=1):
    slot = "Slot %i" % slot_number
    runebook = gumps["runebook"]
    Gumps.ResetGump()
    Items.UseItem(runebook_serial)
    Gumps.WaitForGump(runebook.Id, 1500)
    Gumps.SendAction(runebook.Id, runebook.Options[slot].Id)
    Gumps.CloseGump(runebook.Id)


def RecallNext(runebook, RUNE=1, MIN_RUNE=1, MAX_RUNE=16) -> int:
    # calculates the next RUNE, wrapping around if it exceeds MAX_RUNE
    next_rune = MIN_RUNE + (RUNE + 1 - MIN_RUNE) % (MAX_RUNE - MIN_RUNE + 1)
    Misc.SendMessage(">> recalling to next zone", colors["notice"])
    use_runebook(runebook, next_rune)
    Misc.Pause(config.recallDelay + config.shardLatency)
    return next_rune


def RecallCurrent(runebook, RUNE=1):
    Misc.SendMessage(">> recalling to current zone", colors["notice"])
    use_runebook(runebook, RUNE)
    Misc.Pause(config.recallDelay + config.shardLatency)


def RecallPrevious(runebook, RUNE=1, MIN_RUNE=1, MAX_RUNE=16) -> int:
    # calculates the previous RUNE, wrapping around if it goes below MIN_RUNE
    previous_rune = MAX_RUNE - (MAX_RUNE - RUNE + 1) % (MAX_RUNE - MIN_RUNE + 1)
    Misc.SendMessage(">> recalling to previous zone", colors["notice"])
    use_runebook(runebook, previous_rune)
    Misc.Pause(config.recallDelay + config.shardLatency)
    return previous_rune


def RecallBank(runebook, bank_rune=1):
    use_runebook(runebook, bank_rune)
    Misc.Pause(config.recallDelay + config.shardLatency)
