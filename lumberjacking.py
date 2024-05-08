# SCRIPT: lumberjacking.py
# Author: Talik Starr
# IN:RISEN
# Skill: Lumberjacking

# custom RE packages
from glossary.colors import colors
from utils.actions import Bank
from utils.items import MoveItemsByCount, RestockAgent
from utils.magery import Recall
from utils.pathing import Pathing
from utils.status import Overweight

# System packages
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
scanRadius = 30
afkGumpID = 408109089
EquipAxeDelay = 1000
TimeoutOnWaitAction = 3000
ChopDelay = 1000
dragDelay = 600

weightLimit = Player.MaxWeight + 30
backpack = Player.Backpack.Serial
logBag = 0x40054709  # Serial of log bag in bank
bankX = 3697
bankY = 2513
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
tileinfo = List[Statics.TileInfo]
trees = []
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
def CheckInventory():
    global trees
    if Overweight(weightLimit):
        DepositInBank()
        trees = []
        ScanStatic()
        MoveToTree()


# ---------------------------------------------------------------------
def DepositInBank():
    Recall(bankRune)
    Bank(bankX, bankY)
    RestockAgent("lj")
    Misc.Pause(3000)
    RestockAgent("recall")
    Misc.Pause(3000)
    CutLogs()
    Misc.Pause(3000)
    MoveItemsByCount(bankDeposit, backpack, logBag)
    Misc.Pause(3000)


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
    Misc.SendMessage(">> total trees: %i" % (trees.Count), colors["notice"])


# ---------------------------------------------------------------------
def MoveToTree():
    global trees

    if not trees or trees.Count == 0:
        return

    Misc.SendMessage(
        ">> moving to tree: %i, %i" % (trees[0].x, trees[0].y), colors["notice"]
    )
    Misc.Resync()

    if Pathing(trees[0].x, trees[0].y, 0):
        Misc.SendMessage(
            ">> reached tree: %i, %i" % (trees[0].x, trees[0].y), colors["notice"]
        )
    else:
        Misc.SendMessage(
            ">> failed to reach tree: %i, %i" % (trees[0].x, trees[0].y),
            colors["error"],
        )
        trees = []
        ScanStatic()
        MoveToTree()


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
        Misc.SendMessage(">> detected block, canceling target!", colors["notice"])
        Target.Cancel()
        Misc.Pause(500)

    if Player.Weight >= weightLimit:
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
        or Timer.Check("chopTimer") == False
    ):
        Misc.Pause(100)

    if Journal.SearchByType("There's not enough wood here to harvest.", "System"):
        Misc.SendMessage(">> tree change", colors["notice"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search("That is too far away"):
        blockCount = blockCount + 1
        Journal.Clear()
        if blockCount > 1:
            blockCount = 0
            Misc.SendMessage(
                ">> possible block, detected tree change", colors["notice"]
            )
            Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
        else:
            CutTree()
    elif Journal.Search("Target cannot be seen"):
        MoveToTree()
    # elif Journal.Search("bloodwood"):
    #     Player.HeadMessage(1194, "BLOODWOOD!")
    #     Timer.Create("chopTimer", 10000)
    #     CutTree()
    # elif Journal.Search("heartwood"):
    #     Player.HeadMessage(1193, "HEARTWOOD!")
    #     Timer.Create("chopTimer", 10000)
    #     CutTree()
    # elif Journal.Search("frostwood"):
    #     Player.HeadMessage(1151, "FROSTWOOD!")
    #     Timer.Create("chopTimer", 10000)
    #     CutTree()
    elif Timer.Check("chopTimer") == False:
        Misc.SendMessage(">> tree change", colors["notice"])
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
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
def afkGump():
    if Gumps.HasGump(afkGumpID):
        return True


def afkSolveGump():
    return True


# ---------------------------------------------------------------------
def say(text):
    spk = SpeechSynthesizer()
    spk.Speak(text)


# ---------------------------------------------------------------------
def safteyNet():
    if afkGump():
        Misc.Beep()
        Misc.FocusUOWindow()
        say("Solve AFK Prompt")
    if alert:
        toon = Mobiles.ApplyFilter(toonFilter)
        invul = Mobiles.ApplyFilter(invulFilter)
        if toon:
            Misc.Beep()
            Misc.FocusUOWindow()
            say("Someone is here.")
            toonName = Mobiles.Select(toon, "Nearest")
            if toonName:
                Misc.SendMessage(">> toon near: " + toonName.Name, colors["alert"])
        elif invul:
            Misc.Beep()
            say("GM Activity.")
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
    ScanStatic()
    isScanned = True
    while trees.Count > 0:
        isScanned = False
        safteyNet()
        CheckInventory()
        MoveToTree()
        CutTree()
        trees.pop(0)
        trees = sorted(
            trees,
            key=lambda tree: sqrt(
                pow((tree.x - Player.Position.X), 2)
                + pow((tree.y - Player.Position.Y), 2)
            ),
        )
    trees = []
    if isScanned:
        DepositInBank()
    Misc.Pause(100)
