# Description: Magery related functions
import config
import Journal, Misc, Player, Spells, Target
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

    Player.HeadMessage(colors["status"], "[MEDITATE]")
    Player.UseSkill("Meditation")

    while Player.Mana < Player.ManaMax:
        Misc.Pause(100)

        if Player.WarMode or Player.Hits < Player.HitsMax:
            Player.HeadMessage(colors["fail"], "[MEDITATED]")
            break

        if Journal.SearchByType("You cannot focus your concentration.", "System"):
            Player.HeadMessage(colors["fail"], "[MEDITATED]")
            break

        if Journal.SearchByType(
            "You are preoccupied with thoughts of battle.", "System"
        ):
            Player.SetWarMode(True)
            Player.HeadMessage(colors["fail"], "[MEDITATED]")
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
    Casts a spell
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
