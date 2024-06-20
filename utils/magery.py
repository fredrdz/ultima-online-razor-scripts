# Description: Magery related functions

# System packages
from System.Collections.Generic import List
from System import Byte

# Custom RE packages
import config
import Journal, Misc, Mobiles, Player, Spells, Target, Timer
from glossary.colors import colors
from glossary.spells import reagents, spells
from utils.items import FindNumberOfItems


def RecallRune(rune):
    Spells.CastMagery("Recall")
    Target.WaitForTarget(2000, False)
    Target.TargetExecute(rune)


def Teleport():
    Spells.CastMagery("Teleport")
    Target.WaitForTarget(2000, False)
    Target.TargetExecuteRelative(Player.Serial, 10)


def Meditation():
    Journal.Clear()

    Player.HeadMessage(colors["status"], "[meditate]")
    Player.UseSkill("Meditation")

    while Player.Mana < Player.ManaMax:
        Misc.Pause(100)

        if Player.WarMode or Player.Hits < Player.HitsMax:
            Player.HeadMessage(colors["fail"], "[meditated]")
            break

        if Journal.SearchByType("You cannot focus your concentration.", "System"):
            Player.HeadMessage(colors["fail"], "[meditated]")
            break

        if Journal.SearchByType(
            "You are preoccupied with thoughts of battle.", "System"
        ):
            Player.SetWarMode(True)
            Player.HeadMessage(colors["fail"], "[meditated]")
            break


def FindReagents():
    """
    Uses FindNumberOfItems to find an the reagents in the player's backpack
    Returns a dictionary of the reagents found
    """
    reagentItemIDs = []

    for reagent in reagents:
        reagentItemIDs.append(reagents[reagent].itemID)

    return FindNumberOfItems(reagentItemIDs, Player.Backpack)


def CheckReagents(spellName, numberOfCasts=1):
    """
    Checks if the necessary reagents are available in the player's backpack to use a spell
    """
    reagentsInBackpack = FindReagents()
    reagentsNeeded = spells[spellName].reagents

    for reagent in reagentsNeeded:
        if reagentsInBackpack[reagent.itemID] < numberOfCasts:
            return False

    return True


# ---------------------------------------------------------------------
def CastSpellOnSelf(spellName, delay=None):
    """
    Casts a spell self (on the player)
    """
    spell = spells[spellName]

    Spells.CastMagery(spell.name)
    Target.WaitForTarget(2000, False)
    Target.Self()

    if delay is None or not isinstance(delay, int):
        # Use default delay if delay is None or not an int
        delay = spell.delayInMs + config.shardLatency

    Misc.Pause(delay)


# Example usage
# CastSpellOnSelf("Greater Heal")  # Uses default delay
# CastSpellOnSelf("Greater Heal", 1500)  # Uses specified delay of 1500 ms
# CastSpellOnSelf("Greater Heal", "fast")  # Uses default delay due to invalid type


def CastSpellOnTarget(target, spellName, delay=None):
    """
    Casts a spell on the target
    """
    spell = spells[spellName]

    Spells.CastMagery(spell.name)
    Target.WaitForTarget(2000, False)
    Target.TargetExecute(target)

    if delay is None or not isinstance(delay, int):
        # Use default delay if delay is None or not an int
        delay = spell.delayInMs + config.shardLatency

    Misc.Pause(delay)


def CastSpellRepeatably(spellName, target=None):
    """
    Casts a spell on the target multiple times
    """
    # init
    Journal.Clear()
    enemy = None
    enemies = []
    Timer.Create("cast_cd", 1)

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

    # check if target is provided
    if target is None:
        # get enemies
        enemies = Mobiles.ApplyFilter(enemyFilter)
        # check if enemies found and select one
        if len(enemies) > 0:
            # exception: we name our friendly followers "bob"
            # dont select bob
            for e in enemies:
                if e.Name != "bob":
                    # select nearest enemy
                    enemy = e

    if enemy:
        # stop defense script while attacking
        if Misc.ScriptStatus("_defense.py"):
            Misc.ScriptStop("_defense.py")
        # start attacking
        Player.HeadMessage(colors["success"], f"[targeting {enemy.Name}]")
        Mobiles.Message(
            enemy,
            colors["warning"],
            ">> enemy",
        )
        while Player.Mana > spells[spellName].manaCost:
            Misc.Pause(100)
            # check player status and defend if necessary
            hp_diff = Player.HitsMax - Player.Hits
            if 0 < hp_diff > 40 or Player.Poisoned:
                Player.HeadMessage(colors["notice"], "[defending]")
                if not Misc.ScriptStatus("_defense.py"):
                    Misc.ScriptRun("_defense.py")
                # stop attacking; exit script
                return
            # enemy and spell checks
            if not enemy:
                Player.HeadMessage(colors["status"], "[enemy gone]")
                break
            elif enemy.IsGhost or enemy.Deleted:
                Player.HeadMessage(colors["status"], "[enemy gone]")
                break
            elif Player.InRangeMobile(enemy, 14) is False:
                Player.HeadMessage(colors["fail"], "[enemy los]")
                break
            elif CheckReagents(spellName) is False:
                Player.HeadMessage(colors["fail"], "[no reagents]")
                break
            elif Timer.Check("cast_cd") is True:
                continue
            # exception checks
            if spellName == "Poison":
                if enemy.Poisoned:
                    Player.HeadMessage(colors["success"], "[enemy poisoned]")
                    break
                elif Journal.Search("The poison seems to have no effect."):
                    Player.HeadMessage(colors["notice"], "[enemy immune]")
                    break
            # actual spell cast
            Target.ClearLastandQueue()
            CastSpellOnTarget(enemy, spellName, 0)
            Timer.Create("cast_cd", spells[spellName].delayInMs + config.shardLatency)
            # exception checks
            if spellName == "Curse":
                break
    else:
        Player.HeadMessage(colors["status"], "[no target]")

    # resume defense script
    if not Misc.ScriptStatus("_defense.py"):
        Misc.ScriptRun("_defense.py")


# ---------------------------------------------------------------------
def StopAllCastsExcept(castScript):
    """
    Stops all spell casting scripts
    """
    scripts = [
        "cast_Curse.py",
        "cast_Poison.py",
        "cast_Lightning.py",
        "cast_Harm.py",
        "cast_MagicArrow.py",
        "cast_Fireball.py",
        "cast_Explosion.py",
        "cast_EnergyBolt.py",
    ]

    for script in scripts:
        if Misc.ScriptStatus(script) and script != castScript:
            Misc.ScriptStop(script)
        Misc.Pause(50)
