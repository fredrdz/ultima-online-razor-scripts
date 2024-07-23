# custom RE packages
from config import shardLatency
import Items, Journal, Misc, Mobiles, Player, Timer
from utils.item_actions.common import equip_left_hand, unequip_hands
from utils.items import FindItem
from glossary.items.potions import potions
from glossary.colors import colors

# init
enemy = None

# find items
weapon = FindItem(0x1403, Player.Backpack)
shield = FindItem(0x1B74, Player.Backpack)

# stop other scripts
scripts = ["_defense.py"]

for script in scripts:
    Misc.ScriptStop(script)


# main loop
while not Player.IsGhost:
    # reduce cpu usage
    Misc.Pause(25)

    # check hp
    hp_diff = Player.HitsMax - Player.Hits

    if 0 < hp_diff >= 60:
        Player.HeadMessage(colors["alert"], "[hp]")
        break

    # check for paralysis
    if Journal.SearchByType("You cannot move!", "System"):
        break

    # check for curse
    if (
        Player.Str < Misc.ReadSharedValue("str")
        or Player.Dex < Misc.ReadSharedValue("dex")
        or Player.Int < Misc.ReadSharedValue("int")
    ):
        break

    # check mp
    mp_diff = Player.ManaMax - Player.Mana

    if Player.WarMode is True:
        if Timer.Check("pot_cd") is False:
            # mana pots
            if 0 < mp_diff >= 40:
                mana_pot = FindItem(
                    potions["greater mana potion"].itemID, Player.Backpack
                )
                if mana_pot:
                    Player.HeadMessage(colors["debug"], "[gmana pot]")
                    Items.UseItem(mana_pot)
                    Timer.Create("pot_cd", 1000)

    # overwrites enemy mob target via script shared value if one is set
    shared_target = Misc.ReadSharedValue("kill_target")
    if shared_target > 0:
        enemy = Mobiles.FindBySerial(shared_target)

    # equip weapon
    if weapon:
        if Player.CheckLayer("RightHand"):
            unequip_hands()
        elif Player.CheckLayer("LeftHand"):
            if Player.GetItemOnLayer("LeftHand").ItemID != weapon.ItemID:
                unequip_hands()

        if not Player.CheckLayer("LeftHand"):
            equip_left_hand(weapon, 350 + shardLatency)

        if enemy and Timer.Check("attack_cd") is False:
            Player.Attack(enemy)
            Timer.Create("attack_cd", 30000)

        if enemy:
            if enemy.Poisoned:
                break

# resume defense script
Misc.ScriptRun("_defense.py")
Misc.SetSharedValue("spell", "Lightning")
