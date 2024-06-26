# System Packages
import sys

# Custom Packages
import Misc, Mobiles, Player, Target
from glossary.colors import colors
from utils.magery import CastSpellOnTarget

"""
Area to test functions.
"""

target = Target.PromptTarget(">> select a target", colors["notice"])

if not target or target == -1:
    Player.HeadMessage(colors["status"], "[no target selected]")
    sys.exit()
elif target == Player.Serial:
    Player.HeadMessage(colors["status"], "[targeted self]")

if target:
    target = Mobiles.FindBySerial(target)
    Mobiles.Message(
        target,
        colors["debug"],
        ">> debug target",
    )
    # test moblie targeted funcs here
    CastSpellOnTarget(target, "Flamestrike", 0)
