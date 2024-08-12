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
from System import Int32
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
)
from utils.actions import Chat_on_position, Audio_say
from utils.item_actions.common import (
    unequip_hands,
    RecallNext,
    RecallBank,
)
from utils.items import MoveItemsByCount
from utils.status import Overweight
from utils.gumps import is_afk_gump, get_afk_gump_button_options, solve_afk_gump


# ********************

# Tiles where there is no longer enough ore to be harvested will not be revisited until this much time has passed
mineCooldown = 300000  # 5 minutes

# Want this script to alert you for GM or prompts?
alert = True

# Want this script to run away from bad guys?
runaway = True

# Stealth mining? Will use stealth skill to hide while mining if true
stealth = True

# restock/deposit container:
# house or bank, only one can be set
# setting a house container will override bank functions; won't call "bank" or use bank rune
# set the one not in use to: None
# if both are set, house will be used
containerInHouse = 0x4011E131
containerInBank = None

# use ".where" chat command to find bank coordinates
# the player will chat "bank" only on these coordinates
# only used if a container in bank is set
# vesper bank
bankX = 2891
bankY = 675

# runebook used for traveling to house or bank and mining locations
runebookSerial = 0x4003835F
# slot number in runebook; use from 1 to 16
# 1 = first rune, 16 = last rune
# as mentioned above, only one of the two will be used depending on container
houseRune = 1
bankRune = 2

# these set the runebook slot ranges w/ mining locations
# the MIN_RUNE should be the first mining location and the MAX_RUNE the last
MIN_RUNE = 3
MAX_RUNE = 9
# CURRENT_RUNE should be the first mining location to start there
CURRENT_RUNE = MIN_RUNE

# ********************

# Parameters
# more than 25 tiles of scanning may crash client
scanRadius = 25

weightLimit = Player.MaxWeight + 20

toolIDs = [0x0E86, 0x0F39]  # pickaxe, shovel
ingotID = 0x1BEF
goldID = 0x0EED

# triplet; (itemID, color, count)
# defaults to natural color of item if tuple
# naturalColor = 0
# anyColor = -1
# anyAmount = -1
depositItems = [
    (ingotID, -1, -1),
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
playerBag = Player.Backpack.Serial

# ---
# validate runebook
if not runebookSerial or not isinstance(runebookSerial, int):
    Misc.SendMessage(">> no runebook serial set", colors["fatal"])
    sys.exit()

# validate house rune
if not houseRune or not isinstance(houseRune, int):
    # checks if number is within range: 1-16
    if not 1 <= houseRune <= 16:
        Misc.SendMessage(">> no house rune set", colors["warning"])
        Misc.SendMessage(">> setting house rune to runebook slot 1", colors["warning"])
        houseRune = 1

# validate bank rune
if not bankRune or not isinstance(bankRune, int):
    # checks if number is within range: 1-16
    if not 1 <= houseRune <= 16:
        Misc.SendMessage(">> no bank rune set", colors["warning"])
        Misc.SendMessage(">> setting bank rune to runebook slot 2", colors["warning"])
        bankRune = 2

# ---
# validate/set transfers container and transfers rune
if isinstance(containerInHouse, int):
    # use house
    transfersContainer = containerInHouse
    transfersRune = houseRune
    transfersType = "house"
elif isinstance(containerInBank, int):
    # use bank
    transfersContainer = containerInBank
    transfersRune = bankRune
    transfersType = "bank"
else:
    Misc.SendMessage(">> no valid transfers container set", colors["fatal"])
    Misc.SendMessage(">> set either house or bank container", colors["fatal"])
    sys.exit()
# ---

caveStatics = [
    # cave floor
    0x053A,
    0x053B,
    0x053C,
    0x053D,
    0x053E,
    0x053F,
    0x0540,
    0x0541,
    0x0542,
    0x0543,
    0x0544,
    0x0545,
    0x0546,
    0x0547,
    0x0548,
    0x0549,
    0x054A,
    0x054B,
    0x054C,
    0x054D,
    0x054E,
    0x054F,
]


# ---------------------------------------------------------------------
def Deposit(itemList, dst, src=Player.Backpack.Serial):
    # validations
    if not itemList:
        Misc.SendMessage(">> no items set for deposit", colors["fatal"])
        return

    if dst is None or not isinstance(dst, int):
        Misc.SendMessage(">> no destination container specified", colors["fatal"])
        return

    # get container as an item class
    containerItem = Items.FindBySerial(dst)
    if not containerItem:
        Misc.SendMessage(">> deposit container not found", colors["fatal"])
        PlayerHideAndExit()

    # open the container to load contents into memory
    if containerItem.IsContainer:
        Items.UseItem(containerItem)

    # init
    Journal.Clear()

    # deposit items in container
    MoveItemsByCount(itemList, src, dst)

    # fatal error if container is full
    if Journal.SearchByType("That container cannot hold more weight.", "System"):
        Misc.SendMessage(">> container is full", colors["fatal"])
        PlayerHideAndExit()


def Restock(itemList, src, dst=Player.Backpack.Serial):
    # validations
    if not itemList:
        Misc.SendMessage(">> no items requested for restock", colors["fatal"])
        return False

    if src is None or not isinstance(src, int):
        Misc.SendMessage(">> no source container specified", colors["fatal"])
        return False

    # get container as an item class
    containerItem = Items.FindBySerial(src)
    if not containerItem:
        Misc.SendMessage(">> restock container not found", colors["fatal"])
        PlayerHideAndExit()

    # open the container to load contents into memory
    if containerItem.IsContainer:
        Items.UseItem(containerItem)

    # check if enough to restock and calculate difference
    difference = []
    for id, required_count in itemList:
        src_count = Items.ContainerCount(src, id)
        if src_count <= required_count:
            return False

        dst_count = Items.BackpackCount(id)
        if dst_count < required_count:
            difference.append((id, required_count - dst_count))

    # if no difference, then no items need restocking
    if not difference:
        Misc.SendMessage(">> no items need restocking", colors["success"])
        return True

    # restock items to destination
    MoveItemsByCount(difference, src, dst)

    return True


def DepositAndRestock():
    # deposit
    Deposit(depositItems, transfersContainer, playerBag)

    # restock
    recallSpell = spellReagents.get("Recall", [])
    restockItems = []
    for reg in recallSpell:
        restockItems.append((reg.itemID, 10))

    if Restock(restockItems, transfersContainer, playerBag) is False:
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

    Misc.SendMessage(">> total tiles: %i" % len(tiles), colors["success"])
    return tiles


# ---------------------------------------------------------------------
def MoveToTile(tX, tY, offset=False):
    # if tx or tY are not ints or valid coordinates, return false
    if not isinstance(tX, int) or not isinstance(tY, int):
        return False

    if PathCount(tX, tY) > 50:
        Misc.SendMessage(f">> tile too far away: {tX}, {tY}", colors["warning"])
        return False

    path_config = {
        "search_statics": False,
        "player_house_filter": True,
        "items_filter": {
            "Enabled": True,
        },
        "mobiles_filter": {
            "Enabled": True,
        },
    }

    # offset player position by 1 if offset is true
    if offset:
        tX, tY = PlayerDiagonalOffset(tX, tY, path_config)

    Misc.SendMessage(f">> moving to tile: {tX}, {tY}", colors["status"])
    Misc.SetSharedValue("pathFindingOverride", (tX, tY))
    Misc.SetSharedValue("pathFindingConfig", path_config)
    Misc.ScriptRun("pathfinding.py")

    # init timeouts
    Timer.Create("pathing", 10000)
    Timer.Create("safteyNet", 1)

    # wait while pathfinding script is running or until t/o
    while Misc.ScriptStatus("pathfinding.py") is True:
        Misc.Pause(random.randint(50, 150))
        if Timer.Check("safteyNet") is False:
            SafetyNet()
            Timer.Create("safteyNet", 1000)
        elif Timer.Check("pathing") is False:
            Misc.SendMessage(">> pathing timed out", colors["fail"])
            Misc.ScriptStop("pathfinding.py")
            return False

    # check if we reached the tile
    if IsPosition(tX, tY) is False:
        Misc.SendMessage(">> pathlocked, resetting", colors["error"])
        Misc.SendMessage(f">> failed to reach tile: {tX}, {tY}", colors["fail"])
        return False

    # if here, we succeeded in reaching the tile
    Misc.SendMessage(f">> reached tile: {tX}, {tY}", colors["notice"])
    return True


# ---------------------------------------------------------------------
def FindForge(radius=10):
    """
    Locates a forge within reach.
    """

    forgeFilter = Items.Filter()
    forgeFilter.OnGround = 1
    forgeFilter.Movable = False
    forgeFilter.RangeMin = 0
    forgeFilter.RangeMax = radius
    forgeFilter.Graphics = List[Int32]([0x0FB1, 0x197E, 0x199E, 0x19A2, 0x197A])

    forge = Items.ApplyFilter(forgeFilter)

    if len(forge) >= 1:
        return forge[0]

    return None


def FindTool(tools=List[int]):
    # if tools are found in the backpack, return the first tool
    for item in Player.Backpack.Contains:
        if item.ItemID in tools:
            return item

    # check if holding a tool in hands
    if Player.CheckLayer("RightHand"):
        unequip_hands()
    elif Player.CheckLayer("LeftHand"):
        if Player.GetItemOnLayer("LeftHand").ItemID not in tools:
            unequip_hands()

    if not Player.CheckLayer("LeftHand"):
        for item in Player.Backpack.Contains:
            if item.ItemID in tools:
                return item
        if not Player.CheckLayer("LeftHand"):
            return None


def HaveOres():
    # init
    ores = [0x19B9, 0x19B7, 0x19BA, 0x19B8]

    for ore in ores:
        if Items.BackpackCount(ore) > 0:
            return True

    return False


def Smelt(forge):
    # init
    Timer.Create("smelt_timeout", 10000)

    # validate
    if not forge:
        return

    # if forge within 3 tiles, smelt ores
    if PathCount(forge.Position.X, forge.Position.Y) <= 4:
        Misc.SendMessage(">> smelting ores...", colors["status"])
        ores = [0x19B9, 0x19B7, 0x19BA, 0x19B8]
        for ore in ores:
            while Items.BackpackCount(ore) > 0:
                Items.UseItemByID(ore)
                Misc.Pause(500)
                # infinte loop check
                if Timer.Check("smelt_timeout") is False:
                    Misc.SendMessage(">> smelting timed out", colors["error"])
                    return


def Mine(count=0):
    # use stealth if enabled
    if stealth and Player.Visible:
        Player.UseSkill("Stealth", False)
        Misc.Pause(2000)

    # check for target cursor, cancel if found
    if Target.HasTarget():
        Misc.SendMessage(">> detected target cursor, refreshing...", colors["warning"])
        Target.Cancel()
        Misc.Pause(500)

    # mining func is recursive, so we check between attempts
    if Overweight(weightLimit):
        return

    # check if we are stuck in an infinite loop
    if count > 10:
        Misc.SendMessage(">> stuck in loop; resetting", colors["warning"])
        return

    # init
    Journal.Clear()

    # find mining tool; hide and stop script if none
    tool = FindTool(toolIDs)
    if not tool:
        Misc.SendMessage(">> no tools found", colors["fatal"])
        Misc.Beep()
        PlayerHideAndExit()

    # use tool to mine cave tile
    Items.UseItem(tool.Serial)
    Target.WaitForTarget(3000, True)
    Target.TargetExecute(
        caveTiles[0].x, caveTiles[0].y, caveTiles[0].z, caveTiles[0].id
    )

    # init timers
    Timer.Create("mine_timeout", 10000)
    Timer.Create("safteyNet", 1)

    # wait for tile to be mined until t/o
    while not (
        Journal.SearchByType("You dig some", "System")  # success
        or Journal.SearchByType("You loosen some", "System")  # fail
        or Journal.SearchByType("There is no metal", "System")  # done
        or Journal.Search("Target cannot be seen")  # error1
        or Journal.Search("That is too far away")  # error2
        or not Timer.Check("mine_timeout")
    ):
        Misc.Pause(100)

    # safteyNet runs every second in between swings
    if Timer.Check("safteyNet") is False:
        SafetyNet()
        Timer.Create("safteyNet", 1000)

    # if here, we are not mining, so we do checks
    if Journal.SearchByType("There is no metal", "System"):
        Misc.SendMessage(">> no ore here", colors["status"])
        Misc.SendMessage(">> tile change", colors["status"])
        Timer.Create("%i,%i" % (caveTiles[0].x, caveTiles[0].y), mineCooldown)
    elif Journal.Search("That is too far away"):
        Misc.SendMessage(">> blocked; cannot target", colors["warning"])
        Timer.Create("%i,%i" % (caveTiles[0].x, caveTiles[0].y), mineCooldown)
    elif Journal.Search("Target cannot be seen"):
        Misc.SendMessage(">> blocked; cannot target", colors["warning"])
        Timer.Create("%i,%i" % (caveTiles[0].x, caveTiles[0].y), mineCooldown)
    elif Timer.Check("mine_timeout") is False:
        Misc.SendMessage(">> tile change", colors["status"])
        Timer.Create("%i,%i" % (caveTiles[0].x, caveTiles[0].y), mineCooldown)
    elif Journal.Search("sapphire"):
        Misc.SendMessage(">> sapphire!", colors["status"])
        Timer.Create("mine_timeout", 10000)
        Mine()
    else:
        Mine(count + 1)


# ---------------------------------------------------------------------
# safteyNet

enemyFilter = Mobiles.Filter()
enemyFilter.Enabled = True
enemyFilter.RangeMin = 0
enemyFilter.RangeMax = 30
enemyFilter.CheckLineOfSight = True
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
        for human in humans:
            if human.Serial not in humanIgnoreList:
                Misc.SendMessage(">> human nearby <<", colors["alert"])
                Misc.SendMessage(">> checking if player...", colors["alert"])
                # tracking skill used to confirm if player
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
            if human.Serial not in humanIgnoreList:
                # add to ignore list if not player
                Misc.SendMessage(f">> {human.Name} is not a player", colors["debug"])
                Misc.SendMessage(">> adding to ignore list", colors["debug"])
                humanIgnoreList.append(human.Serial)
                Misc.Pause(1000)  # skill wait
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

    # close gumps that may be opened to avoid issues
    if Gumps.CurrentGump() == 0xB16E7D71:
        Gumps.CloseGump(0xB16E7D71)  # tracking gump
    if Gumps.CurrentGump() == 0x554B87F3:
        Gumps.CloseGump(0x554B87F3)  # runebook gump


# ---------------------------------------------------------------------
Misc.SendMessage(">> mining script starting...", colors["notice"])
# deposit/restock if tranfers container is nearby
if Items.FindBySerial(transfersContainer):
    Items.UseItem(transfersContainer)
    DepositAndRestock()

# main process loop
while not Player.IsGhost:
    SafetyNet()
    Misc.Pause(100)
    caveTiles = ScanStatic(caveTiles)

    if not caveTiles or len(caveTiles) == 0:
        Misc.SendMessage(">> no tiles found", colors["fatal"])
        Misc.SendMessage(">> going to next zone...", colors["notice"])
        CURRENT_RUNE = RecallNext(runebookSerial, CURRENT_RUNE, MIN_RUNE, MAX_RUNE)
        continue

    while len(caveTiles) > 0:
        if Overweight(weightLimit) and HaveOres():
            Misc.SendMessage(">> overweight w/ ores", colors["warning"])
            forge = FindForge(20)
            if forge:
                MoveToTile(forge.Position.X, forge.Position.Y, True)
                Smelt(forge)
        if Overweight(weightLimit):
            Misc.SendMessage(">> overweight, going to deposit", colors["warning"])
            # use runebook to recall close to deposit/restock location
            RecallBank(runebookSerial, transfersRune)
            Misc.Pause(3000)  # wait a bit to let things load
            # banking if enabled; moves to position and chats "bank"
            if transfersType == "bank":
                if MoveToTile(bankX, bankY):
                    Chat_on_position("bank", (bankX, bankY))
            # smelt ores before deposit if forge is nearby
            forge = FindForge(20)
            if forge:
                Smelt(forge)
            # deposit ingots and restock recall regs
            DepositAndRestock()
            # go to next mining location
            CURRENT_RUNE = RecallNext(runebookSerial, CURRENT_RUNE, MIN_RUNE, MAX_RUNE)
            break
        if MoveToTile(caveTiles[0].x, caveTiles[0].y):
            Mine()
        caveTiles.pop(0)
        caveTiles.sort(
            key=lambda tile: math.hypot(
                tile.x - Player.Position.X, tile.y - Player.Position.Y
            )
        )
