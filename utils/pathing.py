import PathFinding, Player, Misc, Target
from glossary.colors import colors


class Point3D:
    def __init__(self, x, y, z):
        self.X = int(x)
        self.Y = int(y)
        self.Z = int(z)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.X == other.X and self.Y == other.Y and self.Z == other.Z
        else:
            return False


class Position:
    def __init__(self, x, y):
        self.X = int(x)
        self.Y = int(y)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.X == other.X and self.Y == other.Y
        else:
            return False


# ---------------------------------------------------------------------


def IsPosition(x=0, y=0):
    return Player.Position.X == x and Player.Position.Y == y


def Wait_on_position(pos=None):
    if not pos:
        pos = Get_position()

    Misc.SendMessage(">> waiting until location reached...", colors["status"])
    while not IsPosition(pos.X, pos.Y):
        Misc.Pause(100)


def Get_position(sys_msg=None):
    if sys_msg:
        Misc.SendMessage(">> %s" % sys_msg, colors["notice"])

    position = Target.PromptGroundTarget(">> set coordinates:", colors["notice"])
    Misc.SendMessage(
        ">> coordinates set: %i, %i" % (position.X, position.Y), colors["info"]
    )
    return position


def PathCount(x, y=0, z=0):
    player_position = Player.Position
    pX = player_position.X
    pY = player_position.Y

    if isinstance(x, Point3D):
        target_position = x
    elif isinstance(x, Position):
        target_position = Point3D(x.X, x.Y, z)
    else:
        target_position = Point3D(int(x), int(y), int(z))

    tX = target_position.X
    tY = target_position.Y

    return Misc.Distance(pX, pY, tX, tY)


def PlayerDirectionOffset(x, y):
    player_position = Player.Position
    pX = player_position.X
    pY = player_position.Y

    if pX > x:
        tX = x + 1
    elif pX < x:
        tX = x - 1
    else:
        tX = x

    if pY > y:
        tY = y + 1
    elif pY < y:
        tY = y - 1
    else:
        tY = y

    return tX, tY


# ---------------------------------------------------------------------
def RazorPathing(x, y):
    route = PathFinding.Route()
    route.X = x
    route.Y = y
    route.DebugMessage = False
    route.StopIfStuck = True
    route.MaxRetry = 0
    route.Timeout = 3

    Misc.SendMessage(">> razor pathing", colors["debug"])
    distance = PathCount(route.X, route.Y)
    message = ">> distance left: %i" % (distance)
    Misc.SendMessage(message, colors["info"])

    if PathFinding.Go(route):
        return True

    return False
