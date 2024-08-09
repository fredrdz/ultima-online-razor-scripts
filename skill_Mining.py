"""
SCRIPT: skill_Mining.py
Author: Talik Starr
IN:RISEN
Skill: Mining
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
from utils.common import Beep
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
    RecallBank,
)
from utils.items import MoveItemsByCount
from utils.status import Overweight
from utils.gumps import is_afk_gump, get_afk_gump_button_options, solve_afk_gump


# ********************
# Tiles where there is no longer enough ore to be harvested will not be revisited until this much time has passed
mineCooldown = 1200000  # 1,200,000 ms is 20 minutes

# Want this script to alert you for GM or prompts?
alert = True
# Want this script to run away from bad guys?
runaway = True

# setting a secure container will disable bank restocking
# will restock from here instead
secureContainer = None

containerInBank = 0x40054709  # Serial of log bag in bank
bankX = 2891
bankY = 675


# slot number in runebook, 1 of 16
runebookSerial = Misc.CheckSharedValue("mining_runebook")
houseRune = 1
bankRune = 2

# Define constants for the minimum and maximum values of tree_rune
MIN_RUNE = 3
MAX_RUNE = 11
CURRENT_RUNE = 3
# ********************

# Parameters
# more than 25 tiles of scanning may crash client
scanRadius = 25

weightLimit = Player.MaxWeight + 30

toolIDs = [0x0F49, 0x13FB, 0x0F47, 0x1443, 0x0F45, 0x0F4B, 0x0F43]

oreID = 0x1BDD
ingotID = 0x1BD7
goldID = 0x0EED

# triplet; (itemID, color, count)
# defaults to natural color of item if tuple
# naturalColor = 0
# anyColor = -1
# anyAmount = -1
depositItems = [
    (ingotID, -1, -1),
    (oreID, -1, -1),
    (goldID, -1),
]

# ---------------------------------------------------------------------
# do not edit below this line


class Tile:
    def __init__(self, x, y, z, id):
        self.x = x
        self.y = y
        self.z = z
        self.id = id


# init
caveTiles = []
humanIgnoreList = []
Timer.Create("tracking_cd", 1)
playerBag = Player.Backpack.Serial

# check for runebook
if not runebookSerial:
    runebookSerial = Target.PromptTarget(">> target your runebook", colors["notice"])

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

caveStatics = [
    0x0C95,
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
    # init
    Journal.Clear()

    # use bank if enabled
    if containerInBank is not None:
        Bank(runebook, rune, x, y)

    # get container as an item class
    containerItem = Items.FindBySerial(restockContainer)
    if not containerItem:
        Misc.SendMessage(">> restocking container not found", colors["fatal"])
        PlayerHideAndExit()

    # some chopping if logs in player bag
    while Items.BackpackCount(oreID) > 0:
        Smelt()

    # open the container to load contents into memory
    if containerItem.IsContainer:
        Items.UseItem(containerItem)

    # deposit items in container
    MoveItemsByCount(depositItems, playerBag, restockContainer)

    # fatal error if container is full
    if Journal.SearchByType("That container cannot hold more weight.", "System"):
        Misc.SendMessage(">> container is full", colors["fatal"])
        PlayerHideAndExit()

    # restock
    recallSpell = spellReagents.get("Recall", [])
    restockItems = []
    for reg in recallSpell:
        restockItems.append((reg.itemID, 10))
    if Restock(restockItems, restockContainer) is False:
        Misc.SendMessage(">> failed to restock necessary items", colors["fatal"])
        PlayerHideAndExit()


def PlayerHideAndExit():
    Misc.ScriptStop("_watcher.py")
    Player.UseSkill("Hiding", False)
    sys.exit()


# ---------------------------------------------------------------------
# bug: may crash client when tree list is too large or too many tiles
def ScanStatic(tiles=List[Tile]) -> List[Tile]:
    new_tiles = []

    Misc.Resync()
    Misc.SendMessage(">> scanning tiles...", colors["status"])

    player_position = Player.Position
    minX = player_position.X - scanRadius
    maxX = player_position.X + scanRadius
    minY = player_position.Y - scanRadius
    maxY = player_position.Y + scanRadius

    Misc.SendMessage(">> adding tiles", colors["status"])
    for x in range(minX, maxX + 1):
        for y in range(minY, maxY + 1):
            staticsTileInfo = Statics.GetStaticsTileInfo(x, y, Player.Map)
            # might reduce client crash by throttling tile lookups
            time.sleep(0.001)  # 1 milliseconds
            if staticsTileInfo:
                for tile in staticsTileInfo:
                    if tile.StaticID in caveStatics and not Timer.Check(f"{x},{y}"):
                        new_tiles.append(Tile(x, y, tile.StaticZ, tile.StaticID))

    Misc.SendMessage(">> sorting tiles", colors["status"])
    new_tiles.sort(
        key=lambda tree: math.hypot(
            tree.x - player_position.X, tree.y - player_position.Y
        )
    )

    tiles.extend(new_tiles)

    Misc.SendMessage(">> total trees: %i" % len(tiles), colors["success"])
    return tiles


# ---------------------------------------------------------------------
def MoveToTile():
    if not caveTiles or len(caveTiles) == 0:
        return False

    tX = caveTiles[0].x
    tY = caveTiles[0].y

    if PathCount(tX, tY) > 50:
        Misc.SendMessage(f">> tile too far away: {tX}, {tY}", colors["warning"])
        return False

    Misc.SendMessage(f">> moving to tile: {tX}, {tY}", colors["status"])

    actionOffset = PlayerDiagonalOffset(tX, tY)
    if not actionOffset:
        return False

    actionX, actionY = actionOffset
    if RazorPathing(actionX, actionY) is False:
        Misc.SetSharedValue("pathFindingOverride", (actionX, actionY))
        Misc.ScriptRun("pathfinding.py")

    # init timeouts
    Timer.Create("pathing", 10000)
    Timer.Create("safteyNet", 1)

    # wait for position to be reached until t/o
    while IsPosition(actionX, actionY) is False and Timer.Check("pathing") is True:
        Misc.Pause(random.randint(50, 150))
        if Timer.Check("safteyNet") is False:
            SafetyNet()
            Timer.Create("safteyNet", 1000)

    # if pathfinding script is still running after t/o, stop it
    if Timer.Check("pathing") is False:
        if Misc.ScriptStatus("pathfinding.py"):
            Misc.ScriptStop("pathfinding.py")
        Misc.SendMessage(">> pathlocked, resetting", colors["error"])
        Misc.SendMessage(f">> failed to reach tile: {tX}, {tY}", colors["error"])
        return False

    # if here, we succeeded in reaching the tree
    Misc.SendMessage(f">> reached tile: {tX}, {tY}", colors["notice"])
    return True


# ---------------------------------------------------------------------
def Smelt():
    EquipTool()
    for item in Player.Backpack.Contains:
        if item.ItemID == oreID:
            Items.UseItem(Player.GetItemOnLayer("LeftHand"))
            Target.WaitForTarget(1000, False)
            Target.TargetExecute(item)
            Misc.Pause(300)


def EquipTool():
    if Player.CheckLayer("RightHand"):
        unequip_hands()
    elif Player.CheckLayer("LeftHand"):
        if Player.GetItemOnLayer("LeftHand").ItemID not in toolIDs:
            unequip_hands()

    if not Player.CheckLayer("LeftHand"):
        for item in Player.Backpack.Contains:
            if item.ItemID in toolIDs:
                equip_left_hand(item.Serial)
                break
        if not Player.CheckLayer("LeftHand"):
            Misc.SendMessage(">> no tools found", colors["fatal"])
            Misc.Beep()
            PlayerHideAndExit()


def Mine():
    if Target.HasTarget():
        Misc.SendMessage(">> detected target cursor, refreshing...", colors["warning"])
        Target.Cancel()
        Misc.Pause(500)

    if Overweight(weightLimit):
        return

    Journal.Clear()

    EquipTool()
    Items.UseItem(Player.GetItemOnLayer("LeftHand"))
    Target.WaitForTarget(3000, True)
    Target.TargetExecute(
        caveTiles[0].x, caveTiles[0].y, caveTiles[0].z, caveTiles[0].id
    )

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

    # safteyNet runs every second in between chops
    if Timer.Check("safteyNet") is False:
        SafetyNet()
        Timer.Create("safteyNet", 1000)

    # if here, we are not chopping, so we do checks
    if Journal.SearchByType("There's not enough wood here to harvest.", "System"):
        Misc.SendMessage(">> no wood here", colors["status"])
        Misc.SendMessage(">> tree change", colors["status"])
        Timer.Create("%i,%i" % (caveTiles[0].x, caveTiles[0].y), mineCooldown)
    elif Journal.Search("That is too far away"):
        Misc.SendMessage(">> blocked; cannot target", colors["warning"])
        Timer.Create("%i,%i" % (caveTiles[0].x, caveTiles[0].y), mineCooldown)
    elif Journal.Search("Target cannot be seen"):
        Misc.SendMessage(">> blocked; cannot target", colors["warning"])
        Timer.Create("%i,%i" % (caveTiles[0].x, caveTiles[0].y), mineCooldown)
    elif Timer.Check("chop_timeout") is False:
        Misc.SendMessage(">> tree change", colors["status"])
        Timer.Create("%i,%i" % (caveTiles[0].x, caveTiles[0].y), mineCooldown)
    elif Journal.Search("bloodwood"):
        Misc.SendMessage(">> bloodwood!", colors["status"])
        Timer.Create("chop_timeout", 10000)
        Mine()
    elif Journal.Search("heartwood"):
        Misc.SendMessage(">> heartwood!", colors["status"])
        Timer.Create("chop_timeout", 10000)
        Mine()
    elif Journal.Search("frostwood"):
        Misc.SendMessage(">> frostwood!", colors["status"])
        Timer.Create("chop_timeout", 10000)
        Mine()
    else:
        Mine()


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
        colors["alert"],
        ">> enemy detected <<",
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


def IsPlayer() -> bool:
    # init
    global humanIgnoreList

    # run mobile filter: short range human detection
    humans = Mobiles.ApplyFilter(playerFilter)

    # add human NPCs to ignore list or return true if player
    if len(humans) > 0:
        for i in range(len(humans) - 1, -1, -1):
            h = humans[i]
            if h.Serial not in humanIgnoreList:
                Misc.SendMessage(">> human nearby <<", colors["alert"])
                # tracking skill used to confirm if player
                Misc.SendMessage(">> checking if player...", colors["alert"])
                Player.UseSkill("Tracking", False)
                Gumps.WaitForGump(2976808305, 2000)
                # button 4 for checking for players
                if Gumps.CurrentGump() == 2976808305:
                    Gumps.SendAction(2976808305, 4)
                    Gumps.WaitForGump(993494147, 2000)
                    # player gump shows if any found
                    if Gumps.CurrentGump() == 993494147:
                        Misc.SendMessage(">> found players", colors["alert"])
                        player_list = Gumps.LastGumpGetLineList()
                        if player_list:
                            player_list = [str(line) for line in player_list]
                            for player in player_list:
                                Misc.SendMessage(f"-- {player}", colors["alert"])
                            Gumps.CloseGump(993494147)
                            return True
                    else:
                        humanIgnoreList.append(h.Serial)
    return False


invulFilter = Mobiles.Filter()
invulFilter.Enabled = True
invulFilter.RangeMin = -1
invulFilter.RangeMax = -1
invulFilter.Friend = False
invulFilter.Notorieties = List[Byte](bytes([7]))


def SafetyNet():
    # init
    global CURRENT_RUNE

    # checks runaway flag; recalls away from enemies if detected
    if runaway is True:
        if IsEnemy() is True:
            Beep(2)
            Audio_say("enemy detected")
            CURRENT_RUNE = RecallNext(runebookSerial, CURRENT_RUNE, MIN_RUNE, MAX_RUNE)
        if IsPlayer() is True:
            Beep(3)
            Audio_say("player is here")
            CURRENT_RUNE = RecallNext(runebookSerial, CURRENT_RUNE, MIN_RUNE, MAX_RUNE)

    # monitors mobiles and alerts if found
    if alert:
        invul = Mobiles.ApplyFilter(invulFilter)
        # tries to auto solve afk gump or alerts if it fails
        if is_afk_gump():
            Beep()
            button_options = get_afk_gump_button_options()
            if button_options:
                if not solve_afk_gump(button_options):
                    Audio_say("solve AFK Gump")
                    Misc.FocusUOWindow()
                    PlayerHideAndExit()
        if invul:
            Beep(4)
            Misc.FocusUOWindow()
            Audio_say("GM here")
            invulName = Mobiles.Select(invul, "Nearest")
            if invulName:
                Misc.SendMessage(">> invul near:" + invul.Name, colors["alert"])
            sys.exit()

    # close any gumps that may be opened to avoid issues
    if Gumps.HasGump():
        opened_gump_id = Gumps.CurrentGump()
        Gumps.CloseGump(opened_gump_id)


# ---------------------------------------------------------------------
# main process
Misc.SendMessage(">> mining script starting...", colors["notice"])
DepositAndRestock(runebookSerial, bankRune, bankX, bankY)
CURRENT_RUNE = RecallNext(runebookSerial, CURRENT_RUNE, MIN_RUNE, MAX_RUNE)

while not Player.IsGhost:
    Misc.Pause(100)
    caveTiles = ScanStatic(caveTiles)

    if not caveTiles or len(caveTiles) == 0:
        Misc.SendMessage(">> no tiles found", colors["fatal"])
        Misc.SendMessage(">> going to next zone...", colors["notice"])
        CURRENT_RUNE = RecallNext(runebookSerial, CURRENT_RUNE, MIN_RUNE, MAX_RUNE)
        continue

    while len(caveTiles) > 0:
        if Overweight(weightLimit):
            DepositAndRestock(runebookSerial, bankRune, bankX, bankY)
            CURRENT_RUNE = RecallNext(runebookSerial, CURRENT_RUNE, MIN_RUNE, MAX_RUNE)
            break
        if MoveToTile():
            Mine()
        caveTiles.pop(0)
        caveTiles.sort(
            key=lambda tile: math.hypot(
                tile.x - Player.Position.X, tile.y - Player.Position.Y
            )
        )
