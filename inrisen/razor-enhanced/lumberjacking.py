# SCRIPT: lumberjacking.py
# Author: Talik Starr
# IN:RISEN
# Skill: Lumberjacking

if Player.GetRealSkillValue("Lumberjacking") < 40:
    Misc.SendMessage("No skill, stopping", 33)
    Stop

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
# axeSerial = None
afkGumpID = 408109089
EquipAxeDelay = 1000
TimeoutOnWaitAction = 3000
ChopDelay = 1000
runeBank = 0x400BAAB7  # Rune for bank
recallPause = 3000
dragDelay = 600
logID = 0x1BDD
boardID = 0x1BD7
otherResourceID = [0x318F, 0x3199, 0x2F5F, 0x3190, 0x3191]
logBag = 0x40054709  # Serial of log bag in bank
otherResourceBag = 0x40137DD2  # Serial of other resource in bank
weightLimit = Player.MaxWeight
bankX = 3689
bankY = 2521
axeList = [0x0F49, 0x13FB, 0x0F47, 0x1443, 0x0F45, 0x0F4B, 0x0F43]
# rightHand = Player.CheckLayer('RightHand')
leftHand = Player.CheckLayer("LeftHand")
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
from System.Collections.Generic import List
from System import Byte
from math import sqrt
import clr

clr.AddReference("System.Speech")
from System.Speech.Synthesis import SpeechSynthesizer

tileinfo = List[Statics.TileInfo]
trees = []
blockCount = 0
onLoop = True


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


class Point3D:
    def __init__(self, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)


# ---------------------------------------------------------------------
def CheckInventory():
    global trees
    if Player.Weight >= weightLimit:
        DepositInBank()
        trees = []
        ScanStatic()
        MoveToTree()


# ---------------------------------------------------------------------
def RecallBack(rune):
    Spells.CastMagery("Recall")
    Target.WaitForTarget(3500, False)
    Target.TargetExecute(rune)
    Misc.Pause(recallPause)


# ---------------------------------------------------------------------
def DepositInBank():
    RecallBack(runeBank)
    Misc.Pause(recallPause)
    Player.ChatSay(77, "bank")
    Misc.Pause(300)

    Restock.ChangeList("lj")
    Restock.FStart()
    Misc.Pause(3000)
    Restock.ChangeList("recall")
    Restock.FStart()
    Misc.Pause(3000)

    CutLogs()
    for item in Player.Backpack.Contains:
        if item.ItemID == boardID:
            Misc.SendMessage(">> moving boards", 77)
            Items.Move(item, logBag, 0)
            Misc.Pause(dragDelay)
        else:
            for otherid in otherResourceID:
                if item.ItemID == otherid:
                    Misc.SendMessage(">> moving other", 77)
                    Items.Move(item, otherResourceBag, 0)
                    Misc.Pause(dragDelay)
                else:
                    Misc.NoOperation()


# ---------------------------------------------------------------------
def ScanStatic():
    global trees
    Misc.SendMessage(">> scan tile started...", 77)
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
                            # Misc.SendMessage( '>> tree X: %i - Y: %i - Z: %i' % ( minX, minY, tile.StaticZ ), 66 )
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
    Misc.SendMessage(">> total trees: %i" % (trees.Count), 77)


# ---------------------------------------------------------------------
def PathCount(x, y):
    playerX = Player.Position.X
    playerY = Player.Position.Y
    return Misc.Distance(playerX, playerY, x, y)


# ---------------------------------------------------------------------
def MoveToTree():
    global trees

    if not trees or trees.Count == 0:
        return

    Misc.SendMessage(">> moving to tree: %i, %i" % (trees[0].x, trees[0].y), 77)
    # Misc.Resync()

    if Pathing(trees[0].x, trees[0].y, 0):
        Misc.SendMessage(">> reached tree: %i, %i" % (trees[0].x, trees[0].y), 77)
    else:
        Misc.SendMessage(
            ">> failed to reach tree: %i, %i" % (trees[0].x, trees[0].y), 34
        )
        trees = []
        ScanStatic()
        MoveToTree()


# ---------------------------------------------------------------------
def Pathing(x, y, z):
    route = PathFinding.Route()
    destination = Point3D(x, y, z)
    playerPosition = Player.Position

    # determine direction offset
    if playerPosition.X > destination.x:
        destinationX = destination.x + 1
    elif playerPosition.X < destination.x:
        destinationX = destination.x - 1
    else:
        destinationX = destination.x

    ## TODO: issue here with Y axis; tends to be blocked which causes the uo client to freeze

    if playerPosition.Y > destination.y:
        destinationY = destination.y + 1
    elif playerPosition.Y < destination.y:
        destinationY = destination.y - 1
    else:
        destinationY = destination.y

    # check if destination is a valid land tile
    if Statics.GetLandID(destinationX, destinationY, 0) != None:
        destinationY = destination.y

    # razor pathing parameters
    route.X = destinationX
    route.Y = destinationY
    route.DebugMessage = False
    route.StopIfStuck = True
    route.MaxRetry = 0
    route.Timeout = 3

    # custom pathing parameters
    failCount = 0
    failTolerance = 3
    maxFails = 6
    minDistance = 30

    while not PathCount(route.X, route.Y) == 0:
        Misc.Pause(100)
        distance = PathCount(route.X, route.Y)
        message = ">> distance left: %i" % (distance)
        Misc.SendMessage(message, 50)

        if distance < minDistance:
            Misc.SendMessage(">> classicUO pathing", 50)
            Player.PathFindTo(route.X, route.Y, z)
            Timer.Create("classicPathingTimeout", 10000)
            while not PathCount(route.X, route.Y) == 0:
                Misc.Pause(100)
                if not Timer.Check("classicPathingTimeout"):
                    Misc.SendMessage(">> classicUO pathing failed", 34)
                    break
        elif failCount <= failTolerance:
            Misc.SendMessage(">> razor pathing", 50)
            if not PathFinding.Go(route):
                traveled = distance - PathCount(route.X, route.Y)
                if traveled == 0:
                    Misc.SendMessage(">> razor pathing failed", 34)
                    failCount = failCount + 1
                else:
                    failCount = 0
        elif failCount > maxFails:
            Misc.SendMessage(">> all pathing attempts failed", 34)
            return False
        elif Player.Position.Z != 0 or failCount > failTolerance:
            Misc.SendMessage(">> pathing issues detected", 34)
            Misc.SendMessage(">> trying directional movement", 50)
            directionalMove(route.X, route.Y)
            traveled = distance - PathCount(route.X, route.Y)
            if traveled < 4:
                Misc.SendMessage(">> directional pathing failed", 34)
                failCount = failCount + 1
            else:
                failCount = 0

    return True


# ---------------------------------------------------------------------
def directionalMove(x, y):
    playerPos = Player.Position

    for _ in range(2):
        if playerPos.X > x:
            Player.Run("Left")
            Misc.Pause(150)
        elif playerPos.X < x:
            Player.Run("Right")
            Misc.Pause(150)
        elif playerPos.Y > y:
            Player.Run("Down")
            Misc.Pause(150)
        elif playerPos.Y < y:
            Player.Run("Up")
            Misc.Pause(150)


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
        Misc.SendMessage(">> detected block, canceling target!", 77)
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
        Misc.SendMessage(">> tree change", 77)
        Timer.Create("%i,%i" % (trees[0].x, trees[0].y), treeCooldown)
    elif Journal.Search("That is too far away"):
        blockCount = blockCount + 1
        Journal.Clear()
        if blockCount > 1:
            blockCount = 0
            Misc.SendMessage(">> possible block, detected tree change", 77)
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
        Misc.SendMessage(">> tree change", 77)
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
                Misc.SendMessage(">> toon near: " + toonName.Name, 30)
        elif invul:
            Misc.Beep()
            say("GM Activity.")
            invulName = Mobiles.Select(invul, "Nearest")
            if invulName:
                Misc.SendMessage(">> invul near:" + invul.Name, 30)
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
Misc.SendMessage(">> lumberjack starting up...", 77)
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
