# custom RE packages
import Items, Journal, Misc, Player, Target, Timer
from config import shardLatency
from utils.items import FindItem
from utils.item_actions.common import equip_left_hand
from utils.magery import Meditation, CastSpellOnSelf, CheckReagents, FindScrollBySpell
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.spells import spells
from glossary.colors import colors


# ---------------------------------------------------------------------
# init
Player.HeadMessage(colors["status"], "[defense]")

# stop other scripts
scripts = ["_melee.py", "_cast.py"]
for script in scripts:
    Misc.ScriptStop(script)

# set shared values based on player name
str = Misc.ReadSharedValue("str")
dex = Misc.ReadSharedValue("dex")
int = Misc.ReadSharedValue("int")

# find items
gheal_scroll = FindScrollBySpell("Greater Heal")
bandages = FindBandage(Player.Backpack)
shield = FindItem(0x1B74, Player.Backpack)
cure_pot = FindItem(potions["cure potion"].itemID, Player.Backpack)

# reset shared spell
Misc.SetSharedValue("spell", "")

# check shared cast cd timer
if Misc.ReadSharedValue("cast_cd") > 0:
    Timer.Create("cast_cd", Misc.ReadSharedValue("cast_cd"))

# ---------------------------------------------------------------------
# main loop
while not Player.IsGhost:
    Misc.Pause(50)

    if not bandages:
        Misc.SendMessage(">> no bandages", colors["fatal"])
        Misc.Pause(5000)
        continue

    # equip shield (kite)
    # if shield:
    #     equip_left_hand(shield, 0)

    # check hp
    hp_diff = Player.HitsMax - Player.Hits

    # check for poison
    if 0 < hp_diff > 40 and Player.Poisoned and Timer.Check("cast_cd") is False:
        Player.HeadMessage(colors["alert"], "[poisoned]")
        # find cure method
        if Player.Mana >= spells["Cure"].manaCost and CheckReagents("Cure"):
            CastSpellOnSelf("Cure")
            Misc.SetSharedValue("cast_cd", -1)
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

    if (
        0 < hp_diff >= 100
        and gheal_scroll
        and Player.Mana >= spells["Greater Heal"].scrollMana
        and Timer.Check("cast_cd") is False
    ):
        if CheckReagents("Greater Heal"):
            CastSpellOnSelf(
                "Greater Heal",
                0,
                gheal_scroll,
            )
            Timer.Create("cast_cd", spells["Greater Heal"].scrollDelay + shardLatency)
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
    elif (
        0 < hp_diff >= 90
        and Player.Mana >= spells["Heal"].manaCost
        and Timer.Check("cast_cd") is False
    ):
        if CheckReagents("Heal"):
            CastSpellOnSelf("Heal", 0)
            Timer.Create("cast_cd", spells["Heal"].delayInMs + shardLatency)
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
    elif (
        0 < hp_diff >= 40
        and Player.Mana >= spells["Greater Heal"].manaCost
        and Timer.Check("cast_cd") is False
    ):
        if CheckReagents("Greater Heal"):
            CastSpellOnSelf(
                "Greater Heal",
                0,
            )
            Timer.Create("cast_cd", spells["Greater Heal"].delayInMs + shardLatency)
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))

    # check mp
    mp_diff = Player.ManaMax - Player.Mana
    if hp_diff == 0 and Player.WarMode is False:
        if mp_diff != 0:
            Meditation()

    if Player.WarMode is True:
        if Timer.Check("pot_cd") is False:
            # heal pots
            if 0 < hp_diff >= 90:
                heal_pot = FindItem(
                    potions["greater heal potion"].itemID, Player.Backpack
                )
                if heal_pot:
                    Player.HeadMessage(colors["status"], "[gheal pot]")
                    Items.UseItem(heal_pot)
                    Timer.Create("pot_cd", 1000)
            # mana pots
            elif 0 < mp_diff >= 40:
                mana_pot = FindItem(
                    potions["greater mana potion"].itemID, Player.Backpack
                )
                if mana_pot:
                    Player.HeadMessage(colors["status"], "[gmana pot]")
                    Items.UseItem(mana_pot)
                    Timer.Create("pot_cd", 1000)

    # check for paralysis
    if (
        Journal.SearchByType("You cannot move!", "System")
        and Timer.Check("cast_cd") is False
    ):
        Player.HeadMessage(colors["alert"], "[paralyzed]")
        if Player.Mana >= spells["Magic Arrow"].manaCost and CheckReagents(
            "Magic Arrow"
        ):
            Journal.Clear()
            CastSpellOnSelf("Magic Arrow")
            Misc.SetSharedValue("cast_cd", -1)

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
                CastSpellOnSelf("Bless")
                Misc.SetSharedValue("cast_cd", -1)
                agility_pot = FindItem(
                    potions["greater agility potion"].itemID, Player.Backpack
                )
                if agility_pot:
                    Player.HeadMessage(colors["debug"], "[agility pot]")
                    Items.UseItem(agility_pot)
                    Timer.Create("pot_cd", 1000)
