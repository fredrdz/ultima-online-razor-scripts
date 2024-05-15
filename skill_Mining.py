from utils.items import FindItem, FindNumberOfItems, MoveItem
from glossary.items.ores import ores
from glossary.colors import colors

useMount = True
usePetStorage = True


def Mount():
    Misc.Pause(700)
    mountSerial = Misc.ReadSharedValue("mount")
    if mountSerial is not None:
        mount = Mobiles.FindBySerial(Misc.ReadSharedValue("mount"))
        if mount is not None:
            Mobiles.UseMobile(mount)


def MoveOreToPet():
    petSerial = Misc.ReadSharedValue("petForStorage1")
    if petSerial is not None:
        pet = Mobiles.FindBySerial(Misc.ReadSharedValue("petForStorage1"))

    if pet is None:
        Misc.SendMessage(">> could not find storage pet", colors["fatal"])

    for ore in ores:
        oreStack = FindItem(ores[ore].itemID, Player.Backpack, ores[ore].color)
        while oreStack is not None:
            Misc.SendMessage(
                ">> moving stack of %s to pet" % ores[ore].name, colors["status"]
            )
            MoveItem(Items, Misc, oreStack, pet.Backpack)

            oreStack = Items.FindBySerial(oreStack.Serial)
            if oreStack != None and oreStack.RootContainer != Player.Serial:
                # the stack still exists, but was moved to the pet
                oreStack = None

            if oreStack is None:
                continue

            # stack wasn't moved, so the pet is either overweight or nearly overweight
            # move as much as we can over to the pet by moving one item from the stack at a time
            amountBeforeMove = FindNumberOfItems(
                ores[ore].itemID, Player.Backpack, ores[ore].color
            )
            MoveItem(Items, Misc, oreStack, pet.Backpack, 1)
            oreStack = Items.FindBySerial(oreStack.Serial)
            amountInBag = FindNumberOfItems(
                ores[ore].itemID, Player.Backpack, ores[ore].color
            )
            while amountInBag != amountBeforeMove:
                amountBeforeMove = amountInBag
                Misc.SendMessage(">> %s" % oreStack, colors["status"])
                MoveItem(Items, Misc, oreStack, pet.Backpack, 1)
                oreStack = Items.FindBySerial(oreStack.Serial)
                amountInBag = FindNumberOfItems(
                    ores[ore].itemID, Player.Backpack, ores[ore].color
                )

            if Player.Weight <= Player.MaxWeight:
                Misc.SendMessage(
                    ">> moved enough to pet for you to move normally", colors["success"]
                )

            Misc.SendMessage(">> pet is overweight", colors["fatal"])
            # There is still some ore in the player's bag
            return False

    # We were able to move all of the ore
    return True


def Mine():
    global useMount
    global usePetStorage

    mount = None
    mountSerial = None
    pet = None
    petSerial = None

    if usePetStorage:
        petSerial = Misc.ReadSharedValue("petForStorage1")
        if petSerial is not None:
            pet = Mobiles.FindBySerial(Misc.ReadSharedValue("petForStorage1"))

    if Player.Mount != None:
        # we need to dismount to be able to mine
        Mobiles.UseMobile(Player.Serial)
        Misc.Pause(1000)

    Journal.Clear()
    while (
        not Journal.SearchByName("There is no metal here to mine.", "System")
        and not Journal.SearchByName("Target cannot be seen.", "System")
        and not Journal.SearchByName("You can't mine there.", "System")
    ):
        if Player.Weight <= Player.MaxWeight:
            pickaxe = FindItem(0x0E86, Player.Backpack)
            if pickaxe is None:
                Misc.SendMessage(">> no pickaxes", colors["fatal"])
                break

            Items.UseItem(pickaxe)
            Target.WaitForTarget(2000, True)
            Target.TargetExecuteRelative(Player.Serial, 1)

            Misc.Pause(500)
            if Journal.SearchByType("Target cannot be seen.", "Regular"):
                Journal.Clear()
                break

            # wait for the mining animation to complete and then call the guards in case an elemental appears
            Misc.Pause(500)
            # Player.ChatSay( 90, 'guards' )
        else:
            Misc.SendMessage(">> player overweight", colors["fatal"])

        # if we're overweight, move ore into a pet
        if usePetStorage and Player.Weight > Player.MaxWeight:
            Misc.SendMessage(">> moving ore to pet", colors["notice"])
            movedAllOre = MoveOreToPet()
            if not movedAllOre:
                if useMount:
                    Mount()
                return

        # Wait a little bit so that the while loop doesn't consume as much CPU
        Misc.Pause(50)

    Misc.SendMessage(">> no more ores to mine here", colors["fail"])
    if useMount:
        Mount()


if useMount:
    if not Misc.CheckSharedValue("mount"):
        if Player.Mount != None:
            mount = Player.Mount.Serial
        else:
            mount = Target.PromptTarget("Select your mount")
        Misc.SetSharedValue("mount", mount)

if usePetStorage:
    if not Misc.CheckSharedValue("petForStorage1"):
        pet = Target.PromptTarget("Select pet to store ore in")
        Misc.SetSharedValue("petForStorage1", pet)

# Start mining
Mine()
# MoveOreToPet()
