# System packages
import sys

# custom RE packages
import Items, Journal, Misc, Player, Target, Timer
from config import shardLatency
from utils.items import FindItem
from utils.item_actions.common import equip_left_hand
from utils.magery import (
    CastSpellRepeatably,
    Meditation,
    CastSpellOnSelf,
    CheckReagents,
    FindScrollBySpell,
)
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.spells import spells
from glossary.colors import colors


# ---------------------------------------------------------------------

# stop other scripts
scripts = ["_melee.py"]
for script in scripts:
    Misc.ScriptStop(script)

# set shared values based on player name
str = Misc.ReadSharedValue("str")
dex = Misc.ReadSharedValue("dex")
int = Misc.ReadSharedValue("int")

# find items
bandages = FindBandage(Player.Backpack)
shield = FindItem(0x1B74, Player.Backpack)
cure_pot = FindItem(potions["cure potion"].itemID, Player.Backpack)
mana_pot = FindItem(potions["greater mana potion"].itemID, Player.Backpack)
heal_pot = FindItem(potions["greater heal potion"].itemID, Player.Backpack)
gheal_scroll = FindScrollBySpell("Greater Heal")

# init loop
Misc.SetSharedValue("spell", "")
enemy = -1
spell = ""


# ---------------------------------------------------------------------
if not bandages:
    Misc.SendMessage(">> no bandages", colors["fatal"])
    sys.exit()

# main loop
while not Player.IsGhost:
    Misc.Pause(25)

    # check hp
    hp_diff = Player.HitsMax - Player.Hits

    # check for poison
    if 0 < hp_diff >= 80:
        if Player.Poisoned:
            if Timer.Check("cast_cd") is False:
                Player.HeadMessage(colors["alert"], "[poisoned]")
                # find cure method
                if Player.Mana >= spells["Cure"].manaCost and CheckReagents("Cure"):
                    CastSpellOnSelf("Cure", 0)
                    Timer.Create("cast_cd", spells["Cure"].delayInMs + shardLatency)
                elif cure_pot and Timer.Check("pot_cd") is False:
                    Player.HeadMessage(colors["status"], "[cure pot]")
                    Items.UseItem(cure_pot)
                    Timer.Create("pot_cd", 1000)

    # use bandage
    if (
        (0 < hp_diff > 1 or Player.Poisoned)
        and Timer.Check("bandage_cd") is False
        and Timer.Check("cast_cd") is False
    ):
        if Target.HasTarget():
            Target.Cancel()
        Items.UseItem(bandages)
        Target.WaitForTarget(200, False)
        Target.Self()
        Timer.Create("bandage_cd", 2350 + shardLatency)

    # spell healing
    if 0 < hp_diff >= 110:
        if (
            gheal_scroll
            and Player.Mana >= spells["Greater Heal"].scrollMana
            and Timer.Check("cast_cd") is False
        ):
            if CheckReagents("Greater Heal"):
                CastSpellOnSelf(
                    "Greater Heal",
                    0,
                    gheal_scroll,
                )
                Timer.Create(
                    "cast_cd", spells["Greater Heal"].scrollDelay + shardLatency
                )
    elif 0 < hp_diff >= 100:
        if Player.Mana >= spells["Heal"].manaCost and Timer.Check("cast_cd") is False:
            if CheckReagents("Heal"):
                CastSpellOnSelf("Heal", 0)
                Timer.Create("cast_cd", spells["Heal"].delayInMs + shardLatency)
    elif 0 < hp_diff >= 70:
        if (
            Player.Mana >= spells["Greater Heal"].manaCost
            and Timer.Check("cast_cd") is False
        ):
            if CheckReagents("Greater Heal"):
                CastSpellOnSelf(
                    "Greater Heal",
                    0,
                )
                Timer.Create("cast_cd", spells["Greater Heal"].delayInMs + shardLatency)

    # check mp
    mp_diff = Player.ManaMax - Player.Mana
    if hp_diff == 0 and Player.WarMode is False:
        if mp_diff != 0:
            Meditation()

    if Player.WarMode is True:
        if Timer.Check("pot_cd") is False:
            # heal pots
            if 0 < hp_diff >= 110:
                if heal_pot:
                    Items.UseItem(heal_pot)
                    Timer.Create("pot_cd", 500)
            # mana pots
            elif 0 < mp_diff >= 40:
                if mana_pot:
                    Items.UseItem(mana_pot)
                    Timer.Create("pot_cd", 500)

    # check for paralysis
    if Journal.SearchByType("You cannot move!", "System"):
        if Timer.Check("cast_cd") is False:
            Player.HeadMessage(colors["alert"], "[paralyzed]")
            if Player.Mana >= spells["Magic Arrow"].manaCost and CheckReagents(
                "Magic Arrow"
            ):
                Journal.Clear()
                CastSpellOnSelf("Magic Arrow")

    # check for curse
    if Player.WarMode is True:
        if Player.Str < str or Player.Dex < dex or Player.Int < int:
            if (
                Timer.Check("cast_cd") is False
                and Player.Mana >= spells["Bless"].manaCost
                and CheckReagents("Bless")
            ):
                Player.HeadMessage(colors["alert"], "[cursed]")
                # bless buff lasts about 3 mins
                CastSpellOnSelf("Bless", 0)
                Timer.Create("cast_cd", spells["Bless"].delayInMs + shardLatency)

    # check bless

    # manual offensive targeting
    if enemy <= 0:
        enemy = Misc.ReadSharedValue("kill_target")

    # swap to offensive casting if spell is set
    if not spell:
        spell = Misc.ReadSharedValue("spell")
    else:
        # attack
        Player.HeadMessage(colors["status"], "[offensive]")
        remaining = CastSpellRepeatably("spell", enemy)
        if remaining > 0:
            Timer.Create("cast_cd", remaining)
        # defend
        Player.HeadMessage(colors["status"], "[defense]")
        spell = ""
        enemy = -1

    # equip shield (kite)
    if shield:
        equip_left_hand(shield, 0)
