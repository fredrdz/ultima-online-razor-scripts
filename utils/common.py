import time
import sys

#
import Mobiles
import Items
import Player
import Gumps
import Target
import Misc

#
import re

#
from System.Collections.Generic import List
from System import Byte, Int32


#
def FindPets():
    pets = []
    pet_filter = Mobiles.Filter()
    pet_filter.Enabled = True
    pet_filter.RangeMin = -1
    pet_filter.RangeMax = 10
    pet_filter.Notorieties = List[Byte](bytes([1, 2]))
    potentialPets = Mobiles.ApplyFilter(pet_filter)
    for potentialPet in potentialPets:
        #
        props = Mobiles.GetPropStringList(potentialPet)
        for p in props:
            prop = str(p)
            # Misc.SendMessage(prop)
            ownerMatch = re.search("Owner: ({}).*".format(Player.Name), prop)
            if ownerMatch:
                pets.append(potentialPet)
            # bonded = re.search("bonded", prop)
            # if bonded:
            # pets.append(potentialPet)

    return pets


#
def DoForEachItemIn(bag, fn):
    ret_list = []
    if isinstance(bag, int):
        container = Items.FindBySerial(bag)
    else:
        container = bag
    # if not found
    if container == None:
        return ret_list
    # if the itemId is in array (container or not) return it and don't look further
    if fn(container):
        ret_list.append(container)
    # if not container return empty list
    if not container.IsContainer:
        return ret_list
    #  These things appear as containers but are not
    if container.ItemID == 0x1EA7 and container.Hue == 0x0032:
        # gem of nautical exploration is a container !?!
        return ret_list
    if "sending" in Items.GetPropStringByIndex(container, 0).lower():
        return ret_list
    if "spellbook" in Items.GetPropStringByIndex(container, 0).lower():
        return ret_list
    Items.UseItem(container)
    Items.WaitForContents(container, 2000)
    for item in container.Contains:
        for tmp in DoForEachItemIn(item.Serial, fn):
            ret_list.append(tmp)
    return ret_list


#
def findRecursive(containerSerial, typeArray, openContainers=False):
    ret_list = []
    container = Items.FindBySerial(containerSerial)
    # if not found
    if container == None:
        return ret_list
    # if the itemId is in array (container or not) return it and don't look further
    if container.ItemID in typeArray:
        ret_list.append(container)
        return ret_list
    # if not container return empty list
    if not container.IsContainer:
        return ret_list
    #  These things appear as containers but are not
    if container.ItemID == 0x1EA7 and container.Hue == 0x0032:
        # gem of nautical exploration is a container !?!
        return ret_list
    if "sending" in Items.GetPropStringByIndex(container, 0).lower():
        return ret_list
    if "spellbook" in Items.GetPropStringByIndex(container, 0).lower():
        return ret_list
    # If a container has not been openned it will appear empty, but opening them all makes the UI ugly
    if openContainers:
        Items.UseItem(container)
        Items.WaitForContents(container, 2000)
    for item in container.Contains:
        for tmp in findRecursive(item.Serial, typeArray, openContainers):
            ret_list.append(tmp)
    return ret_list


#
def findRecursiveWithColor(containerSerial, typeArray, openContainers=False):
    ret_list = []
    types = []
    typeColor = []
    for id in typeArray:
        types.append(id[0])
        typeColor.append(id[1])
    #
    container = Items.FindBySerial(containerSerial)
    # if not found
    if container == None:
        return ret_list
    # if the itemId is in array (container or not) return it and don't look further
    try:
        index = types.index(container.ItemID)
        # Misc.SendMessage("2 container: {:x} id: {:x} color: {:x}".format(container.Serial, container.ItemID, container.Hue))
        # Misc.SendMessage("Index: {}".format(index))
        if container.Hue == typeColor[index] or typeColor[index] == -1:
            ret_list.append(container)
    except ValueError:
        pass
    # if not container return empty list
    if not container.IsContainer:
        return ret_list
    #  These things appear as containers but are not
    if container.ItemID == 0x1EA7 and container.Hue == 0x0032:
        # gem of nautical exploration is a container !?!
        return ret_list
    if "sending" in Items.GetPropStringByIndex(container, 0).lower():
        return ret_list
    if "spellbook" in Items.GetPropStringByIndex(container, 0).lower():
        return ret_list
    # If a container has not been openned it will appear empty, but opening them all makes the UI ugly
    if openContainers:
        Items.UseItem(container)
        Items.WaitForContents(container, 2000)
    for item in container.Contains:
        # Misc.SendMessage("1 container: {:x} id: {:x} color: {:x}".format(container.Serial, item.ItemID, item.Hue))
        for tmp in findRecursiveWithColor(item.Serial, typeArray, openContainers):
            ret_list.append(tmp)
    return ret_list


#
def find(containerSerial, typeArray):
    ret_list = []
    container = Items.FindBySerial(containerSerial)
    if container != None:
        for item in container.Contains:
            if item.ItemID in typeArray:
                ret_list.append(item)
    return ret_list


#
def DexHealingFormula():
    if Player.Dex > 80:
        healTime = 8 - ((Player.Dex - 80) / 20)
        if healTime < 0.5:
            return 0.5
        else:
            return healTime
    else:
        return 8


#
NextHealTime = time.time()


def HealMe(wait=True):
    global NextHealTime
    if True == BandageHeal.Status():
        return
    healDelay = NextHealTime - time.time()
    if healDelay > 0:
        if wait:
            Misc.Pause(healDelay * 1000)
        else:
            return
    if Misc.CheckSharedValue("BandSelf"):
        Player.ChatSay(0, Misc.ReadSharedValue("BandSelf"))
    else:
        Items.UseItemByID(0x0E21, 0x0480)
        Target.WaitForTarget(200, False)
        Target.Self()
    delay = DexHealingFormula()
    NextHealTime = time.time() + delay
    # Misc.SendMessage("Next heal time {} now {}".format(NextHealTime, time.time()))


#
tinker_kitsID = 0x1EB8
fletching_kitsID = 0x1022
woodID = 0x1BD7
woodStorage = 0x44046D13
shaftID = 0x1BD4
metalID = 0x1BF2
hatchetID = 0x0F43


#
def MakeTinkerKits():
    kit = Items.FindByID(tinker_kitsID, 0, Player.Backpack.Serial)
    if kit == None:
        Misc.SendMessage("CANNOT MAKE TINKER KITS WITHOUT AT LEAST 1 IN PACK")
        sys.exit(0)
    #
    if Items.BackpackCount(metalID, 0) < 2:
        Misc.SendMessage("Need iron ingots in your pack to make tinker kit")
        sys.exit(0)
    #
    Items.UseItem(kit)
    Gumps.WaitForGump(949095101, 2000)
    Gumps.SendAction(949095101, 8)
    Gumps.WaitForGump(949095101, 2000)
    Gumps.SendAction(949095101, 23)
    Gumps.WaitForGump(949095101, 2000)
    Gumps.SendAction(949095101, 0)
    Gumps.WaitForGump(949095101, 2000)
    Target.Cancel()


#
def MakeFletchingKits():
    kit = Items.FindByID(tinker_kitsID, 0, Player.Backpack.Serial)
    if kit == None:
        MakeTinkerKits()
        kit = Items.FindByID(tinker_kitsID, 0, Player.Backpack.Serial)
        if kit == None:
            Misc.SendMessage("Insufficient TINKER KITS TO MAKE FLETCHING KIT")
            sys.exit(0)
    #
    if Items.BackpackCount(metalID, 0) < 3:
        Misc.SendMessage("Need iron ingots in your pack to make fletching kit")
        sys.exit(0)
    #
    Items.UseItem(kit)
    Gumps.WaitForGump(949095101, 5000)
    Gumps.SendAction(949095101, 8)
    Gumps.WaitForGump(949095101, 5000)
    Gumps.SendAction(949095101, 142)
    Gumps.WaitForGump(949095101, 5000)
    Gumps.SendAction(949095101, 0)


#
def MakeHatchet():
    kit = Items.FindByID(tinker_kitsID, 0, Player.Backpack.Serial)
    if kit == None:
        Misc.SendMessage("Insufficient TINKER KITS TO MAKE FLETCHING KIT")
        sys.exit(0)
    #
    if Items.BackpackCount(metalID, 0) < 4:
        Misc.SendMessage("Need iron ingots in your pack to make fletching kit")
        sys.exit(0)
    #
    Items.UseItem(kit)
    Gumps.WaitForGump(949095101, 10000)
    Gumps.SendAction(949095101, 8)
    Gumps.WaitForGump(949095101, 10000)
    Gumps.SendAction(949095101, 30)
    Gumps.WaitForGump(949095101, 10000)
    Gumps.SendAction(949095101, 0)


#
def MakeShovel():
    kit = Items.FindByID(tinker_kitsID, 0, Player.Backpack.Serial)
    if kit == None:
        Misc.SendMessage("Insufficient TINKER KITS TO MAKE FLETCHING KIT")
        sys.exit(0)
    #
    if Items.BackpackCount(metalID, 0) < 4:
        Misc.SendMessage("Need iron ingots in your pack to make fletching kit")
        sys.exit(0)
    #
    Items.UseItem(kit)
    Gumps.WaitForGump(949095101, 2000)
    Gumps.SendAction(949095101, 8)
    Gumps.WaitForGump(949095101, 2000)
    Gumps.SendAction(949095101, 72)
    Gumps.WaitForGump(949095101, 2000)
    Gumps.SendAction(949095101, 0)
