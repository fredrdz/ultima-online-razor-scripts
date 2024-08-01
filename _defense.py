# System packages
import sys

# custom RE packages
import Items, Journal, Misc, Player, Target, Timer
from config import shardLatency
from utils.items import FindItem
from utils.item_actions.common import equip_left_hand
from utils.melee import PhysicalAttack
from utils.magery import (
    CastSpellRepeatably,
    Meditation,
    CastSpellOnSelf,
    CheckReagents,
)
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.spells import spells
from glossary.colors import colors


# ---------------------------------------------------------------------
# init

# clear shared spell
Misc.SetSharedValue("spell", "")

# init event triggers
enemy = -1
spell = ""
physical_attack = False

# find items
bandages = FindBandage(Player.Backpack)
shield = FindItem(0x1B76, Player.Backpack)
cure_pot = FindItem(potions["cure potion"].itemID, Player.Backpack)
mana_pot = FindItem(potions["greater mana potion"].itemID, Player.Backpack)
heal_pot = FindItem(potions["greater heal potion"].itemID, Player.Backpack)


# ---------------------------------------------------------------------
if not bandages:
    Misc.SendMessage(">> no bandages", colors["fatal"])
    sys.exit()

# main loop
while not Player.IsGhost:
    Misc.Pause(25)

    # set hp/mp
    hp_diff = Player.HitsMax - Player.Hits
    mp_diff = Player.ManaMax - Player.Mana

    # check for poison
    if Player.Poisoned:
        if Timer.Check("cast_cd") is False:
            Player.HeadMessage(colors["alert"], "[poison]")
            # find cure method
            if Player.Mana > spells["Cure"].manaCost and CheckReagents("Cure"):
                if Target.HasTarget():
                    Target.Cancel()
                CastSpellOnSelf("Cure", 100)
                Timer.Create("cast_cd", spells["Cure"].delayInMs + shardLatency)
                continue
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
        Target.WaitForTarget(300, False)
        Target.Self()
        Timer.Create("bandage_cd", 3000 + shardLatency)
        if Target.HasTarget():
            Target.Cancel()

    # check pots
    if Player.WarMode is True:
        if Timer.Check("pot_cd") is False:
            # heal pots
            if 0 < hp_diff > 110:
                if heal_pot:
                    Items.UseItem(heal_pot)
                    Timer.Create("pot_cd", 500)
            # mana pots
            elif 0 < mp_diff > 40:
                if mana_pot:
                    Items.UseItem(mana_pot)
                    Timer.Create("pot_cd", 500)

    # check hp
    if 0 < hp_diff >= 100:
        if Player.Mana > spells["Heal"].manaCost and Timer.Check("cast_cd") is False:
            if CheckReagents("Heal"):
                if Target.HasTarget():
                    Target.Cancel()
                CastSpellOnSelf("Heal", 100)
                Timer.Create("cast_cd", spells["Heal"].delayInMs + shardLatency)
                continue
    elif 0 < hp_diff >= 50:
        if (
            Player.Mana > spells["Greater Heal"].manaCost
            and Timer.Check("cast_cd") is False
        ):
            if CheckReagents("Greater Heal"):
                if Target.HasTarget():
                    Target.Cancel()
                CastSpellOnSelf(
                    "Greater Heal",
                    100,
                )
                Timer.Create("cast_cd", spells["Greater Heal"].delayInMs + shardLatency)
                continue

    # check for paralysis
    if Journal.SearchByType("You cannot move!", "System"):
        if Timer.Check("cast_cd") is False:
            Player.HeadMessage(colors["alert"], "[paralyzed]")
            if Player.Mana > spells["Magic Arrow"].manaCost and CheckReagents(
                "Magic Arrow"
            ):
                Journal.Clear()
                CastSpellOnSelf("Magic Arrow")
                continue

    # set attack target
    if enemy <= 0:
        enemy = Misc.ReadSharedValue("kill_target")

    if enemy >= 0:
        if hp_diff <= 60:
            if Timer.Check("cast_cd") is False:
                # physical attack
                physical_attack = Misc.ReadSharedValue("physical_attack")
                if physical_attack:
                    Player.HeadMessage(colors["status"], "[weapon]")
                    PhysicalAttack(enemy)
                    # defend
                    Player.HeadMessage(colors["status"], "[defend]")
                    physical_attack = False
                    enemy = -1
                    continue

                # magic attack
                spell = Misc.ReadSharedValue("spell")
                if spell:
                    Player.HeadMessage(colors["status"], "[magic]")
                    remaining = CastSpellRepeatably("spell", enemy)
                    if remaining > 0:
                        Timer.Create("cast_cd", remaining)
                    # defend
                    Player.HeadMessage(colors["status"], "[defend]")
                    spell = ""
                    enemy = -1
                    continue

    # equip shield (kite)
    if shield:
        equip_left_hand(shield, 300 + shardLatency)

    # check if we can meditate
    if hp_diff == 0 and Player.WarMode is False:
        if mp_diff != 0:
            Meditation()
