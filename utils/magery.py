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


def CastSpellOnSelf(spellName, delay=None, scroll=None):
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

    if scroll:
        Player.HeadMessage(colors["debug"], f"[scroll: {spell.name}]")
        Items.UseItem(scroll)
    else:
        Spells.CastMagery(spell.name)

    Target.WaitForTarget(200, False)
    Target.Self()

    if delay is None or not isinstance(delay, int):
        if scroll:
            delay = spell.scrollDelay + config.shardLatency
        else:
            delay = spell.delayInMs + config.shardLatency

    Misc.Pause(delay)


# Example usage
# CastSpellOnSelf("Greater Heal")  # Uses default delay
# CastSpellOnSelf("Greater Heal", 1500)  # Uses specified delay of 1500 ms
# CastSpellOnSelf("Greater Heal", "fast")  # Uses default delay due to invalid type


def CastSpellOnTarget(target, spellName, delay=None, scroll=None):
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

    if scroll:
        Player.HeadMessage(colors["debug"], f"[scroll: {spell.name}]")
        Items.UseItem(scroll)
    else:
        Spells.CastMagery(spell.name)

    Target.WaitForTarget(200, False)
    Target.TargetExecute(target)

    if delay is None or not isinstance(delay, int):
        if scroll:
            delay = spell.scrollDelay + config.shardLatency
        else:
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


def CastSpellRepeatably(spellName="", enemySerial=-1, casts=-1):
    """
    Casts a spell on the target multiple times
    """
    # init
    enemy = None

    # check if enemy is provided
    if enemySerial > 0:
        enemy = Mobiles.FindBySerial(enemySerial)
    else:
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
    # shield = FindItem(0x1B74, Player.Backpack)
    mana_pot = FindItem(potions["greater mana potion"].itemID, Player.Backpack)
    cast_count = 0

    if enemy:
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

            # immediate break if no spell is set
            if spellName == "":
                Player.HeadMessage(colors["debug"], "[no spell]")
                break

            spellMana = spells[spellName].manaCost
            spellDelay = spells[spellName].delayInMs

            # check if player has a scroll for spell
            scroll = FindScrollBySpell(spellName)
            if scroll:
                spellMana = spells[spellName].scrollMana
                spellDelay = spells[spellName].scrollDelay

            # equip shield (kite)
            # if shield:
            #     equip_left_hand(shield, 0)

            # check hp/mp
            hp_diff = Player.HitsMax - Player.Hits
            mp_diff = Player.ManaMax - Player.Mana

            # check player status and act accordingly
            if 0 < hp_diff >= 65:
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
            # spell checks
            elif cast_count == casts:
                break
            elif Player.Mana <= spellMana:
                Player.HeadMessage(colors["fail"], "[oom]")
                break
            elif CheckReagents(spellName) is False:
                Player.HeadMessage(colors["fail"], "[no reagents]")
                break
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
            # cast timer check
            elif Timer.Check("cast_cd") is True:
                continue
            elif spellName == "Magic Reflection":
                CastSpellOnSelf("Magic Reflection")
                Timer.Create("cast_cd", 1)
                Misc.SetSharedValue("spell", "Poison")
                continue
            # actual spell cast
            if Target.HasTarget():
                Target.Cancel()
            CastSpellOnTarget(enemy, spellName, 0, scroll)
            Timer.Create("cast_cd", spellDelay + config.shardLatency)
            # increment cast count
            cast_count += 1
            # spell combos
            if spellName == "Curse":
                Misc.SetSharedValue("spell", "Poison")
            elif spellName == "Magic Arrow":
                Misc.SetSharedValue("spell", "Weaken")
            elif spellName == "Paralyze":
                Misc.SetSharedValue("spell", "Weaken")
            elif spellName == "Weaken":
                Misc.SetSharedValue("spell", "Feeblemind")
            elif spellName == "Feeblemind":
                Misc.SetSharedValue("spell", "Clumsy")
            elif spellName == "Clumsy":
                Misc.SetSharedValue("spell", "Poison")
            elif spellName == "Poison":
                Misc.SetSharedValue("spell", "Lightning")
            elif spellName == "Flamestrike":
                Misc.SetSharedValue("spell", "Lightning")
            elif spellName == "Lightning":
                if enemy.Poisoned:
                    Misc.SetSharedValue("spell", "Flamestrike")
                    continue
                Misc.SetSharedValue("spell", "Poison")
            ## debug ##
            # Sound.Log(True)
            # sounds = List[Int32]([249])  # meditation sound
            # exception checks
            ## end debug ##
    else:
        Player.HeadMessage(colors["debug"], "[no target]")

    # back to defense script
    Misc.SetSharedValue("spell", "")
    return Timer.Remaining("cast_cd")
