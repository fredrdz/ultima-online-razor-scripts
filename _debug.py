# System Packages
import sys

# Custom Packages
import Misc, Mobiles, Player, Target
from config import shardLatency
from glossary.colors import colors
from glossary.spells import spells
from glossary.items.potions import potions
from glossary.items.scrolls import mageryScrolls
from utils.magery import Meditation, CastSpellOnSelf, CheckReagents, FindScrollBySpell
from utils.items import FindItem, FindNumberOfItems

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

    # find items
    gheal_scroll = FindScrollBySpell("Greater Heal")
    explo_pot = FindItem(potions["greater explosion potion"].itemID, Player.Backpack)

    # test mobile targeted funcs here
    ######

    # toss an explosion potion
    for _ in range(3):
        if explo_pot:
            Items.UseItem(explo_pot)
            Target.WaitForTarget(1000, False)
            Misc.Pause(2000)
            Player.HeadMessage(colors["debug"], "[explo toss]")
            Target.TargetExecute(target)
            Misc.Pause(12000)

    sys.exit()
    # unused code below for reference

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
