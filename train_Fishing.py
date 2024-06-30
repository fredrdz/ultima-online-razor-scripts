"""
SCRIPT: skill_Fishing.py
Author: Talik Starr
IN:RISEN
Skill: Fishing
"""

# System packages
import sys
import math
import time
from System import Byte
from System import Int32
from System.Collections.Generic import List

# Custom RE packages
import config
import Gumps, Items, Journal, Misc, Mobiles, Player, Statics, Target, Timer
from glossary.colors import colors
from glossary.items.containers import FindHatch
from glossary.items.tools import tools
from utils.magery import CastSpellRepeatably
from utils.items import FindItem, MoveItemsByCount
from utils.item_actions.common import (
    equip_right_hand,
    unequip_hands,
    use_runebook,
)
from utils.status import Overweight
from utils.gumps import is_afk_gump, get_afk_gump_button_options, solve_afk_gump
from utils.actions import Audio_say
from utils.common import Beep

# ---------------------------------------------------------------------
# True will move the boat with the 'foward' and 'backword' commands
# False will move the boat with the 'left' and 'right' commands
moveForwardBackward = True

# spell to cast when an enemy is detected
spellName = "Lightning"

fishCuttingTool = tools["cleaver"]
leatherCuttingTool = tools["scissors"]

fishIDs = [0x09CF, 0x09CE, 0x09CC, 0x09CD]
fishingPole = tools["fishing pole"]
fishingTools = [fishingPole.itemID]

goldID = 0x0EED
leatherID = 0x1081
fishSteakID = 0x097A

depositItems = [
    (goldID, -1),
    (leatherID, -1),
    (fishSteakID, -1),
]

leatherGoods = [
    (0x170B, 0x0000),
    (0x170D, 0x0000),
    (0x170F, 0x0000),
    (0x1711, 0x0000),
]

# ********************
# Parameters
# more than 25 tiles of scanning may crash client
scanRadius = 3
# Water where there is no longer fishes to be harvested will not be revisited until this much time has passed
waterCooldown = 1200000  # 1,200,000 ms is 20 minutes
weightLimit = Player.MaxWeight + 30

waterLandIDs = [
    0x00AA,
    0x00AB,
    0x00A8,
    0x00A9,
    0x0064,
    0x005B,
    0x0053,
]

# ---------------------------------------------------------------------
# do not edit below this line


class Water:
    def __init__(self, x, y, z, id):
        self.X = x
        self.Y = y
        self.Z = z
        self.ID = id


# ---------------------------------------------------------------------
def EquipFishingPole():
    """
    Searches and equips a fishing pole.
    """
    # check if the left hand is equipped and unequip if necessary
    if Player.GetItemOnLayer("LeftHand"):
        unequip_hands()

    # check the right hand and decide the course of action
    right_hand_item = Player.GetItemOnLayer("RightHand")

    if right_hand_item:
        # if the item in the right hand is not a fishing tool, unequip
        if right_hand_item.ItemID not in fishingTools:
            unequip_hands()
        else:
            return True  # the right hand is already holding a fishing tool

    # if no item in the right hand, or item was unequipped, find and equip a fishing pole
    foundItem = FindItem(fishingPole.itemID, Player.Backpack)
    if foundItem:
        equip_right_hand(foundItem.Serial)
        return True

    # fatal error if no fishing pole equipped
    Misc.SendMessage(">> no fishing tools found", colors["fatal"])
    Misc.Beep()
    sys.exit()


def Fishing(tile):
    """
    Casts the fishing pole and returns True while the fish are biting.
    """

    if not isinstance(tile, Water):
        Misc.SendMessage(">> invalid tile", colors["fatal"])
        return False

    global fishIDs

    Journal.Clear()
    if EquipFishingPole() is True:
        Items.UseItem(Player.GetItemOnLayer("RightHand"))

    Target.WaitForTarget(1000, False)
    Target.TargetExecute(tile.X, tile.Y, tile.Z)

    Misc.Pause(config.dragDelayMilliseconds)

    Timer.Create("timeout", 20000)
    while not (
        Journal.SearchByType("You pull", "System")
        or Journal.SearchByType(
            "You fish a while, but fail to catch anything.", "System"
        )
        or Journal.SearchByType("There are no fish here.", "System")
        or Journal.SearchByType(
            "Your fishing pole bends as you pull a big fish from the depths!", "System"
        )
        or Journal.SearchByType("Uh oh! That doesn't look like a fish!", "System")
    ):
        if (
            Timer.Check("timeout") is False
            or Timer.Check(f"{tile.X},{tile.Y}") is True
            or Journal.SearchByType("Target cannot be seen.", "System")
            or Journal.SearchByType("That is too far away.", "System")
        ):
            break
        Misc.Pause(50)

    if Journal.SearchByType(
        "There are no fish here.", "System"
    ) or Journal.SearchByType("Target cannot be seen.", "System"):
        Journal.Clear()
        Timer.Create(f"{tile.X},{tile.Y}", waterCooldown)
        return False

    # cut the fish and leather goods if player is overweight
    if Overweight(weightLimit):
        # create fish steaks
        for fishID in fishIDs:
            fish = Items.FindByID(fishID, -1, Player.Backpack.Serial)
            if fish:
                f_tool = FindItem(fishCuttingTool.itemID, Player.Backpack)
                if not f_tool:
                    # check if tool in right hand
                    if Player.CheckLayer("RightHand"):
                        if (
                            Player.GetItemOnLayer("RightHand").ItemID
                            == fishCuttingTool.itemID
                        ):
                            f_tool = Player.GetItemOnLayer("RightHand")
                if f_tool:
                    Items.UseItem(f_tool.Serial)
                    Target.WaitForTarget(2000, False)
                    Target.TargetExecute(fish)
                    Misc.Pause(config.dragDelayMilliseconds)
        # create leather from shoes
        for backpack_item in Player.Backpack.Contains:
            item_tuple = (backpack_item.ItemID, backpack_item.Hue)
            if item_tuple in leatherGoods:
                good = Items.FindByID(
                    backpack_item.ItemID, backpack_item.Hue, Player.Backpack.Serial
                )
                if good:
                    g_tool = FindItem(leatherCuttingTool.itemID, Player.Backpack)
                    if g_tool:
                        Items.UseItem(g_tool.Serial)
                        Target.WaitForTarget(1000, False)
                        Target.TargetExecute(good)
                        Misc.Pause(config.dragDelayMilliseconds)
        # throw the fish and shoes into the boat's hatch
        hatch = FindHatch()
        if hatch:
            Player.ChatSay(colors["debug"], "stop")
            MoveItemsByCount(depositItems, Player.Backpack.Serial, hatch)

    return True


# ---------------------------------------------------------------------
# safteyNet

fishingMobFilter = Mobiles.Filter()
fishingMobFilter.Enabled = True
fishingMobFilter.RangeMin = 1
fishingMobFilter.RangeMax = 5
fishingMobFilter.CheckLineOfSight = True
fishingMobFilter.Poisoned = -1
fishingMobFilter.IsHuman = -1
fishingMobFilter.IsGhost = False
fishingMobFilter.Warmode = -1
fishingMobFilter.Friend = False
fishingMobFilter.Paralized = -1
fishingMobFilter.Notorieties = List[Byte](bytes([4, 5, 6]))


def IsEnemy():
    enemies = Mobiles.ApplyFilter(fishingMobFilter)
    if not enemies or len(enemies) == 0:
        return None

    nearestEnemy = Mobiles.Select(enemies, "Nearest")

    Mobiles.Message(
        nearestEnemy,
        colors["alert"],
        ">> enemy detected",
    )

    return nearestEnemy


def FightEnemy(target=None):
    CastSpellRepeatably(spellName, target)
    # loot if corpse is found
    corpseFilter = Items.Filter()
    corpseFilter.Movable = False
    corpseFilter.Graphics = List[Int32]([0x2006])
    corpses = Items.ApplyFilter(corpseFilter)
    for corpse in corpses:
        for item in corpse.Contains:
            Items.Move(item, Player.Backpack.Serial, 0)
            Misc.Pause(config.dragDelayMilliseconds)


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
        Timer.Create("tracking_cd", 10000)
        Gumps.WaitForGump(2976808305, 1000)
        if Gumps.CurrentGump() == 2976808305:
            Gumps.SendAction(2976808305, 4)
            Gumps.WaitForGump(993494147, 1000)
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


def IsInvul():
    invul = Mobiles.ApplyFilter(invulFilter)
    if not invul or len(invul) == 0:
        return None

    nearestInvul = Mobiles.Select(invul, "Nearest")

    Misc.SendMessage(">> invul near:" + invul.Name, colors["alert"])
    Mobiles.Message(
        nearestInvul,
        colors["warning"],
        ">> invulnerable detected",
    )

    return nearestInvul


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

    # monitors mobiles and alerts if found
    if IsEnemy():
        Beep(2)
        enemy = IsEnemy()
        FightEnemy(enemy)
    elif IsPlayer():
        Beep(3)
        Audio_say("player is here")
        Misc.FocusUOWindow()
        rb = Misc.ReadSharedValue("young_runebook")
        use_runebook(rb, 1)
        Misc.Pause(2000)
        Player.UseSkill("Hiding", False)
        sys.exit()
    elif IsInvul():
        Beep(4)
        Misc.FocusUOWindow()
        Audio_say("invulnerable here")
        sys.exit()

    # close any gumps that may be opened to avoid issues
    if Gumps.HasGump():
        opened_gump_id = Gumps.CurrentGump()
        Gumps.CloseGump(opened_gump_id)


# ---------------------------------------------------------------------
# bug: may crash client when tree list is too large or too many tiles
def ScanLand(ocean=List[Water]) -> List[Water]:
    # debug
    Misc.SendMessage(f"fish skill: {Player.GetSkillValue('Fishing')}")

    # init
    new_ocean = []

    Misc.Resync()
    Misc.SendMessage(">> scanning tiles...", colors["status"])

    player_position = Player.Position
    minX = player_position.X - scanRadius
    maxX = player_position.X + scanRadius
    minY = player_position.Y - scanRadius
    maxY = player_position.Y + scanRadius

    Misc.SendMessage(">> adding water tiles", colors["status"])
    for x in range(minX, maxX + 1):
        for y in range(minY, maxY + 1):
            staticsLandID = Statics.GetLandID(x, y, Player.Map)
            # might reduce client crash by throttling tile lookups
            time.sleep(0.001)  # 1 milliseconds
            if staticsLandID:
                if Statics.GetLandFlag(staticsLandID, "Wet"):
                    z = Statics.GetLandZ(x, y, Player.Map)
                    if staticsLandID in waterLandIDs and not Timer.Check(f"{x},{y}"):
                        new_ocean.append(Water(x, y, z, staticsLandID))
                        # Player.HeadMessage(
                        #     colors["debug"],
                        #     f"water tile: {x},{y}, {z}, {staticsLandID}",
                        # )

    Misc.SendMessage(">> sorting water tiles", colors["status"])
    new_ocean.sort(
        key=lambda water: math.hypot(
            water.X - player_position.X, water.Y - player_position.Y
        )
    )

    ocean.extend(new_ocean)

    Misc.SendMessage(">> total water tiles: %i" % len(ocean), colors["success"])
    return ocean


# ---------------------------------------------------------------------
def TrainFishing(moveForwardBackward=False):
    """
    Trains Fishing to its skill cap.
    """

    # init skill check
    if Player.GetSkillValue("Fishing") == Player.GetSkillCap("Fishing"):
        Misc.SendMessage(">> maxed out fishing skill", colors["notice"])
        return

    # init vars
    ocean = []
    moveBoatInThisDirection = None
    if moveForwardBackward:
        moveBoatInThisDirection = "forward"
    else:
        moveBoatInThisDirection = "right"

    Misc.SendMessage(">> starting fishing training...", colors["notice"])

    # while skill can increase and player is not dead
    while not Player.IsGhost and Player.GetSkillValue("Fishing") < Player.GetSkillCap(
        "Fishing"
    ):
        # reduce cpu usage
        Misc.Pause(100)

        # scan for water tiles
        ocean = ScanLand(ocean)

        # move boat if nothing to fish
        if not ocean or len(ocean) == 0:
            Misc.SendMessage(">> no fishes around", colors["notice"])
            Misc.SendMessage(">> going to next spot...", colors["notice"])

        # start fishing water tiles in range
        while len(ocean) > 0:
            while Fishing(ocean[0]):
                SafteyNet()
            ocean.pop(0)

        Player.ChatSay(colors["debug"], f"{moveBoatInThisDirection} one")
        Misc.Pause(2000)

        Misc.Pause(config.journalEntryDelayMilliseconds)
        if Journal.Search("Ar, we've stopped sir."):
            Journal.Clear()
            if moveForwardBackward:
                if moveBoatInThisDirection == "forward":
                    moveBoatInThisDirection = "backward"
                else:
                    moveBoatInThisDirection = "forward"
            else:
                if moveBoatInThisDirection == "right":
                    moveBoatInThisDirection = "left"
                else:
                    moveBoatInThisDirection = "right"

    # if here, skill cap reached
    Misc.SendMessage(">> congrats, maxed out Fishing skill", colors["notice"])


# Start Fishing Training
TrainFishing(moveForwardBackward)
