"""
SCRIPT: stealing.py
Author: Talik Starr
IN:RISEN
Skill: Stealing
"""

# custom RE packages
from config import journalEntryDelayMilliseconds
from glossary.colors import colors

psHue = 0x0481
blazeHue = 1161  # 0x0489
short_delay = 20
snoop_delay = 600

ignoreList = []

trap_hues = [0x0489, 0x0026]
containers = [0xE76, 0xE75, 0xE74, 0xE78, 0xE7D, 0xE77]
bags = [0x0E76, 0xE75, 0xE74, 0xE78, 0xE77, 0x0E79]
# 0x0E7D trap box
# 0x0E79 pouch
# 0x0E75 backpack
# 0x0E76 bag

powerScroll = 0x14F0
skillScroll = 0x2260
garlic = 0x0F84
root = 0x0F86
bandages = 0x0E21
cure_pots = 0x0F07

steal_priorities_Hues = [powerScroll, skillScroll]
steal_priorities = [skillScroll, powerScroll, garlic, root, bandages, cure_pots]
stealHues = [blazeHue, psHue]


def is_steal_success():
    Misc.Pause(journalEntryDelayMilliseconds)
    Timer.Create("journal_timeout", 4500)
    while not Journal.SearchByType("You successfully steal the item.", "System"):
        Misc.Pause(100)
        if Journal.SearchByType("You fail to steal the item.", "System"):
            Misc.SendMessage(">> failed to steal item", colors["fail"])
            return False
        elif not Timer.Check("journal_timeout"):
            Misc.SendMessage(">> stealing timed out", colors["error"])
            return False

    Misc.SendMessage(">> successfully stole item", colors["success"])
    return True


def steal(item, mark):
    Journal.Clear()
    attempted = False
    Items.WaitForProps(item, 500)

    while not attempted:
        if Items.GetPropValue(item, "Blessed"):
            Misc.SendMessage(">> detected blessed item", colors["alert"])
            ignoreList.append(item.Serial)
            break

        Misc.SendMessage(">> attempting steal", colors["status"])
        Target.ClearLastandQueue()
        Target.Cancel()
        Player.UseSkill("Stealing")
        Misc.Pause(journalEntryDelayMilliseconds)
        if Journal.SearchByType("You must wait to perform another action.", "System"):
            Misc.SendMessage(">> skill cooldown", colors["warning"])
            Journal.Clear()
            Misc.Pause(1000)
        elif Journal.SearchByType("You can't steal that.", "System"):
            Misc.SendMessage(">> blessed item", colors["error"])
            ignoreList.append(item)
            Journal.Clear()
            attempted = True
        else:
            Target.WaitForTarget(1000)
            while Player.DistanceTo(mark) > 1:
                Misc.Pause(short_delay)
            Target.TargetExecute(item)
            attempted = True

    is_steal_success()


def snoop_recursive(container, mark):
    Items.UseItem(container)
    contents = container.Contains
    stealThis = []

    steal_target_bags = [
        item for item in contents if item.ItemID in bags and item.Hue not in trap_hues
    ]

    items_to_steal = [
        item.Serial for item in contents if (item.ItemID in steal_priorities)
    ]

    for i in items_to_steal:
        ok = Items.FindBySerial(i)
        if ok.Serial in ignoreList:
            Misc.NoOperation()
        elif ok.ItemID in steal_priorities_Hues:
            if ok.Hue in stealHues:
                stealThis.append(i)
        else:
            stealThis.append(i)

    if len(stealThis) > 0:
        stealItem = Items.FindBySerial(stealThis[0])
        Misc.SendMessage(">> item: %s" % (stealItem.Name), colors["info"])
        return steal(stealItem, mark)

    if len(steal_target_bags) == 0:
        return True
    else:
        for bag in steal_target_bags:
            Misc.Pause(snoop_delay)
            snoop_recursive(bag, mark)
    return True


def stealing_run_continuously():
    while Player.Hits > 0:
        mark = Target.GetTargetFromList("stealtarget")
        if mark != None and Player.DistanceTo(mark) < 2:
            snoop_recursive(mark.Backpack, mark)
            Misc.Pause(short_delay)
        Misc.Pause(600)


# filter
def find():
    fil = Mobiles.Filter()
    fil.Enabled = True
    fil.RangeMax = 1
    fil.IsHuman = True
    fil.IsGhost = False
    fil.Friend = False
    fil.Notorieties = List[Byte](bytes(1, 3, 4, 5, 6))
    list = Mobiles.ApplyFilter(fil)

    return list


def stealing_run_once():
    mark = Mobiles.Select(find(), "Next")  # Target.GetTargetFromList("stealtarget")

    if mark != None and Player.DistanceTo(mark) < 2:
        snoop_recursive(mark.Backpack, mark)
        Misc.Pause(short_delay)
    Misc.Pause(600)


def stealing_run_once_targeted(mobile):
    mark = mobile

    if mark != None and Player.DistanceTo(mark) < 2:
        snoop_recursive(mark.Backpack, mark)
        Misc.Pause(short_delay)
    Misc.Pause(600)
