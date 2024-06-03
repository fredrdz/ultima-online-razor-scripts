import Items, Mobiles, PathFinding, Player, Misc, Statics, Target
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


def PathCount(x, y=0, z=0) -> int:
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


def PlayerDiagonalOffset(x=0, y=0):
    position_range = GetDiagonalCoordsOfPosition(x, y)

    for pos in position_range:
        if CheckTile(pos[0], pos[1]):
            return (pos[0], pos[1])

    return None


def GetDiagonalCoordsOfPosition(x=0, y=0):
    _out = []

    # calculate diagonal tuples of coordinates around position within 2 spaces
    for dx in [-2, -1, 1, 2]:
        for dy in [-2, -1, 1, 2]:
            if abs(dx) == abs(dy):  # ensure it's a diagonal
                _out.append((x + dx, y + dy))

    return _out


# ---------------------------------------------------------------------
def CheckTile(tile_x, tile_y, config=None):
    # Default config
    default_config = {
        "search_statics": True,  # look for blockable statics like trees, rocks (not blocked by sittable tree trunks) etc...
        "player_house_filter": True,  # avoid player houses - make this False if you need to use inside a large open player house room without walls
        "items_filter": {
            "Enabled": True,  # look for items which may block the tile, chests, tables (but is also stopped by objects like chairs and cups) etc...
        },
        "mobiles_filter": {
            "Enabled": True,  # look for MOBS which may block the tile (lambs, ancient dragons) etc...
        },
    }

    # Use default config if none or empty config is provided
    if not config:
        config = default_config
    else:
        # Merge provided config with default config
        config = {**default_config, **config}

    # Init
    flag_name = "Impassable"

    # Filter to get all items
    if config.get("items_filter", {}).get("Enabled"):
        items_filter = Items.Filter()
        items_filter.Enabled = True
        items = Items.ApplyFilter(items_filter)
        # Check if any items are on the tile
        for item in items:
            if (
                item.Position.X == tile_x
                and item.Position.Y == tile_y
                and item.OnGround
                and item.Visible
                and item.Name != "nodraw"
            ):
                return False  # Tile is blocked by an item

    # Filter to get all mobiles
    if config.get("mobiles_filter", {}).get("Enabled"):
        mobiles_filter = Mobiles.Filter()
        mobiles_filter.Enabled = True
        mobiles = Mobiles.ApplyFilter(mobiles_filter)
        # Check if any mobiles are on the tile
        for mobile in mobiles:
            if (
                mobile.Position.X == tile_x
                and mobile.Position.Y == tile_y
                and mobile.Visible
            ):
                return False  # Tile is blocked by a mobile

    # Check for statics and houses on the tile
    if config.get("search_statics", False):
        static_land = Statics.GetLandID(tile_x, tile_y, Player.Map)
        if Statics.GetLandFlag(static_land, flag_name):
            return False  # Tile is blocked by a static

        static_tile = Statics.GetStaticsTileInfo(tile_x, tile_y, Player.Map)
        if len(static_tile) > 0:
            for idx, static in enumerate(static_tile):
                if Statics.GetTileFlag(static.StaticID, flag_name):
                    return False  # Tile is blocked by a static

    if config.get("player_house_filter", False):
        is_blocked_by_house = Statics.CheckDeedHouse(tile_x, tile_y)
        if is_blocked_by_house:
            return False  # Tile is blocked by a house

    # Tile is passable because it's not blocked
    return True


# Usage
# is_passable = CheckTile(Player.Position.X + 1, Player.Position.Y)  # For one tile east
# Misc.SendMessage(f"is_passable = {is_passable}")  # Prints True if the tile is passable, False otherwise


# ---------------------------------------------------------------------
def RazorPathing(x, y):
    route = PathFinding.Route()
    route.X = x
    route.Y = y
    route.DebugMessage = False
    route.StopIfStuck = True
    route.MaxRetry = 0
    route.Timeout = 5

    Misc.SendMessage(">> razor pathing", colors["debug"])
    distance = PathCount(route.X, route.Y)
    message = ">> distance left: %i" % (distance)
    Misc.SendMessage(message, colors["info"])

    if PathFinding.Go(route):
        return True

    return False


def ClassicPathing(x, y):
    Player.PathFindTo(x, y, 1)
