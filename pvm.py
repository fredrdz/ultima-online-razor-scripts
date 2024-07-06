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
if not Misc.ScriptStatus("_defense.py"):
    Misc.ScriptRun("_defense.py")

while not Player.IsGhost:
    Misc.Pause(100)

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

    # check if we can summon a daemon
    follower_diff = Player.FollowersMax - Player.Followers
    if 0 < follower_diff >= 2 and Player.Mana >= 50:
        Spells.CastMagery("Summon Daemon")
        Timer.Create("cast_cd", spells["Summon Daemon"].delayInMs + config.shardLatency)
        Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))

    # get enemies
    enemies = Mobiles.ApplyFilter(pvmFilter)
    # heal if needed and then filter out enemies named "bob"
    for i in range(len(enemies) - 1, -1, -1):
        if enemies[i].Name == "bob":
            if enemies[i].Hits < enemies[i].HitsMax:
                if (
                    Timer.Check("bandage_cd") is False
                    and Player.InRangeMobile(enemies[i], 2) is True
                ):
                    bandages = FindBandage(Player.Backpack)
                    if bandages:
                        if Target.HasTarget():
                            Target.Cancel()
                        Items.UseItem(bandages)
                        Target.WaitForTarget(1000, False)
                        Target.TargetExecute(enemies[i])
                        Timer.Create("bandage_cd", 2300 + config.shardLatency)
            del enemies[i]
    # check if enemies found and select one
    if len(enemies) > 0:
        for e in enemies:
            # exception: we name our friendly followers "bob"
            # if our daemon summon, rename, set to guard, and go to next target
            if e.MobileID == daemon and e.Name != "bob":
                Misc.PetRename(e, "bob")
                Player.ChatSay(colors["debug"], "All Guard Me")
                continue
            # overwrites enemy mob target via script shared value if one is set
            shared_target = Misc.ReadSharedValue("kill_target")
            if shared_target > 0:
                enemy = Mobiles.FindBySerial(shared_target)
                if enemy:
                    break
            # select nearest enemy if shared target not found
            enemy = Mobiles.Select(enemies, "Nearest")

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
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(enemy)
        Timer.Create("kill_cd", 4000)

    # if no enemy found, clear target
    enemy = None
