# Description: Magery related functions

# System packages
from System import Byte
from System import Int32
from System.Collections.Generic import List

# Custom RE packages
import config
import Items, Journal, Misc, Mobiles, Player, Spells, Sound, Target, Timer
from glossary.colors import colors
from glossary.spells import reagents, spells
from glossary.items.scrolls import mageryScrolls
from glossary.items.potions import potions
from utils.item_actions.common import equip_left_hand
from utils.items import FindItem, FindNumberOfItems


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
            Player.HeadMessage(colors["debug"], "[meditating]")
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
        Player.HeadMessage(colors["debug"], "[full mp]")


# ---------------------------------------------------------------------
# Reagents and scrolls


def FindScrollBySpell(spellname):
    """
    Uses FindItem to recursively search for a specific spell scroll in backpack.
    Returns the item object if found, otherwise None.
    """
    # validate
    if not isinstance(spellname, str) or not spellname:
        Misc.SendMessage(">> invalid spell scroll name", colors["fatal"])
        Misc.Pause(5000)
        return None

    scroll_name = spellname + " scroll"

    if scroll_name in mageryScrolls:
        scroll_id = mageryScrolls[scroll_name].itemID
        return FindItem(scroll_id, Player.Backpack)
    else:
        return None


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
# Casting magery spells


def CastSpellOnSelf(spellName, delay=None):
    """
    Casts a spell self (on the player)
    """
    # validate
    if not isinstance(spellName, str) or not spellName:
        Misc.SendMessage(">> invalid spell name", colors["fatal"])
        Misc.Pause(5000)
        return

    # init
    spell = spells[spellName]
    scroll = FindScrollBySpell(spell.name)
    ## debug ##
    if spell.name == "Magic Reflection":
        scroll = None
    ## end debug ##

    if scroll:
        Player.HeadMessage(colors["debug"], f"[scroll: {spell.name}]")
        Items.UseItem(scroll)
    else:
        Spells.CastMagery(spell.name)

    Target.WaitForTarget(200, False)
    Target.Self()

    if delay is None or not isinstance(delay, int):
        # use default delay if delay is None or not an int
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
    # validate
    if not isinstance(spellName, str) or not spellName:
        Misc.SendMessage(">> invalid spell name", colors["fatal"])
        Misc.Pause(5000)
        return

    # init
    spell = spells[spellName]
    scroll = FindScrollBySpell(spell.name)

    if scroll:
        # Player.HeadMessage(colors["debug"], f"[scroll: {spell.name}]")
        Items.UseItem(scroll)
    else:
        Spells.CastMagery(spell.name)

    Target.WaitForTarget(200, False)
    Target.TargetExecute(target)

    if delay is None or not isinstance(delay, int):
        # use default delay if delay is None or not an int
        delay = spell.delayInMs + config.shardLatency

    Misc.Pause(delay)


# filter for enemies
castFilter = Mobiles.Filter()
castFilter.Enabled = True
castFilter.RangeMin = 1
castFilter.RangeMax = 15
castFilter.CheckLineOfSight = True
castFilter.Poisoned = -1
castFilter.IsHuman = -1
castFilter.IsGhost = False
castFilter.Warmode = -1
castFilter.Friend = False
castFilter.Paralized = -1
castFilter.Notorieties = List[Byte](bytes([4, 5, 6]))
# blue = 1, green = 2, grey = 3, grey(aggro) = 4, orange = 5, red = 6


def CastSpellRepeatably(spellName="", enemy=None, casts=-1):
    """
    Casts a spell on the target multiple times
    """
    # init
    Player.HeadMessage(colors["status"], "[offensive]")

    # checks for shared spell casting cooldown to prevent fizzling
    cast_cd = Misc.ReadSharedValue("cast_cd")
    if cast_cd > 0:
        Timer.Create("cast_cd", cast_cd)

    # overwrites enemy mob target via script shared value if one is set
    shared_target = Misc.ReadSharedValue("kill_target")
    if shared_target > 0:
        enemy = Mobiles.FindBySerial(shared_target)

    # check if target is provided
    if not enemy:
        # get enemies
        enemies = Mobiles.ApplyFilter(castFilter)
        # filter out enemies named "bob"
        for i in range(len(enemies) - 1, -1, -1):
            if enemies[i].Name == "bob":
                del enemies[i]
        # check if enemies found and select one
        if len(enemies) > 0:
            # select nearest enemy
            enemy = Mobiles.Select(enemies, "Nearest")

    # init for loop
    Journal.Clear()
    shield = FindItem(0x1B74, Player.Backpack)
    mana_pot = FindItem(potions["greater mana potion"].itemID, Player.Backpack)
    cast_count = 0

    if enemy:
        # stop defense script
        Misc.ScriptStop("_defense.py")
        # show selected target
        Mobiles.Message(
            enemy,
            colors["alert"],
            ">> spell target <<",
        )
        # start attacking
        while enemy:
            Misc.Pause(25)

            # check if player has changed requested spell
            spellName = Misc.ReadSharedValue("spell")

            # equip shield (kite)
            if shield:
                equip_left_hand(shield, 1)

            # check hp/mp
            hp_diff = Player.HitsMax - Player.Hits
            mp_diff = Player.ManaMax - Player.Mana

            # check player status and act accordingly
            if 0 < hp_diff >= 70:
                Player.HeadMessage(colors["alert"], "[hp]")
                break
            elif Journal.SearchByType("You cannot move!", "System"):
                break
            elif (
                Player.WarMode is True
                and 0 < mp_diff >= 40
                and Timer.Check("pot_cd") is False
            ):
                if mana_pot:
                    Player.HeadMessage(colors["status"], "[gmana pot]")
                    Items.UseItem(mana_pot)
                    Timer.Create("pot_cd", 1000)
                    continue
            elif (
                Player.Str < Misc.ReadSharedValue("str")
                or Player.Dex < Misc.ReadSharedValue("dex")
                or Player.Int < Misc.ReadSharedValue("int")
            ):
                break
            elif Player.Poisoned and Timer.Check("cast_cd") is False:
                break
            # spell checks
            elif spellName == "":
                Player.HeadMessage(colors["debug"], "[no spell]")
                break
            elif Timer.Check("cast_cd") is True:
                Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
                continue
            elif cast_count == casts:
                break
            elif Player.Mana <= spells[spellName].manaCost:
                Player.HeadMessage(colors["fail"], "[oom]")
                break
            elif CheckReagents(spellName) is False:
                Player.HeadMessage(colors["fail"], "[no reagents]")
                break
            elif spellName == "Magic Reflection":
                continue
            # enemy checks
            elif not enemy:
                Player.HeadMessage(colors["debug"], "[enemy gone]")
                break
            elif enemy.IsGhost or enemy.Deleted:
                Player.HeadMessage(colors["debug"], "[enemy dead]")
                break
            elif Player.InRangeMobile(enemy, 14) is False:
                Player.HeadMessage(colors["debug"], "[enemy range]")
                break
            elif Journal.Search("Target cannot be seen."):
                Journal.Clear()
                Player.HeadMessage(colors["debug"], "[enemy los]")
                break
            # actual spell cast
            if Target.HasTarget():
                Target.Cancel()
            CastSpellOnTarget(enemy, spellName, 0)
            Timer.Create("cast_cd", spells[spellName].delayInMs + config.shardLatency)
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
            # increment cast count
            cast_count += 1
            # spell combos
            if spellName == "Curse":
                Misc.SetSharedValue("spell", "Poison")
                spellName = "Poison"
                Misc.Pause(25)
            elif spellName == "Magic Arrow":
                Misc.SetSharedValue("spell", "Paralyze")
                spellName = "Paralyze"
                Misc.Pause(25)
            elif spellName == "Paralyze":
                Misc.SetSharedValue("spell", "Weaken")
                spellName = "Weaken"
                Misc.Pause(25)
            elif spellName == "Weaken":
                Misc.SetSharedValue("spell", "Feeblemind")
                spellName = "Feeblemind"
                Misc.Pause(25)
            elif spellName == "Feeblemind":
                Misc.SetSharedValue("spell", "Clumsy")
                spellName = "Clumsy"
                Misc.Pause(25)
            elif spellName == "Clumsy":
                Misc.SetSharedValue("spell", "Poison")
                spellName = "Poison"
                Misc.Pause(25)
            elif spellName == "Poison":
                Misc.SetSharedValue("spell", "Flamestrike")
                spellName = "Flamestrike"
                Misc.Pause(25)
            ## debug ##
            # Sound.Log(True)
            # sounds = List[Int32]([249])  # meditation sound
            # exception checks
            ## end debug ##
    else:
        Player.HeadMessage(colors["debug"], "[no target]")

    # resume defense script
    Misc.ScriptRun("_defense.py")
    Misc.SetSharedValue("spell", "")
    return Timer.Remaining("cast_cd")
