# SCRIPT: lumberjacking.py
# Author: Talik Starr
# IN:RISEN
# Skill: Lumberjacking

# custom RE packages
from glossary.colors import colors
from utils.actions import Bank
from utils.items import MoveItemsByCount, RestockAgent
from utils.magery import Recall
from utils.status import Overweight

# System packages
import sys
import random
from System.Collections.Generic import List
from System import Byte
from math import sqrt
import clr

clr.AddReference("System.Speech")
from System.Speech.Synthesis import SpeechSynthesizer


# ********************
# you want boards or logs?
logsToBoards = False

# Trees where there is no longer enough wood to be harvested will not be revisited until this much time has passed
treeCooldown = 1200000  # 1,200,000 ms is 20 minutes

# Want this script to alert you for humaniods?
alert = True
# ********************

# Parameters
scanRadius = 40
afkGumpID = 408109089
EquipAxeDelay = 1000
TimeoutOnWaitAction = 3000
ChopDelay = 1000
dragDelay = 600

weightLimit = Player.MaxWeight + 30
backpack = Player.Backpack.Serial
logBag = 0x40054709  # Serial of log bag in bank
bankX = 3698
bankY = 2514
bankRune = 0x400BAAB7

# rightHand = Player.CheckLayer('RightHand')
leftHand = Player.CheckLayer("LeftHand")
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
# System Variables
blockCount = 0
onLoop = True


# Custom Classes
class Tree:
    x = None
    y = None
    z = None
    id = None

    def __init__(self, x, y, z, id):
        self.x = x
        self.y = y
        self.z = z
        self.id = id


# ---------------------------------------------------------------------
def DepositInBank():
    Recall(bankRune)
    Bank(bankX, bankY)
    Journal.Clear()

    RestockAgent("lj")
    Misc.Pause(3000)

    RestockAgent("recall")
    Misc.Pause(3000)

    CutLogs()
    Misc.Pause(3000)

    MoveItemsByCount(bankDeposit, backpack, logBag)
    Misc.Pause(3000)

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

    chopX = trees[0].x + 1
    chopY = trees[0].y
    Misc.SetSharedValue("pathFindingOverride", (chopX, chopY))
    Misc.ScriptRun("pathfinding.py")

    Timer.Create("path_timeout", 10000)
    while Misc.Distance(Player.Position.X, Player.Position.Y, chopX, chopY) != 0:
        Misc.Pause(100)
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
    for item in Player.Backpack.Contains:
        if item.ItemID == logID:
            Items.UseItem(axeSerial)
            Target.WaitForTarget(1000, False)
            Target.TargetExecute(item)
            Misc.Pause(200)


# ---------------------------------------------------------------------
def EquipAxe():
    global axeSerial

    if not leftHand:
        for item in Player.Backpack.Contains:
            if item.ItemID in axeList:
                Player.EquipItem(item.Serial)
                Misc.Pause(600)
                axeSerial = Player.GetItemOnLayer("LeftHand").Serial
    elif Player.GetItemOnLayer("LeftHand").ItemID in axeList:
        axeSerial = Player.GetItemOnLayer("LeftHand").Serial
    else:
        Player.HeadMessage(35, "You must have an axe to chop trees!")
        Misc.Pause(1000)


# ---------------------------------------------------------------------
def CutTree():
    global blockCount
    if Target.HasTarget():
        Misc.SendMessage(">> detected target cursor, refreshing...", colors["notice"])
        Target.Cancel()
        Misc.Pause(500)

    if Overweight(weightLimit):
        return

    Journal.Clear()

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
        Misc.Pause(random.randint(50, 150))

    if Journal.SearchByType("There's not enough wood here to harvest.", "System"):
        Misc.SendMessage(">> no wood here", colors["status"])
        Misc.SendMessage(">> tree change", colors["status"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search("That is too far away"):
        blockCount = blockCount + 1
        Journal.Clear()
        if blockCount > 1:
            blockCount = 0
            Misc.SendMessage(">> blocked; cannot target", colors["warning"])
            Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
        else:
            CutTree()
    elif Journal.Search("Target cannot be seen"):
        blockCount = blockCount + 1
        Journal.Clear()
        if blockCount > 1:
            blockCount = 0
            Misc.SendMessage(">> blocked; cannot target", colors["warning"])
            Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
        else:
            CutTree()
    elif not Timer.Check("chopTimer"):
        Misc.SendMessage(">> tree change", colors["status"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search("bloodwood"):
        Player.HeadMessage(1194, "BLOODWOOD!")
        Timer.Create("chopTimer", 10000)
        CutTree()
    elif Journal.Search("heartwood"):
        Player.HeadMessage(1193, "HEARTWOOD!")
        Timer.Create("chopTimer", 10000)
        CutTree()
    elif Journal.Search("frostwood"):
        Player.HeadMessage(1151, "FROSTWOOD!")
        Timer.Create("chopTimer", 10000)
        CutTree()
    else:
        CutTree()


# ---------------------------------------------------------------------
# def filterItem(id, range=2, movable=True):
#     fil = Items.Filter()
#     fil.Movable = movable
#     fil.RangeMax = range
#     fil.Graphics = List[int](id)
#     list = Items.ApplyFilter(fil)
#     return list


# ---------------------------------------------------------------------
def is_afk_gump():
    if Gumps.HasGump(afkGumpID):
        return True
    return False


def get_afk_gump_button_options():
    gump_text_options = Gumps.LastGumpGetLineList()
    if gump_text_options:
        return [str(line) for line in gump_text_options]
    return None


def solve_afk_gump(text_list):
    result_list = []
    current_word = ""

    for text in text_list:
        if isinstance(text, str):
            text = text.strip()
            if text:
                if "rightbutton" in text.lower():
                    result_list.append("Right Button")
                elif "wrongbutton" in text.lower():
                    result_list.append("Wrong Button")
                else:
                    current_word += text
                    if "rightbutton" in current_word.lower():
                        result_list.append("Right Button")
                        current_word = ""
                    elif "wrongbutton" in current_word.lower():
                        result_list.append("Wrong Button")
                        current_word = ""

    right_button_index = (
        result_list.index("Right Button") if "Right Button" in result_list else -1
    )

    if isinstance(right_button_index, int):
        if right_button_index != -1:
            Misc.SendMessage(
                ">> afk gump -Right Button- found at index: %i" % right_button_index,
                colors["info"],
            )
            Misc.Pause(random.randint(1000, 2000))
            Gumps.SendAction(afkGumpID, right_button_index)
            Gumps.CloseGump(afkGumpID)
            return True
        else:
            Misc.SendMessage(
                ">> afk gump -Right Button- not found; solve manually or die",
                colors["fatal"],
            )
    return False


# ---------------------------------------------------------------------
def say(text):
    spk = SpeechSynthesizer()
    spk.Speak(text)


# ---------------------------------------------------------------------
def safteyNet():
    if is_afk_gump():
        Misc.Beep()
        say("solving AFK Gump")
        button_options = get_afk_gump_button_options()
        if button_options:
            if not solve_afk_gump(button_options):
                Misc.FocusUOWindow()
                sys.exit()

    if alert:
        toon = Mobiles.ApplyFilter(toonFilter)
        invul = Mobiles.ApplyFilter(invulFilter)
        if toon:
            Misc.Beep()
            Misc.FocusUOWindow()
            say("someone is here")
            toonName = Mobiles.Select(toon, "Nearest")
            if toonName:
                Misc.SendMessage(">> toon near: " + toonName.Name, colors["alert"])
        elif invul:
            Misc.Beep()
            Misc.FocusUOWindow()
            say("GM here")
            invulName = Mobiles.Select(invul, "Nearest")
            if invulName:
                Misc.SendMessage(">> invul near:" + invul.Name, colors["alert"])
        else:
            Misc.NoOperation()


# ---------------------------------------------------------------------
# main process

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
EquipAxe()

while onLoop:
    Misc.Pause(100)
    trees = []
    ScanStatic()

    if not trees or trees.Count == 0:
        Misc.SendMessage(">> no trees found, waiting...", colors["fail"])
        Misc.Pause(10000)
        continue

    while trees.Count > 0:
        safteyNet()
        if Overweight(weightLimit):
            DepositInBank()
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
