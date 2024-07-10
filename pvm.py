# System packages
from System.Collections.Generic import List
from System import Byte

# Custom RE packages
import config
import Items, Journal, Misc, Mobiles, Player, Spells, Target, Timer
from glossary.colors import colors
from glossary.spells import spells
from glossary.items.healing import FindBandage

# init
Journal.Clear()
enemy = None
enemies = []
daemon = 0x0009

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
if Misc.ScriptStatus("_defense.py") is False:
    Misc.ScriptRun("_defense.py")

while not Player.IsGhost:
    Misc.Pause(100)

    # toggle war mode off if trying to do something peaceful
    if Journal.SearchByType("You are preoccupied with thoughts of a battle.", "System"):
        Player.SetWarMode(True)
        Player.SetWarMode(False)

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

    # check follower count
    follower_diff = Player.FollowersMax - Player.Followers

    # check if we can summon a daemon
    if 0 < follower_diff >= 2 and Player.Mana >= 50:
        # stop casting script if running to avoid fizzles
        if Misc.ScriptStatus("_cast.py") is True:
            Misc.ScriptStop("_cast.py")
            Misc.SetSharedValue("spell", "")
            # read global cast cd timer
            if Misc.ReadSharedValue("cast_cd") > 0:
                current = Misc.ReadSharedValue("cast_cd")
                Timer.Create("cast_cd", current)
            # wait out timer
            remaining = Timer.Remaining("cast_cd")
            Misc.Pause(remaining)
        Spells.CastMagery("Summon Daemon")
        Timer.Create("cast_cd", spells["Summon Daemon"].delayInMs + config.shardLatency)
        current = Timer.Remaining("cast_cd")
        Misc.SetSharedValue("cast_cd", current)

    # get enemies
    enemies = Mobiles.ApplyFilter(pvmFilter)

    # check enemies
    for i in range(len(enemies) - 1, -1, -1):
        e = enemies[i]
        if e.Name == "bob":
            del enemies[i]
            # if enemies[i].Hits < enemies[i].HitsMax:
            #     if (
            #         Timer.Check("bandage_cd") is False
            #         and Player.InRangeMobile(enemies[i], 2) is True
            #     ):
            #         bandages = FindBandage(Player.Backpack)
            #         if bandages:
            #             if Target.HasTarget():
            #                 Target.Cancel()
            #             Items.UseItem(bandages)
            #             Target.WaitForTarget(200, False)
            #             Target.TargetExecute(enemies[i])
            #             Timer.Create("bandage_cd", 2350 + config.shardLatency)
        elif e.MobileID == daemon and e.Name != "bob":
            # if our daemon, rename, set to guard
            Misc.PetRename(e, "bob")
            Player.ChatSay(colors["debug"], "All Guard Me")

    # select nearest enemy
    enemy = Mobiles.Select(enemies, "Nearest")

    # overwrite with shared target if found
    shared_target = Misc.ReadSharedValue("kill_target")
    if shared_target > 0:
        found = Mobiles.FindBySerial(shared_target)
        if found:
            enemy = found

    # if enemy is found, select and kill
    if enemy and Timer.Check("kill_cd") is False:
        Mobiles.Message(
            enemy,
            colors["alert"],
            ">> follower target <<",
        )
        if Target.HasTarget():
            Target.Cancel()
        Player.ChatSay(colors["debug"], "All Kill")
        Target.WaitForTarget(200, False)
        Target.TargetExecute(enemy)
        Timer.Create("kill_cd", 5000)

    # if no enemy found, clear target
    enemy = None
