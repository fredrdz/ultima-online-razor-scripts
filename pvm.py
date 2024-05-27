import Items, Journal, Misc, Player, Spells, Target, Timer
from glossary.colors import colors
from glossary.spells import spells
from utils.targeting import AttackFromEnemyFilter

if not Misc.ScriptStatus("_defense.py"):
    Misc.ScriptRun("_defense.py")

while not Player.IsGhost:
    Misc.Pause(100)

    if Player.FollowersMax - Player.Followers >= 2 and Player.Mana >= 40:
        Spells.CastMagery("Summon Daemon")
        Misc.Pause(spells["Summon Daemon"].delayInMs)
        Player.ChatSay(colors["chat"], "All Guard Me")

    AttackFromEnemyFilter()
