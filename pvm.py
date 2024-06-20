# System packages
from System.Collections.Generic import List
from System import Byte

# Custom RE packages
import config
import Items, Journal, Misc, Mobiles, Player, Spells, Target, Timer
from glossary.colors import colors
from glossary.spells import spells

# init
enemy = None
enemies = []
daemon = 0x0009
Timer.Create("cast_cd", 1)
Timer.Create("kill_cd", 1)

# filter for enemies
enemyFilter = Mobiles.Filter()
enemyFilter.Enabled = True
enemyFilter.RangeMin = -1
enemyFilter.RangeMax = -1
enemyFilter.CheckLineOfSight = True
enemyFilter.Poisoned = -1
enemyFilter.IsHuman = -1
enemyFilter.IsGhost = False
enemyFilter.Warmode = -1
enemyFilter.Friend = False
enemyFilter.Paralized = -1
enemyFilter.Notorieties = List[Byte](bytes([4, 5, 6]))

# check if _defense.py is running
if not Misc.ScriptStatus("_defense.py"):
    Misc.ScriptRun("_defense.py")

while not Player.IsGhost:
    Misc.Pause(100)

    # check if our daemons are attacking friendlies
    if Journal.Search("*You see bob attacking you!*"):
        Journal.Clear()
        Player.ChatSay(colors["chat"], "All Stop")
        Player.ChatSay(colors["chat"], "All Guard Me")
        Misc.Pause(2000)
    elif Journal.Search("*You see bob attacking bob!*"):
        Journal.Clear()
        Player.ChatSay(colors["chat"], "All Stop")
        Player.ChatSay(colors["chat"], "All Guard Me")
        Misc.Pause(2000)

    # check if we can summon a daemon
    follower_diff = Player.FollowersMax - Player.Followers
    if 0 < follower_diff >= 2 and Player.Mana >= 40:
        Spells.CastMagery("Summon Daemon")
        Misc.Pause(spells["Summon Daemon"].delayInMs + config.shardLatency)

    # get enemies
    enemies = Mobiles.ApplyFilter(enemyFilter)

    # check if enemies found and select one
    if len(enemies) > 0:
        for e in enemies:
            # exception: we name our friendly followers "bob"
            # if our daemon summon, rename, set to guard, and go to next target
            if e.MobileID == daemon and e.Name != "bob":
                Misc.PetRename(e, "bob")
                Player.ChatSay(colors["chat"], "All Guard Me")
            elif e.Name != "bob":
                # select nearest enemy
                enemy = e
    else:
        enemy = None

    # if enemy is found, select and kill
    if enemy and Timer.Check("kill_cd") is False:
        Mobiles.Message(
            enemy,
            colors["warning"],
            ">> enemy",
        )
        Player.ChatSay(colors["chat"], "All Kill")
        Target.WaitForTarget(2000, False)
        Target.TargetExecute(enemy)
        Timer.Create("kill_cd", 5000)
