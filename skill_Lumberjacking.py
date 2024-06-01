"""
SCRIPT: skill_Lumberjacking.py
Author: Talik Starr
IN:RISEN
Skill: Lumberjacking
"""

# System packages
import sys
from System.Collections.Generic import List
from System import Byte
from math import sqrt
import random

# custom RE packages
import Friend, Items, Journal, Player, Misc, Mobiles, Statics, Target, Timer
from glossary.colors import colors
from utils.pathing import (
    IsPosition,
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
)
from utils.items import MoveItemsByCount, RestockAgent
from utils.status import Overweight
from utils.gumps import is_afk_gump, get_afk_gump_button_options, solve_afk_gump


# ********************
# Trees where there is no longer enough wood to be harvested will not be revisited until this much time has passed
treeCooldown = 1200000  # 1,200,000 ms is 20 minutes

# Want this script to alert you for humaniods?
alert = True
# Want this script to run away from bad guys?
runaway = False

logBag = 0x40054709  # Serial of log bag in bank
bankX = 3699
bankY = 2520
runebook = 0x4003B289
bank_rune = 2

# Define constants for the minimum and maximum values of tree_rune
MIN_TREE_RUNE = 3
MAX_TREE_RUNE = 3
CURRENT_TREE_RUNE = 2
# ********************

# Parameters
scanRadius = 40
TimeoutOnWaitAction = 3000

weightLimit = Player.MaxWeight + 30
backpack = Player.Backpack.Serial

axeList = [0x0F49, 0x13FB, 0x0F47, 0x1443, 0x0F45, 0x0F4B, 0x0F43]

logID = 0x1BDD
boardID = 0x1BD7
goldID = 0x0EED

bankDeposit = [
    (boardID, -1),
    (logID, -1),
    (goldID, -1),
]

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
# Custom Classes
class Tree:
    def __init__(self, x, y, z, id):
        self.x = x
        self.y = y
        self.z = z
        self.id = id


# ---------------------------------------------------------------------
def Bank(x=0, y=0):
    if not IsPosition(x, y):
        if RazorPathing(x, y) is False:
            Misc.SetSharedValue("pathFindingOverride", (x, y))
            Misc.ScriptRun("pathfinding.py")

    Chat_on_position("bank", (x, y))


def DepositInBank(x=0, y=0):
    # go to the bank
    if not IsPosition(x, y):
        RecallBank(runebook, bank_rune)
    Bank(x, y)
    Journal.Clear()

    # restock and wait a bit before chopping logs
    RestockAgent("recall")
    Misc.Pause(1000)

    # some chopping if logs in player bag
    while Items.BackpackCount(logID) > 0:
        CutLogs()

    MoveItemsByCount(bankDeposit, backpack, logBag)

    # fatal error if bank is full
    if Journal.SearchByType("That container cannot hold more weight.", "System"):
        Misc.SendMessage(">> bank is full", colors["fatal"])
        sys.exit()


# ---------------------------------------------------------------------
def ScanStatic():
    global trees
    Misc.SendMessage(">> scan tile started...", colors["notice"])
    minX = Player.Position.X - scanRadius
    maxX = Player.Position.X + scanRadius
    minY = Player.Position.Y - scanRadius
    maxY = Player.Position.Y + scanRadius

    x = minX
    y = minY

    while x <= maxX:
        while y <= maxY:
            staticsTileInfo = Statics.GetStaticsTileInfo(x, y, Player.Map)
            if staticsTileInfo.Count > 0:
                for tile in staticsTileInfo:
                    for staticid in treeStaticIDs:
                        if staticid == tile.StaticID and not Timer.Check(
                            "%i,%i" % (x, y)
                        ):
                            # Misc.SendMessage( '>> tree X: %i - Y: %i - Z: %i' % ( minX, minY, tile.StaticZ ), colors["debug"])
                            trees.Add(Tree(x, y, tile.StaticZ, tile.StaticID))
            y = y + 1
        y = minY
        x = x + 1

    trees = sorted(
        trees,
        key=lambda tree: sqrt(
            pow((tree.x - Player.Position.X), 2) + pow((tree.y - Player.Position.Y), 2)
        ),
    )
    Misc.SendMessage(">> total trees: %i" % (trees.Count), colors["success"])


# ---------------------------------------------------------------------
def MoveToTree():
    global trees

    if not trees or trees.Count == 0:
        return False

    Misc.SendMessage(
        ">> moving to tree: %i, %i" % (trees[0].x, trees[0].y), colors["notice"]
    )
    Misc.Resync()

    chopOffset = PlayerDiagonalOffset(trees[0].x, trees[0].y)
    if not chopOffset:
        return False

    chopX, chopY = chopOffset
    if not RazorPathing(chopX, chopY):
        Misc.SetSharedValue("pathFindingOverride", (chopX, chopY))
        Misc.ScriptRun("pathfinding.py")

    Timer.Create("path_timeout", 10000)
    while Misc.Distance(Player.Position.X, Player.Position.Y, chopX, chopY) != 0:
        SafteyNet()
        Misc.Pause(random.randint(50, 150))
        if not Timer.Check("path_timeout"):
            if Misc.ScriptStatus("pathfinding.py"):
                Misc.ScriptStop("pathfinding.py")
            Misc.SendMessage(">> pathlocked, resetting", colors["fatal"])
            Misc.SendMessage(
                ">> failed to reach tree: %i, %i" % (trees[0].x, trees[0].y),
                colors["error"],
            )
            return False

    Misc.SendMessage(
        ">> reached tree: %i, %i" % (trees[0].x, trees[0].y), colors["notice"]
    )
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
        Misc.SendMessage(">> detected target cursor, refreshing...", colors["notice"])
        Target.Cancel()
        Misc.Pause(500)

    if Overweight(weightLimit):
        return

    Journal.Clear()

    EquipAxe()
    Items.UseItem(Player.GetItemOnLayer("LeftHand"))
    Target.WaitForTarget(TimeoutOnWaitAction, True)
    Target.TargetExecute(trees[0].x, trees[0].y, trees[0].z, trees[0].id)
    Timer.Create("chopTimer", 10000)
    while not (
        Journal.SearchByType(
            "You hack at the tree for a while, but fail to produce any useable wood.",
            "System",
        )
        or Journal.SearchByType("You chop some", "System")
        or Journal.SearchByType("There's not enough wood here to harvest.", "System")
        or not Timer.Check("chopTimer")
    ):
        SafteyNet()
        Misc.Pause(random.randint(50, 150))

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
    elif not Timer.Check("chopTimer"):
        Misc.SendMessage(">> tree change", colors["status"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search("bloodwood"):
        Misc.SendMessage(">> bloodwood!", colors["success"])
        Timer.Create("chopTimer", 10000)
        CutTree()
    elif Journal.Search("heartwood"):
        Misc.SendMessage(">> heartwood!", colors["success"])
        Timer.Create("chopTimer", 10000)
        CutTree()
    elif Journal.Search("frostwood"):
        Misc.SendMessage(">> frostwood!", colors["success"])
        Timer.Create("chopTimer", 10000)
        CutTree()
    else:
        CutTree()


# ---------------------------------------------------------------------
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


def SafteyNet():
    if is_afk_gump():
        Misc.Beep()
        Audio_say("solving AFK Gump")
        button_options = get_afk_gump_button_options()
        if button_options:
            if not solve_afk_gump(button_options):
                Misc.FocusUOWindow()
                sys.exit()

    if runaway is True:
        if IsEnemy() is True:
            Misc.Beep()
            Audio_say("enemy detected")
            RecallNext(runebook, CURRENT_TREE_RUNE, MIN_TREE_RUNE, MAX_TREE_RUNE)

    if alert:
        toon = Mobiles.ApplyFilter(toonFilter)
        invul = Mobiles.ApplyFilter(invulFilter)
        if toon:
            Misc.Beep()
            Misc.FocusUOWindow()
            Audio_say("someone is here")
            toonName = Mobiles.Select(toon, "Nearest")
            if toonName:
                Misc.SendMessage(">> toon near: " + toonName.Name, colors["alert"])
        elif invul:
            Misc.Beep()
            Misc.FocusUOWindow()
            Audio_say("GM here")
            invulName = Mobiles.Select(invul, "Nearest")
            if invulName:
                Misc.SendMessage(">> invul near:" + invul.Name, colors["alert"])
        else:
            Misc.NoOperation()


# ---------------------------------------------------------------------
# main process
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

toonFilter = Mobiles.Filter()
toonFilter.Enabled = True
toonFilter.RangeMin = -1
toonFilter.RangeMax = -1
toonFilter.IsHuman = True
toonFilter.Friend = False
toonFilter.Notorieties = List[Byte](bytes([1, 4, 5, 6]))

invulFilter = Mobiles.Filter()
invulFilter.Enabled = True
invulFilter.RangeMin = -1
invulFilter.RangeMax = -1
invulFilter.Friend = False
invulFilter.Notorieties = List[Byte](bytes([7]))

Friend.ChangeList("lj")
Misc.SendMessage(">> lumberjack starting up...", colors["notice"])

while not Player.IsGhost:
    Misc.Pause(100)
    trees = []
    ScanStatic()

    if not trees or trees.Count == 0:
        Misc.SendMessage(">> no trees found", colors["fatal"])
        Misc.SendMessage(">> going to next zone...", colors["notice"])
        # RecallNext(runebook, CURRENT_TREE_RUNE, MIN_TREE_RUNE, MAX_TREE_RUNE)
        continue

    while trees.Count > 0:
        if Overweight(weightLimit):
            DepositInBank(bankX, bankY)
            break
        if MoveToTree():
            CutTree()
        trees.pop(0)
        trees = sorted(
            trees,
            key=lambda tree: sqrt(
                pow((tree.x - Player.Position.X), 2)
                + pow((tree.y - Player.Position.Y), 2)
            ),
        )