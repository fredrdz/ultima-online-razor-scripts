# System packages
from System import Byte
from System.Collections.Generic import List

# custom RE packages
from config import shardLatency
import Items, Journal, Misc, Mobiles, Player, Timer
from utils.item_actions.common import equip_left_hand, unequip_hands
from utils.items import FindItem
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.colors import colors


# filter for enemies
attackFilter = Mobiles.Filter()
attackFilter.Enabled = True
attackFilter.RangeMin = 1
attackFilter.RangeMax = 14
attackFilter.CheckLineOfSight = True
attackFilter.Poisoned = -1
attackFilter.IsHuman = -1
attackFilter.IsGhost = False
attackFilter.Warmode = -1
attackFilter.Friend = False
attackFilter.Paralized = -1
attackFilter.Notorieties = List[Byte](bytes([4, 5, 6]))
# blue = 1, green = 2, grey = 3, grey(aggro) = 4, orange = 5, red = 6


# ---------------------------------------------------------------------
def PhysicalAttack(enemySerial=-1):
    # init
    enemy = None

    # check if enemy is provided
    if enemySerial > 0:
        enemy = Mobiles.FindBySerial(enemySerial)
    else:
        # get enemies
        enemies = Mobiles.ApplyFilter(attackFilter)
        # filter out enemies named "bob"
        for i in range(len(enemies) - 1, -1, -1):
            if enemies[i].Name == "bob":
                del enemies[i]
        # check if enemies found and select one
        if len(enemies) > 0:
            # select nearest enemy
            enemy = Mobiles.Select(enemies, "Nearest")

    # find items
    bandages = FindBandage(Player.Backpack)
    weapon = FindItem(0x0F4D, Player.Backpack)
    shield = FindItem(0x1B76, Player.Backpack)
    mana_pot = FindItem(potions["greater mana potion"].itemID, Player.Backpack)

    # start physical attack
    if enemy:
        # equip weapon
        if weapon:
            if Player.CheckLayer("LeftHand"):
                if Player.GetItemOnLayer("LeftHand").ItemID != weapon.ItemID:
                    unequip_hands()
            # elif Player.CheckLayer("RightHand"):
            #     if Player.GetItemOnLayer("RightHand").ItemID != weapon.ItemID:
            #         unequip_hands()

            # if not Player.CheckLayer("RightHand"):
            #     equip_left_hand(weapon, 300 + shardLatency)

            if not Player.CheckLayer("LeftHand"):
                equip_left_hand(weapon, 0 + shardLatency)

        Player.Attack(enemy)
        Player.AttackLast()

        # main loop
        while not Player.IsGhost:
            # reduce cpu usage
            Misc.Pause(25)

            # check hp
            hp_diff = Player.HitsMax - Player.Hits

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
                    if 0 < hp_diff >= 60:
                        Player.HeadMessage(colors["alert"], "[hp]")
                        break

            # enemy checks
            if enemy.IsGhost or enemy.Deleted:
                Player.HeadMessage(colors["debug"], "[enemy dead]")
                break
            elif Player.InRangeMobile(enemy, 8) is False:
                Player.HeadMessage(colors["debug"], "[enemy range]")
                break
            elif Journal.Search("Target cannot be seen."):
                Journal.Clear()
                Player.HeadMessage(colors["debug"], "[enemy los]")
                break

            # check for paralysis
            if Journal.SearchByType("You cannot move!", "System"):
                break

            # check mp
            mp_diff = Player.ManaMax - Player.Mana

            if Player.WarMode is True:
                if Timer.Check("pot_cd") is False:
                    # mana pots
                    if 0 < mp_diff >= 40:
                        if mana_pot:
                            Player.HeadMessage(colors["debug"], "[gmana pot]")
                            Items.UseItem(mana_pot)
                            Timer.Create("pot_cd", 1000)

            # check if spell cast requested
            spell = Misc.ReadSharedValue("spell")
            if spell:
                Player.HeadMessage(
                    colors["debug"],
                    f"[spell requested: {spell}]",
                )
                break
    else:
        Player.HeadMessage(colors["debug"], "[no target]")

    # back to defense script
    Misc.SetSharedValue("physical_attack", False)


# ---------------------------------------------------------------------
