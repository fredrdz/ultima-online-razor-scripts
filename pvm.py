# System packages
from System.Collections.Generic import List
from System import Byte

# Custom RE packages
import config
import Items, Journal, Misc, Mobiles, Player, Spells, Target, Timer
from glossary.colors import colors
from glossary.spells import spells

# init
Journal.Clear()
enemy = None
enemies = []
daemon = 0x0009
Timer.Create("cast_cd", 1)
Timer.Create("kill_cd", 1)

# filter for enemies
pvmFilter = Mobiles.Filter()
pvmFilter.Enabled = True
pvmFilter.RangeMin = 1
pvmFilter.RangeMax = 10
pvmFilter.CheckLineOfSight = True
pvmFilter.Poisoned = -1
pvmFilter.IsHuman = -1
pvmFilter.IsGhost = False
pvmFilter.Warmode = -1
pvmFilter.Friend = False
pvmFilter.Paralized = -1
pvmFilter.Notorieties = List[Byte](bytes([4, 5, 6]))

# check if _defense.py is running
if not Misc.ScriptStatus("_defense.py"):
    Misc.ScriptRun("_defense.py")

while not Player.IsGhost:
    Misc.Pause(100)

    # check if our daemons are attacking friendlies
    if Journal.Search("*You see bob attacking you!*"):
        Journal.Clear()
        Player.ChatSay(colors["debug"], "All Stop")
        Player.ChatSay(colors["debug"], "All Guard Me")
        Misc.Pause(2000)
    elif Journal.Search("*You see bob attacking bob!*"):
        Journal.Clear()
        Player.ChatSay(colors["debug"], "All Stop")
        Player.ChatSay(colors["debug"], "All Guard Me")
        Misc.Pause(2000)
    elif Timer.Check("cast_cd") is True:
        Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
        continue

    # check if we can summon a daemon
    follower_diff = Player.FollowersMax - Player.Followers
    if 0 < follower_diff >= 2 and Player.Mana >= 50:
        Spells.CastMagery("Summon Daemon")
        Timer.Create("cast_cd", spells["Summon Daemon"].delayInMs + config.shardLatency)
        Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))

    # get enemies
    enemies = Mobiles.ApplyFilter(pvmFilter)
    # filter out enemies named "bob"
    for i in range(len(enemies) - 1, -1, -1):
        if enemies[i].Name == "bob":
            del enemies[i]
    # check if enemies found and select one
    if len(enemies) > 0:
        for e in enemies:
            # exception: we name our friendly followers "bob"
            # if our daemon summon, rename, set to guard, and go to next target
            if e.MobileID == daemon and e.Name != "bob":
                Misc.PetRename(e, "bob")
                Player.ChatSay(colors["debug"], "All Guard Me")
            else:
                # select nearest enemy
                enemy = Mobiles.Select(enemies, "Nearest")

    # if enemy is found, select and kill
    if enemy and Timer.Check("kill_cd") is False:
        Mobiles.Message(
            enemy,
            colors["warning"],
            ">> enemy",
        )
        Target.ClearLastandQueue()
        Player.ChatSay(colors["debug"], "All Kill")
        Target.WaitForTarget(2000, False)
        Target.TargetExecute(enemy)
        Timer.Create("kill_cd", 4000)

    enemy = None
