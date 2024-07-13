# custom RE packages
import config
import Items, Journal, Misc, Mobiles, Player, Target, Timer
from utils.item_actions.common import equip_left_hand, unequip_hands
from utils.items import FindItem
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.colors import colors

# init
enemy = None
# find items
bandages = FindBandage(Player.Backpack)
weapon = FindItem(0x0F62, Player.Backpack)
# stop other scripts
scripts = ["_defense.py", "_cast.py"]
for script in scripts:
    Misc.ScriptStop(script)
# global cast cd timer
if Misc.ReadSharedValue("cast_cd") > 0:
    Timer.Create("cast_cd", Misc.ReadSharedValue("cast_cd"))

while not Player.IsGhost:
    Misc.Pause(50)

    if not bandages:
        Misc.SendMessage(">> no bandages", colors["fatal"])
        Misc.Pause(5000)
        continue

    # check for paralysis
    if Journal.SearchByType("You cannot move!", "System"):
        break

    # check for poison
    if Player.Poisoned:
        Player.HeadMessage(colors["alert"], "[poisoned]")
        # find cure method
        cure_pot = FindItem(potions["cure potion"].itemID, Player.Backpack)
        if cure_pot:
            Player.HeadMessage(colors["debug"], "[cure pot]")
            Items.UseItem(cure_pot)
            Timer.Create("pot_cd", 1000)

    # check for curse
    if (
        Player.Str < Misc.ReadSharedValue("str")
        or Player.Dex < Misc.ReadSharedValue("dex")
        or Player.Int < Misc.ReadSharedValue("int")
    ):
        break

    # check hp
    hp_diff = Player.HitsMax - Player.Hits

    if 0 < hp_diff >= 60:
        Player.HeadMessage(colors["alert"], "[hp]")
        break
    elif (
        (0 < hp_diff > 40 or Player.Poisoned)
        and Timer.Check("bandage_cd") is False
        and Timer.Check("cast_cd") is False
    ):
        if Target.HasTarget():
            Target.Cancel()
        Items.UseItem(bandages)
        Target.WaitForTarget(200, False)
        Target.Self()
        Timer.Create("bandage_cd", 2350 + config.shardLatency)

    # check mp
    mp_diff = Player.ManaMax - Player.Mana

    if Player.WarMode is True:
        if Timer.Check("pot_cd") is False:
            # mana pots
            if 0 < mp_diff >= 55:
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

    # equip hand (spear) if we aren't casting anything
    if Timer.Check("cast_cd") is False and weapon:
        if Player.CheckLayer("RightHand"):
            unequip_hands()
        elif Player.CheckLayer("LeftHand"):
            if Player.GetItemOnLayer("LeftHand").ItemID != weapon.ItemID:
                unequip_hands()

        if not Player.CheckLayer("LeftHand"):
            equip_left_hand(weapon, 1)

        if enemy and Timer.Check("attack_cd") is False:
            Player.Attack(enemy)
            Timer.Create("attack_cd", 20000)

# resume defense script
Misc.ScriptRun("_defense.py")
Misc.SetSharedValue("spell", "")
