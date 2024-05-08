from glossary.colors import colors


class Point3D:
    def __init__(self, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)


# ---------------------------------------------------------------------
def PathCount(x, y):
    playerX = Player.Position.X
    playerY = Player.Position.Y
    return Misc.Distance(playerX, playerY, x, y)


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

    if playerPosition.Y > destination.y:
        destinationY = destination.y + 1
    elif playerPosition.Y < destination.y:
        destinationY = destination.y - 1
    else:
        destinationY = destination.y

    # razor pathing parameters
    route.X = destinationX
    route.Y = destinationY
    route.DebugMessage = False
    route.StopIfStuck = True
    route.MaxRetry = 0
    route.Timeout = 2

    # custom pathing parameters
    failCount = 0
    failTolerance = 2
    maxFails = 6
    minDistance = 30

    if not PathFinding.Go(route):
        route.Y = route.Y - 2

    Timer.Create("pathingTimeout", 300000)
    while not PathCount(route.X, route.Y) == 0:
        Misc.Pause(100)
        distance = PathCount(route.X, route.Y)
        message = ">> distance left: %i" % (distance)
        Misc.SendMessage(message, colors["debug"])

        if not Timer.Check("pathingTimeout"):
            Misc.SendMessage(">> pathlocked, resetting", colors["fatal"])
            return False

        if distance < minDistance:
            Misc.SendMessage(">> classicUO pathing", colors["debug"])
            Player.PathFindTo(route.X, route.Y, z)
            Timer.Create("classicPathingTimeout", 10000)
            while not PathCount(route.X, route.Y) == 0:
                Misc.Pause(100)
                if not Timer.Check("classicPathingTimeout"):
                    Misc.SendMessage(">> classicUO pathing failed", colors["error"])
                    break
        elif failCount <= failTolerance:
            Misc.SendMessage(">> razor pathing", colors["debug"])
            if not PathFinding.Go(route):
                traveled = distance - PathCount(route.X, route.Y)
                if traveled == 0:
                    Misc.SendMessage(">> razor pathing failed", colors["error"])
                    failCount = failCount + 1
                else:
                    failCount = 0
        elif failCount > maxFails:
            Misc.SendMessage(">> all pathing attempts failed", colors["error"])
            return False
        elif Player.Position.Z != 0 or failCount > failTolerance:
            Misc.SendMessage(">> pathing issues detected", colors["error"])
            Misc.SendMessage(">> trying directional movement", colors["debug"])
            directionalMove(route.X, route.Y)
            traveled = distance - PathCount(route.X, route.Y)
            if traveled < 4:
                Misc.SendMessage(">> directional pathing failed", colors["error"])
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
