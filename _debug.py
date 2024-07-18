# System Packages
import sys

# Custom Packages
import Misc, Mobiles, Player, Target
from config import shardLatency
from glossary.colors import colors
from glossary.spells import spells
from utils.magery import Meditation, CastSpellOnSelf, CheckReagents, FindScrollBySpell

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

    # check if player has a scroll for spell
    gheal_scroll = FindScrollBySpell("Greater Heal")

    # test moblie targeted funcs here
    spell = "Greater Heal"
    for _ in range(3):
        # CastSpellOnTarget(target, spell)
        CastSpellOnSelf(
            "Greater Heal",
            0,
            # gheal_scroll,
        )
        # Misc.Pause(spells["Greater Heal"].scrollDelay + shardLatency)
        Misc.Pause(spells["Greater Heal"].delayInMs + shardLatency)
