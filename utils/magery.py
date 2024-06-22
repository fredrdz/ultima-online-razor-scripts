# Description: Magery related functions

# System packages
from System import Byte
from System import Int32
from System.Collections.Generic import List

# Custom RE packages
import config
import Journal, Misc, Mobiles, Player, Spells, Sound, Target, Timer
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
    # init
    Journal.Clear()
    Sound.Log(False)
    sounds = List[Int32]([249])  # meditation sound
    # use skill
    Player.UseSkill("Meditation")
    # skill checks
    if Journal.SearchByType("You are preoccupied with thoughts of battle.", "System"):
        Player.HeadMessage(colors["fail"], "[battle]")
        return
    elif Journal.WaitJournal("You begin meditating...", 5000):
        if Journal.WaitJournal("You enter a meditative trance.", 5000):
            Player.HeadMessage(colors["success"], "[meditating]")
            while Player.Mana < Player.ManaMax:
                Misc.Pause(100)
                if Player.WarMode or Player.Hits < Player.HitsMax:
                    Player.HeadMessage(colors["fail"], "[combat]")
                    break
                elif Journal.SearchByType(
                    "You cannot focus your concentration.", "System"
                ):
                    Player.HeadMessage(colors["fail"], "[concentration]")
                    break
                elif Journal.SearchByType(
                    "You are preoccupied with thoughts of battle.", "System"
                ):
                    Player.HeadMessage(colors["fail"], "[battle]")
                    break
                elif Sound.WaitForSound(sounds, 1000) is False:
                    break
    # success check
    if Player.Mana == Player.ManaMax:
        Player.HeadMessage(colors["success"], "[full mp]")


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
    if Misc.ReadSharedValue("cast_cd") > 0:
        Timer.Create("cast_cd", Misc.ReadSharedValue("cast_cd"))

    # filter for enemies
    enemyFilter = Mobiles.Filter()
    enemyFilter.Enabled = True
    enemyFilter.RangeMin = 1
    enemyFilter.RangeMax = 10
    enemyFilter.CheckLineOfSight = True
    enemyFilter.Poisoned = -1
    enemyFilter.IsHuman = -1
    enemyFilter.IsGhost = False
    enemyFilter.Warmode = -1
    enemyFilter.Friend = False
    enemyFilter.Paralized = -1
    enemyFilter.Notorieties = List[Byte](bytes([4, 5, 6]))
    # blue = 1, green = 2, grey = 3, grey(aggro) = 4, orange = 5, red = 6

    # check if target is provided
    if target is None:
        # get enemies
        enemies = Mobiles.ApplyFilter(enemyFilter)
        # filter out enemies named "bob"
        for i in range(len(enemies) - 1, -1, -1):
            if enemies[i].Name == "bob":
                del enemies[i]
        # check if enemies found and select one
        if len(enemies) > 0:
            # select nearest enemy
            enemy = Mobiles.Select(enemies, "Nearest")

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
                Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
                continue
            elif spellName == "Poison":
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
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
            # debug
            # Sound.Log(True)
            # sounds = List[Int32]([249])  # meditation sound
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
        "cast_Flamestrike.py",
    ]

    for script in scripts:
        if Misc.ScriptStatus(script) and script != castScript:
            Misc.ScriptStop(script)


def FindScroll(spellname):
    """
    Finds a scroll in the player's backpack.
    Searches recursively.
    """
