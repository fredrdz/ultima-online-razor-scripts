import config
import Items, Journal, Misc, Player, Target, Timer
from utils.items import FindItem
from utils.magery import Meditation, CastSpellOnSelf, CheckReagents
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.spells import spells
from glossary.colors import colors

# init
Timer.Create("cast_cd", 1)

while not Player.IsGhost:
    Journal.Clear()
    Misc.Pause(100)

    bandages = FindBandage(Player.Backpack)
    if bandages is None:
        Misc.SendMessage(">> no bandages", colors["fatal"])

    if Player.Poisoned and not Timer.Check("cast_cd"):
        Player.HeadMessage(colors["fail"], "[POISONED]")
        Target.ClearLastandQueue()
        if CheckReagents("Cure"):
            CastSpellOnSelf("Cure", 0)
            Timer.Create("cast_cd", spells["Cure"].delayInMs + config.shardLatency)

    if Journal.SearchByType("You cannot move!", "System") and not Timer.Check(
        "cast_cd"
    ):
        Player.HeadMessage(colors["fail"], "[PARALYZED]")
        Target.ClearLastandQueue()
        if CheckReagents("magic arrow"):
            CastSpellOnSelf("Magic Arrow", 0)
            Timer.Create(
                "cast_cd", spells["Magic Arrow"].delayInMs + config.shardLatency
            )

    hp_diff = Player.HitsMax - Player.Hits
    if 0 < hp_diff > 1 and not Timer.Check("bandage_cd") and not Timer.Check("cast_cd"):
        Items.UseItem(bandages)
        Target.WaitForTarget(2000, False)
        Target.Self()
        Timer.Create("bandage_cd", 2500 + config.shardLatency)

    if 0 < hp_diff > 30 and Player.Mana > 5 and not Timer.Check("cast_cd"):
        Target.ClearLastandQueue()
        if CheckReagents("Heal"):
            CastSpellOnSelf("Heal", 0)
            Timer.Create("cast_cd", spells["Heal"].delayInMs + config.shardLatency)

    mp_diff = Player.ManaMax - Player.Mana
    if hp_diff == 0 and not Player.WarMode:
        if not mp_diff == 0:
            Meditation()

    if not Timer.Check("pot_cd"):
        if 0 < mp_diff > 40:
            mana_pot = FindItem(potions["greater mana potion"].itemID, Player.Backpack)
            if mana_pot:
                Player.HeadMessage(colors["success"], "[GMANA POT]")
                Items.UseItem(mana_pot)
                Timer.Create("pot_cd", 10000)
        elif 0 < mp_diff > 20:
            mana_pot = FindItem(potions["mana potion"].itemID, Player.Backpack)
            if mana_pot:
                Player.HeadMessage(colors["success"], "[MANA POT]")
                Items.UseItem(mana_pot)
                Timer.Create("pot_cd", 10000)
