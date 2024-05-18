from System.Collections.Generic import List
from glossary.enemies import GetEnemyNotorieties, GetEnemies
from utils.mobiles import GetEmptyMobileList
from utils.items import FindItem
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.colors import colors


def FindEnemy():
    """
    Returns the nearest enemy
    """
    enemies = GetEnemies(Mobiles, 0, 12, GetEnemyNotorieties())

    if len(enemies) == 0:
        return None
    elif len(enemies) == 1:
        return enemies[0]
    else:
        enemiesInWarMode = GetEmptyMobileList(Mobiles)
        enemiesInWarMode.AddRange([enemy for enemy in enemies if enemy.WarMode])

        if len(enemiesInWarMode) == 0:
            return Mobiles.Select(enemies, "Nearest")
        elif len(enemiesInWarMode) == 1:
            return enemiesInWarMode[0]
        else:
            return Mobiles.Select(enemiesInWarMode, "Nearest")


# enemy = FindEnemy()
# if enemy is not None:
#     Player.Attack(enemy)

while not Player.IsGhost:
    Journal.Clear()
    Misc.Pause(100)

    hasBandages = False
    bandages = FindBandage(Player.Backpack)
    if bandages is None:
        Misc.SendMessage(">> no bandages", colors["fatal"])

    if Player.Poisoned:
        Player.HeadMessage(colors["fail"], "[POISONED]")
        Target.ClearLastandQueue()
        Spells.CastMagery("Cure")
        Target.TargetExecute(Player.Self)
        Misc.Pause(1000)

    if Journal.SearchByType("You cannot move!", "System") or Journal.SearchByType(
        "You are frozen and cannot move.", "System"
    ):
        Player.HeadMessage(colors["fail"], "[PARALYZED]")
        Target.ClearLastandQueue()
        Spells.CastMagery("Magic Arrow")
        Target.TargetExecute(Player.Self)
        Misc.Pause(1100)

    # if Player.WarMode:
    #     Player.SetWarMode(False)
    # if Player.Hits < Player.HitsMax:
    #     Items.UseItem(bandages)
    #     Target.WaitForTarget(2000, False)
    #     Target.Self()
    #     Misc.Pause(2500)

    hp_diff = Player.HitsMax - Player.Hits
    if 0 < hp_diff > 20 and Player.Mana > 5 and not Timer.Check("mheal"):
        Target.ClearLastandQueue()
        Spells.CastMagery("Heal")
        Target.TargetExecute(Player.Self)
        Timer.Create("mheal", 675)
        Timer.Create("mheal", spells.spell["Heal"].delayInMs)

    mp_diff = Player.ManaMax - Player.Mana
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
