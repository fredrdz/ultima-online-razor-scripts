"""
SCRIPT: skill_Lumberjacking.py
Author: Talik Starr
IN:RISEN
Skill: Lumberjacking
"""

# System packages
import sys
import math
import time
import random
from System.Collections.Generic import List
from System import Byte

# custom RE packages
import Gumps, Items, Journal, Player, Misc, Mobiles, Statics, Target, Timer
from glossary.colors import colors
from glossary.spells import spellReagents
from utils.pathing import (
    IsPosition,
    PathCount,
    PlayerDiagonalOffset,
    RazorPathing,
)
from utils.actions import Chat_on_position, Audio_say
from utils.item_actions.common import (
    unequip_hands,
    equip_left_hand,
    RecallNext,
    RecallCurrent,
    RecallPrevious,
    RecallBank,
    use_runebook,
)
from utils.items import MoveItemsByCount
from utils.status import Overweight
from utils.gumps import is_afk_gump, get_afk_gump_button_options, solve_afk_gump


# ********************
# Trees where there is no longer enough wood to be harvested will not be revisited until this much time has passed
treeCooldown = 1200000  # 1,200,000 ms is 20 minutes

# Want this script to alert you for humaniods?
alert = True
# Want this script to run away from bad guys?
runaway = False

# setting a secure container will disable bank restocking
# will restock from here instead
secureContainer = None

containerInBank = 0x40054709  # Serial of log bag in bank
bankX = 3701
bankY = 2519


# slot number in runebook, 1 of 16
bank_rune = 1
house_rune = 2
vendor_rune = 3

# Define constants for the minimum and maximum values of tree_rune
MIN_TREE_RUNE = 3
MAX_TREE_RUNE = 3
CURRENT_TREE_RUNE = 2
# ********************

# Parameters
# more than 25 tiles of scanning may crash client
scanRadius = 25

weightLimit = Player.MaxWeight + 30

axeList = [0x0F49, 0x13FB, 0x0F47, 0x1443, 0x0F45, 0x0F4B, 0x0F43]

logID = 0x1BDD
boardID = 0x1BD7
goldID = 0x0EED

# triplet; (itemID, color, count)
# defaults to natural color of item if tuple
# naturalColor = 0
# anyColor = -1
# anyAmount = -1
depositItems = [
    (boardID, -1, -1),
    (logID, -1, -1),
    (goldID, -1),
]

# ---------------------------------------------------------------------
# do not edit below this line


class Tree:
    def __init__(self, x, y, z, id):
        self.x = x
        self.y = y
        self.z = z
        self.id = id


# init
trees = []
Timer.Create("tracking_cd", 1)
playerBag = Player.Backpack.Serial

# check for runebook
if not Misc.CheckSharedValue("young_runebook"):
    Misc.ScriptRun("_startup.py")
if Misc.CheckSharedValue("young_runebook"):
    runebook_serial = Misc.ReadSharedValue("young_runebook")
else:
    runebook_serial = Target.PromptTarget(">> target your runebook", colors["notice"])

# check what type of restock container we're using;
# only one instance of secureContainer or containerInBank may exist;
# not both; one will be set to None
if secureContainer is not None:
    # secure container was specified; use it
    restockContainer = secureContainer
    containerInBank = None
elif containerInBank is not None:
    # container in bank was specified; use it
    restockContainer = containerInBank
else:
    # no container was specified; prompt for one
    restockContainer = Target.PromptTarget(
        ">> target your restocking container", colors["notice"]
    )
    containerAsItem = Items.FindBySerial(restockContainer)
    # check if container is in bank
    if containerAsItem.IsInBank is False:
        Misc.SendMessage(f">> {containerAsItem.Name} was not in bank", colors["status"])
        secureContainer = restockContainer
        containerInBank = None
    else:
        Misc.SendMessage(f">> {containerAsItem.Name} was in bank", colors["status"])
        containerInBank = restockContainer
        secureContainer = None

treeStaticIDs = [
    0x0C95,
    0x0C96,
    0x0C99,
    0x0C9B,
    0x0C9C,
    0x0C9D,
    0x0C8A,
    0x0CA6,
    0x0CA8,
    0x0CAA,
    0x0CAB,
    0x0CC3,
    0x0CC4,
    0x0CC8,
    0x0CC9,
    0x0CCA,
    0x0CCB,
    0x0CCC,
    0x0CCD,
    0x0CD0,
    0x0CD3,
    0x0CD6,
    0x0CD8,
    0x0CDA,
    0x0CDD,
    0x0CE0,
    0x0CE3,
    0x0CE6,
    0x0CF8,
    0x0CFB,
    0x0CFE,
    0x0D01,
    0x0D25,
    0x0D27,
    0x0D35,
    0x0D37,
    0x0D38,
    0x0D42,
    0x0D43,
    0x0D59,
    0x0D70,
    0x0D85,
    0x0D94,
    0x0D96,
    0x0D98,
    0x0D9A,
    0x0D9C,
    0x0D9E,
    0x0DA0,
    0x0DA2,
    0x0DA4,
    0x0DA8,
]


# ---------------------------------------------------------------------
def Bank(runebook, rune, x=0, y=0):
    # recall to bank if not close
    if PathCount(x, y) > 20:
        RecallBank(runebook, rune)
        Misc.Pause(2000)

    # pathfind to bank if not at bank calling coordinates
    while IsPosition(x, y) is False:
        Misc.Pause(100)
        if RazorPathing(x, y) is False:
            if Misc.ScriptStatus("pathfinding.py") is False:
                Misc.SetSharedValue("pathFindingOverride", (x, y))
                Misc.ScriptRun("pathfinding.py")
                Misc.Pause(1000)

    # use bank via chat; only does it if on bank coordinates
    Chat_on_position("bank", (x, y))


def Restock(itemList, src, dst=Player.Backpack.Serial):
    if not itemList:
        Misc.SendMessage(">> no items requested for restock", colors["fatal"])
        return False

    if src is None or not isinstance(src, int):
        Misc.SendMessage(">> no source container specified", colors["fatal"])
        return False

    difference = []
    for id, required_count in itemList:
        src_count = Items.ContainerCount(src, id)
        if src_count <= required_count:
            return False

        dst_count = Items.BackpackCount(id)
        if dst_count < required_count:
            difference.append((id, required_count - dst_count))

    if not difference:
        Misc.SendMessage(">> no items need restocking", colors["success"])
        return True

    MoveItemsByCount(difference, src, dst)
    return True


def DepositAndRestock(runebook, rune, x=0, y=0):
    Journal.Clear()

    # use bank if enabled
    if containerInBank is not None:
        Bank(runebook, rune, x, y)

    # get container as an item class
    containerItem = Items.FindBySerial(restockContainer)
    if not containerItem:
        Misc.SendMessage(">> restocking container not found", colors["fatal"])
        sys.exit()

    # some chopping if logs in player bag
    while Items.BackpackCount(logID) > 0:
        CutLogs()

    # open the container to load contents into memory
    if containerItem.IsContainer:
        Items.UseItem(containerItem)

    # deposit items in container
    MoveItemsByCount(depositItems, playerBag, restockContainer)

    # fatal error if container is full
    if Journal.SearchByType("That container cannot hold more weight.", "System"):
        Misc.SendMessage(">> container is full", colors["fatal"])
        sys.exit()

    # restock
    recallSpell = spellReagents.get("Recall", [])
    restockItems = []
    for reg in recallSpell:
        restockItems.append((reg.itemID, 10))
    if Restock(restockItems, restockContainer) is False:
        Misc.SendMessage(">> failed to restock necessary items", colors["fatal"])
        sys.exit()


# ---------------------------------------------------------------------
# bug: may crash client when tree list is too large or too many tiles
def ScanStatic(trees=List[Tree]) -> List[Tree]:
    new_trees = []

    Misc.Resync()
    Misc.SendMessage(">> scanning tiles...", colors["status"])

    player_position = Player.Position
    minX = player_position.X - scanRadius
    maxX = player_position.X + scanRadius
    minY = player_position.Y - scanRadius
    maxY = player_position.Y + scanRadius

    Misc.SendMessage(">> adding trees", colors["status"])
    for x in range(minX, maxX + 1):
        for y in range(minY, maxY + 1):
            staticsTileInfo = Statics.GetStaticsTileInfo(x, y, Player.Map)
            # might reduce client crash by throttling tile lookups
            time.sleep(0.001)  # 1 milliseconds
            if staticsTileInfo:
                for tile in staticsTileInfo:
                    if tile.StaticID in treeStaticIDs and not Timer.Check(f"{x},{y}"):
                        new_trees.append(Tree(x, y, tile.StaticZ, tile.StaticID))

    Misc.SendMessage(">> sorting trees", colors["status"])
    new_trees.sort(
        key=lambda tree: math.hypot(
            tree.x - player_position.X, tree.y - player_position.Y
        )
    )

    trees.extend(new_trees)

    Misc.SendMessage(">> total trees: %i" % len(trees), colors["success"])
    return trees


# ---------------------------------------------------------------------
def MoveToTree():
    if not trees or len(trees) == 0:
        return False

    tX = trees[0].x
    tY = trees[0].y

    if PathCount(tX, tY) > 50:
        Misc.SendMessage(f">> tree too far away: {tX}, {tY}", colors["warning"])
        return False

    Misc.SendMessage(f">> moving to tree: {tX}, {tY}", colors["status"])

    chopOffset = PlayerDiagonalOffset(tX, tY)
    if not chopOffset:
        return False

    chopX, chopY = chopOffset
    if RazorPathing(chopX, chopY) is False:
        Misc.SetSharedValue("pathFindingOverride", (chopX, chopY))
        Misc.ScriptRun("pathfinding.py")

    # init timeouts
    Timer.Create("pathing", 10000)
    Timer.Create("safteyNet", 1)

    # wait for position to be reached until t/o
    while IsPosition(chopX, chopY) is False and Timer.Check("pathing") is True:
        Misc.Pause(random.randint(50, 150))
        if Timer.Check("safteyNet") is False:
            SafteyNet()
            Timer.Create("safteyNet", 2000)

    # if pathfinding script is still running after t/o, stop it
    if Timer.Check("pathing") is False:
        if Misc.ScriptStatus("pathfinding.py"):
            Misc.ScriptStop("pathfinding.py")
        Misc.SendMessage(">> pathlocked, resetting", colors["error"])
        Misc.SendMessage(f">> failed to reach tree: {tX}, {tY}", colors["error"])
        return False

    # if here, we succeeded in reaching the tree
    Misc.SendMessage(f">> reached tree: {tX}, {tY}", colors["notice"])
    return True


# ---------------------------------------------------------------------
def CutLogs():
    EquipAxe()
    for item in Player.Backpack.Contains:
        if item.ItemID == logID:
            Items.UseItem(Player.GetItemOnLayer("LeftHand"))
            Target.WaitForTarget(1000, False)
            Target.TargetExecute(item)
            Misc.Pause(300)


# ---------------------------------------------------------------------
def EquipAxe():
    if Player.CheckLayer("RightHand"):
        unequip_hands()
    elif Player.CheckLayer("LeftHand"):
        if Player.GetItemOnLayer("LeftHand").ItemID not in axeList:
            unequip_hands()

    if not Player.CheckLayer("LeftHand"):
        for item in Player.Backpack.Contains:
            if item.ItemID in axeList:
                equip_left_hand(item.Serial)
                break
        if not Player.CheckLayer("LeftHand"):
            Misc.SendMessage(">> no axes found", colors["fatal"])
            Misc.Beep()
            sys.exit()


# ---------------------------------------------------------------------
def CutTree():
    if Target.HasTarget():
        Misc.SendMessage(">> detected target cursor, refreshing...", colors["warning"])
        Target.Cancel()
        Misc.Pause(500)

    if Overweight(weightLimit):
        return

    Journal.Clear()

    EquipAxe()
    Items.UseItem(Player.GetItemOnLayer("LeftHand"))
    Target.WaitForTarget(3000, True)
    Target.TargetExecute(trees[0].x, trees[0].y, trees[0].z, trees[0].id)

    # init timers
    Timer.Create("chop_timeout", 10000)
    Timer.Create("safteyNet", 1)

    # wait for tree to be chopped until t/o
    while not (
        Journal.SearchByType(
            "You hack at the tree for a while, but fail to produce any useable wood.",
            "System",
        )
        or Journal.SearchByType("You chop some", "System")
        or Journal.SearchByType("There's not enough wood here to harvest.", "System")
        or Journal.Search("Target cannot be seen")
        or Journal.Search("That is too far away")
        or not Timer.Check("chop_timeout")
    ):
        Misc.Pause(100)

    # if here, we are not chopping, so we do checks
    if Timer.Check("safteyNet") is False:
        SafteyNet()
        Timer.Create("safteyNet", 2000)

    if Journal.SearchByType("There's not enough wood here to harvest.", "System"):
        Misc.SendMessage(">> no wood here", colors["status"])
        Misc.SendMessage(">> tree change", colors["status"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search("That is too far away"):
        Misc.SendMessage(">> blocked; cannot target", colors["warning"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search("Target cannot be seen"):
        Misc.SendMessage(">> blocked; cannot target", colors["warning"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Timer.Check("chop_timeout") is False:
        Misc.SendMessage(">> tree change", colors["status"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search("bloodwood"):
        Misc.SendMessage(">> bloodwood!", colors["status"])
        Timer.Create("chop_timeout", 10000)
        CutTree()
    elif Journal.Search("heartwood"):
        Misc.SendMessage(">> heartwood!", colors["status"])
        Timer.Create("chop_timeout", 10000)
        CutTree()
    elif Journal.Search("frostwood"):
        Misc.SendMessage(">> frostwood!", colors["status"])
        Timer.Create("chop_timeout", 10000)
        CutTree()
    else:
        CutTree()


# ---------------------------------------------------------------------
# safteyNet

enemyFilter = Mobiles.Filter()
enemyFilter.Enabled = True
enemyFilter.RangeMin = -1
enemyFilter.RangeMax = -1
enemyFilter.Poisoned = -1
enemyFilter.IsHuman = -1
enemyFilter.IsGhost = False
enemyFilter.Warmode = -1
enemyFilter.Friend = False
enemyFilter.Paralized = -1
enemyFilter.Notorieties = List[Byte](bytes([4, 5, 6]))


def IsEnemy():
    enemies = Mobiles.ApplyFilter(enemyFilter)
    if not enemies or len(enemies) == 0:
        return False

    nearestEnemy = Mobiles.Select(enemies, "Nearest")

    Mobiles.Message(
        nearestEnemy,
        colors["warning"],
        ">> enemy detected",
    )

    return True


playerFilter = Mobiles.Filter()
playerFilter.Enabled = True
playerFilter.RangeMin = -1
playerFilter.RangeMax = -1
playerFilter.CheckLineOfSight = False
playerFilter.Poisoned = -1
playerFilter.IsHuman = True
playerFilter.IsGhost = False
playerFilter.Warmode = -1
playerFilter.Friend = False
playerFilter.Paralized = -1
playerFilter.Notorieties = List[Byte](bytes([1, 4, 5, 6]))


def IsPlayer():
    # mobile filter: short range player detection
    # safteyNet runs every 2 seconds
    humans = Mobiles.ApplyFilter(playerFilter)
    if len(humans) > 0:
        Timer.Create("tracking_cd", 1)
        Misc.SendMessage(">> human nearby", colors["warning"])
        Misc.Pause(1000)

    # tracking skill: long range player detection
    # 20 second cooldown unless overridden by short range detection
    if Timer.Check("tracking_cd") is False:
        Misc.SendMessage(">> checking for players...", colors["status"])
        Player.UseSkill("Tracking", False)
        Timer.Create("tracking_cd", 20000)
        Gumps.WaitForGump(2976808305, 2000)
        if Gumps.CurrentGump() == 2976808305:
            Gumps.SendAction(2976808305, 4)
            Gumps.WaitForGump(993494147, 2000)
            if Gumps.CurrentGump() == 993494147:
                Misc.SendMessage(">> found players", colors["alert"])
                player_list = Gumps.LastGumpGetLineList()
                if player_list:
                    player_list = [str(line) for line in player_list]
                    for player in player_list:
                        Misc.SendMessage(f"-- {player}", colors["alert"])
                    Gumps.CloseGump(993494147)
                    return True
    return False


invulFilter = Mobiles.Filter()
invulFilter.Enabled = True
invulFilter.RangeMin = -1
invulFilter.RangeMax = -1
invulFilter.Friend = False
invulFilter.Notorieties = List[Byte](bytes([7]))


def SafteyNet():
    # tries to auto solve afk gump or alerts if it fails
    if is_afk_gump():
        Misc.Beep()
        button_options = get_afk_gump_button_options()
        if button_options:
            if not solve_afk_gump(button_options):
                Audio_say("solve AFK Gump")
                Misc.FocusUOWindow()
                sys.exit()

    # checks runaway flag; recalls away from enemies if detected
    if runaway is True:
        if IsEnemy() is True:
            Misc.Beep()
            Misc.Beep()
            Audio_say("enemy detected")
            RecallNext(runebook_serial, CURRENT_TREE_RUNE, MIN_TREE_RUNE, MAX_TREE_RUNE)

    # monitors mobiles and alerts if found
    if alert:
        invul = Mobiles.ApplyFilter(invulFilter)
        if IsPlayer() is True:
            Misc.Beep()
            Misc.Beep()
            Audio_say("player is here")
            Misc.FocusUOWindow()
            rb = Misc.ReadSharedValue("young_runebook")
            use_runebook(rb, 1)
            Misc.Pause(2000)
            Player.UseSkill("Hiding", False)
            sys.exit()
        elif invul:
            Misc.Beep()
            Misc.Beep()
            Misc.Beep()
            Misc.FocusUOWindow()
            Audio_say("GM here")
            invulName = Mobiles.Select(invul, "Nearest")
            if invulName:
                Misc.SendMessage(">> invul near:" + invul.Name, colors["warning"])

    # close any gumps that may be opened to avoid issues
    if Gumps.HasGump():
        opened_gump_id = Gumps.CurrentGump()
        Gumps.CloseGump(opened_gump_id)


# ---------------------------------------------------------------------
# main process
Misc.SendMessage(">> lumberjack starting up...", colors["notice"])

while not Player.IsGhost:
    Misc.Pause(100)
    trees = ScanStatic(trees)

    if not trees or len(trees) == 0:
        Misc.SendMessage(">> no trees found", colors["fatal"])
        Misc.SendMessage(">> going to next zone...", colors["notice"])
        # RecallNext(runebook, CURRENT_TREE_RUNE, MIN_TREE_RUNE, MAX_TREE_RUNE)
        continue

    while len(trees) > 0:
        if Overweight(weightLimit):
            DepositAndRestock(runebook_serial, house_rune, bankX, bankY)
            break
        if MoveToTree():
            CutTree()
        trees.pop(0)
        trees.sort(
            key=lambda tree: math.hypot(
                tree.x - Player.Position.X, tree.y - Player.Position.Y
            )
        )
