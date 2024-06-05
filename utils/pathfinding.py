"""
SCRIPT: pathfinding.py
Author: Talik Starr
IN:RISEN

Description: custom pathfinding which takes into account statics, player houses, items, and mobiles
"""

import random
from heapq import heappush, heappop
import Items, Player, Misc, Mobiles, Statics, Target
from glossary.colors import colors

# *********************************************************************
# Edit the following variables to suit your needs

# script flags
config = {
    "search_statics": True,
    "player_house_filter": True,
    "items_filter": {"Enabled": True},
    "mobiles_filter": {"Enabled": True},
}

# script parameters
max_iterations = 10000
max_distance = 1000
debug = 1
maxRetryIterations = 1
retryIteration = 0
shortPause = random.randint(50, 150)


# ---------------------------------------------------------------------
# do not edit below this line


# pathfinding classes
class Position:
    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.X == other.X
            and self.Y == other.Y
        )


class Node:
    def __init__(self, x, y, cost=0, heur=0, prev=None):
        self.x = x
        self.y = y
        self.cost = cost
        self.heur = heur
        self.prev = prev

    def __lt__(self, other):
        return self.cost + self.heur < other.cost + other.heur


# ---------------------------------------------------------------------
# start of pathfinding logic
# inits variables

playerStartPosition = Player.Position
goalPosition = Position(0, 0)
overrideAsPosition = Position(0, 0)

if Misc.CheckSharedValue("pathFindingOverride"):
    override = Misc.ReadSharedValue("pathFindingOverride")
    overrideAsPosition = Position(override[0], override[1])

    if goalPosition != overrideAsPosition:
        goalPosition = overrideAsPosition
        if debug > 0:
            Misc.SendMessage(">> remote pathfinding request detected", colors["debug"])
            Misc.SendMessage(
                f">> remote pathfinding request to {override[0],override[1]}",
                colors["debug"],
            )

items_filter = Items.Filter()
items_filter.Enabled = config["items_filter"]["Enabled"]
mobiles_filter = Mobiles.Filter()
mobiles_filter.Enabled = config["mobiles_filter"]["Enabled"]
items = Items.ApplyFilter(items_filter)
mobiles = Mobiles.ApplyFilter(mobiles_filter)


# ---------------------------------------------------------------------
# pathfinding functions


def check_tile(tile_x, tile_y, items, mobiles):
    flag_name = "Impassable"
    for item in items:
        if (
            item.Position.X == tile_x
            and item.Position.Y == tile_y
            and item.OnGround
            and item.Visible
            and item.Name != "nodraw"
        ):
            return False

    for mobile in mobiles:
        if (
            mobile.Position.X == tile_x
            and mobile.Position.Y == tile_y
            and mobile.Visible
        ):
            return False

    if config["search_statics"]:
        static_land = Statics.GetLandID(tile_x, tile_y, Player.Map)
        if Statics.GetLandFlag(static_land, flag_name):
            return False

        static_tile = Statics.GetStaticsTileInfo(tile_x, tile_y, Player.Map)
        for static in static_tile:
            if Statics.GetTileFlag(static.StaticID, flag_name):
                return False

    if config["player_house_filter"]:
        if Statics.CheckDeedHouse(tile_x, tile_y):
            return False

    return True


def heuristic(a, b):
    return abs(b.x - a.x) + abs(b.y - a.y)


def a_star_pathfinding(
    playerStartPosition,
    goalPosition,
    check_tile,
    max_iterations=10000,
    max_distance=None,
):
    items = Items.ApplyFilter(items_filter)
    mobiles = Mobiles.ApplyFilter(mobiles_filter)
    open_nodes = []
    closed_nodes = set()
    path = None

    start_node = Node(playerStartPosition.X, playerStartPosition.Y)
    goal_node = Node(goalPosition.X, goalPosition.Y)

    heappush(open_nodes, start_node)
    if debug > 0:
        Misc.SendMessage(">> pathfinding started...", colors["debug"])

    for i in range(max_iterations):
        if debug > 1:
            Misc.SendMessage(f">> current iteration: {i}", colors["debug"])

        if not open_nodes:
            Misc.SendMessage(
                ">> pathfinding failed: no valid path found", colors["debug"]
            )
            return None

        current_node = heappop(open_nodes)
        closed_nodes.add((current_node.x, current_node.y))

        if (
            max_distance is not None
            and heuristic(start_node, current_node) > max_distance
        ):
            continue

        if current_node.x == goal_node.x and current_node.y == goal_node.y:
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.prev
            if debug > 0:
                Misc.SendMessage(">> pathfinding completed", colors["debug"])
            return path[::-1]

        for dx, dy in [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1),
        ]:
            next_x, next_y = current_node.x + dx, current_node.y + dy
            if (
                dx != 0
                and dy != 0
                and (
                    not check_tile(current_node.x, current_node.y + dy, items, mobiles)
                    or not check_tile(
                        current_node.x + dx, current_node.y, items, mobiles
                    )
                )
            ):
                continue
            if (
                check_tile(next_x, next_y, items, mobiles)
                and (next_x, next_y) not in closed_nodes
            ):
                cost = (
                    current_node.cost + 1.4
                    if dx != 0 and dy != 0
                    else current_node.cost + 1
                )
                next_node = Node(
                    next_x,
                    next_y,
                    cost,
                    heuristic(goal_node, Node(next_x, next_y)),
                    current_node,
                )
                heappush(open_nodes, next_node)

    Misc.SendMessage(">> pathfinding failed", colors["debug"])
    return path


def move_player_along_path(path):
    direction_map = {
        (0, 1): "South",
        (0, -1): "North",
        (1, 0): "East",
        (-1, 0): "West",
        (-1, -1): "Up",
        (1, 1): "Down",
        (1, -1): "Right",
        (-1, 1): "Left",
    }
    stuckCount = 0
    stop_moving = False

    for i in range(len(path) - 1):
        if stop_moving:
            break

        current_node, next_node = path[i], path[i + 1]
        dx = next_node[0] - current_node[0]
        dy = next_node[1] - current_node[1]
        direction = direction_map.get((dx, dy))

        if direction and Player.Direction != direction:
            Player.Run(direction)
            Misc.Pause(shortPause)

        Player.Run(direction)
        Misc.Pause(shortPause)

        if debug > 1:
            Misc.SendMessage(
                f">> moving from {current_node} to {next_node} ({i} of {len(path)})",
                colors["debug"],
            )

        while (Player.Position.X, Player.Position.Y) != next_node:
            Misc.Pause(shortPause)
            if (Player.Position.X, Player.Position.Y) == current_node:
                if debug > 1:
                    Misc.SendMessage(
                        f">> player stuck at {current_node}, trying to move again",
                        colors["debug"],
                    )
                Player.Run(direction)
                Misc.Pause(shortPause)
                stuckCount += 1
                Player.HeadMessage(42, "oops...thinking..!")
                if stuckCount > 5:
                    Player.HeadMessage(42, "I give up!")
                    stop_moving = True
                    break
            elif (
                abs(Player.Position.X - next_node[0]) <= 1
                and abs(Player.Position.Y - next_node[1]) <= 1
            ):
                break


# ---------------------------------------------------------------------
# main process

if goalPosition == Position(0, 0):
    goalPosition = Target.PromptGroundTarget("Where do you wish to pathfind?")

if check_tile(goalPosition.X, goalPosition.Y, items, mobiles):
    if debug > 0:
        Misc.SendMessage(f">> pathfinding to: {goalPosition}", colors["debug"])
    else:
        Player.HeadMessage(42, "Thinking...")
    path = a_star_pathfinding(Player.Position, goalPosition, check_tile)
else:
    path = 0

if path == 0:
    if debug > 0:
        Misc.SendMessage(">> invalid Area", colors["debug"])
    else:
        Player.HeadMessage(42, "That's inaccessible!")
elif not path:
    if debug > 0:
        Misc.SendMessage(">> no valid path found", colors["debug"])
        Misc.SendMessage(f">> failed after {max_iterations} attempts", colors["debug"])
    else:
        Player.HeadMessage(42, "I can't figure out how to get there!")
else:
    if debug == 0:
        Player.HeadMessage(42, "Here we go!")
    for node in path:
        if debug > 1:
            Misc.SendMessage(f">> node in path: {node}", colors["debug"])
    move_player_along_path(path)

if Player.Position == goalPosition:
    if debug == 0:
        Player.HeadMessage(42, "I have arrived!")
    Misc.SendMessage(">> movement complete", colors["debug"])

if Misc.CheckSharedValue("pathFindingOverride"):
    Misc.SetSharedValue(
        "pathFindingOverride", (0, 0)
    )  # resets shared value to allow for normal targeting prompt
