import config
from glossary.gumps import gumps


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


def use_runebook(runebook_serial, slot):
    runebook = gumps["runebook"]
    Gumps.ResetGump()
    Items.UseItem(runebook_serial)
    Gumps.WaitForGump(runebook.Id, 1500)
    Gumps.SendAction(runebook.Id, runebook.Options[slot].Id)
