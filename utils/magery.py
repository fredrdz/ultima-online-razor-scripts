# Description: Magery related functions
import Journal, Misc, Player, Spells, Target
from glossary.colors import colors


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
