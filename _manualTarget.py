import Misc, Mobiles, Player, Target
from glossary.colors import colors

"""
This script is used to set a target for the player to kill.

Uses Razor Enhanced's Target.PromptTarget() to select a target.
Sets the target serial to the 'kill_target' script shared value.
That shared value is used in other scripts for targeting.
"""

target = Target.PromptTarget(">> select a target", colors["notice"])

if not target or target == -1:
    Player.HeadMessage(colors["status"], "[target cleared]")
    Misc.SetSharedValue("kill_target", -1)
elif target == Player.Serial:
    Player.HeadMessage(colors["status"], "[self cleared]")
    Misc.SetSharedValue("kill_target", -1)
elif target:
    Misc.SetSharedValue("kill_target", target)
    target = Mobiles.FindBySerial(target)
    Mobiles.Message(
        target,
        colors["warning"],
        ">> enemy",
    )
