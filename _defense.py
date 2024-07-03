# system packages
import sys

# custom RE packages
import config
import Items, Journal, Misc, Player, Target, Timer
from utils.items import FindItem
from utils.magery import Meditation, CastSpellOnSelf, CheckReagents
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.spells import spells
from glossary.colors import colors

# init
# global cast cd timer
if Misc.ReadSharedValue("cast_cd") > 0:
    Timer.Create("cast_cd", Misc.ReadSharedValue("cast_cd"))

while not Player.IsGhost:
    Journal.Clear()
    Misc.Pause(100)

    bandages = FindBandage(Player.Backpack)
    if bandages is None:
        Misc.SendMessage(">> no bandages", colors["fatal"])
        Misc.Pause(5000)
        continue

    # check for poison
    if Player.Poisoned:
        Player.HeadMessage(colors["fail"], "[poisoned]")
        # find cure method
        cure_pot = FindItem(potions["cure potion"].itemID, Player.Backpack)
        if cure_pot:
            Player.HeadMessage(colors["status"], "[cure pot]")
            Items.UseItem(cure_pot)
            Timer.Create("pot_cd", 1000)
        elif (
            Timer.Check("cast_cd") is False
            and Player.Mana >= spells["Cure"].manaCost
            and CheckReagents("Cure")
        ):
            CastSpellOnSelf("Cure", 0)
            Timer.Create("cast_cd", spells["Cure"].delayInMs + config.shardLatency)
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
            # CastSpellOnSelf(
            #     "Magic Reflection",
            #     spells["Magic Reflection"].delayInMs + config.shardLatency,
            # )

    # check for paralysis
    if (
        Journal.SearchByType("You cannot move!", "System")
        and Timer.Check("cast_cd") is False
    ):
        Player.HeadMessage(colors["fail"], "[paralyzed]")
        if Player.Mana >= spells["Magic Arrow"].manaCost and CheckReagents(
            "Magic Arrow"
        ):
            CastSpellOnSelf("Magic Arrow", 0)
            Timer.Create(
                "cast_cd", spells["Magic Arrow"].delayInMs + config.shardLatency
            )
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))

    # check hp
    hp_diff = Player.HitsMax - Player.Hits
    if (
        (0 < hp_diff > 1 or Player.Poisoned)
        and Timer.Check("bandage_cd") is False
        and Timer.Check("cast_cd") is False
    ):
        Items.UseItem(bandages)
        Target.WaitForTarget(1000, False)
        Target.Self()
        Timer.Create("bandage_cd", 2300 + config.shardLatency)

    if (
        0 < hp_diff >= 90
        and Player.Mana >= spells["Greater Heal"].manaCost
        and Timer.Check("cast_cd") is False
    ):
        if CheckReagents("Greater Heal"):
            CastSpellOnSelf("Greater Heal", 0)
            Timer.Create(
                "cast_cd", spells["Greater Heal"].delayInMs + config.shardLatency
            )
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
    elif (
        0 < hp_diff >= 30
        and Player.Mana >= spells["Heal"].manaCost
        and Timer.Check("cast_cd") is False
    ):
        if CheckReagents("Heal"):
            CastSpellOnSelf("Heal", 0)
            Timer.Create("cast_cd", spells["Heal"].delayInMs + config.shardLatency)
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))

    # check mp
    mp_diff = Player.ManaMax - Player.Mana
    if hp_diff == 0 and Player.WarMode is False:
        if mp_diff != 0:
            Meditation()

    if Timer.Check("pot_cd") is False:
        # mana pots
        if 0 < mp_diff >= 40:
            mana_pot = FindItem(potions["greater mana potion"].itemID, Player.Backpack)
            if mana_pot:
                Player.HeadMessage(colors["status"], "[gmana pot]")
                Items.UseItem(mana_pot)
                Timer.Create("pot_cd", 1000)
        # heal pots
        elif 0 < hp_diff >= 40:
            heal_pot = FindItem(potions["greater heal potion"].itemID, Player.Backpack)
            if heal_pot:
                Player.HeadMessage(colors["status"], "[gheal pot]")
                Items.UseItem(heal_pot)
                Timer.Create("pot_cd", 1000)

    # check for curse
    if Player.WarMode is True:
        if (
            Player.Str < Misc.ReadSharedValue("str")
            or Player.Dex < Misc.ReadSharedValue("dex")
            or Player.Int < Misc.ReadSharedValue("int")
        ):
            if (
                Timer.Check("cast_cd") is False
                and Player.Mana >= spells["Bless"].manaCost
                and CheckReagents("Bless")
            ):
                Player.HeadMessage(colors["status"], "[buffs]")
                # bless buff lasts about 3 mins
                CastSpellOnSelf(
                    "Bless", spells["Bless"].delayInMs + config.shardLatency
                )
                Timer.Create("cast_cd", spells["Bless"].delayInMs + config.shardLatency)
                Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
                # CastSpellOnSelf(
                #     "Protection", spells["Protection"].delayInMs + config.shardLatency
                # )
