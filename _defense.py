# custom RE packages
import config
import Items, Journal, Misc, Player, Target, Timer
from utils.item_actions.common import equip_left_hand
from utils.items import FindItem
from utils.magery import Meditation, CastSpellOnSelf, CheckReagents
from glossary.items.healing import FindBandage
from glossary.items.potions import potions
from glossary.spells import spells
from glossary.colors import colors

# init
# stop other scripts
scripts = ["_melee.py", "_cast.py"]
for script in scripts:
    Misc.ScriptStop(script)
# set shared values based on player name
str = Misc.ReadSharedValue("str")
dex = Misc.ReadSharedValue("dex")
int = Misc.ReadSharedValue("int")
# find items
bandages = FindBandage(Player.Backpack)
shield = FindItem(0x1B74, Player.Backpack)
# global cast cd timer
if Misc.ReadSharedValue("cast_cd") > 0:
    Timer.Create("cast_cd", Misc.ReadSharedValue("cast_cd"))

while not Player.IsGhost:
    Misc.Pause(50)

    if not bandages:
        Misc.SendMessage(">> no bandages", colors["fatal"])
        Misc.Pause(5000)
        continue

    # equip shield (kite)
    if shield:
        equip_left_hand(shield, 1)

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
            CastSpellOnSelf("Magic Arrow", 0)
            Timer.Create(
                "cast_cd", spells["Magic Arrow"].delayInMs + config.shardLatency
            )
            Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))

    # check for poison
    if Player.Poisoned:
        Player.HeadMessage(colors["alert"], "[poisoned]")
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
                CastSpellOnSelf(
                    "Bless", spells["Bless"].delayInMs + config.shardLatency
                )
                Timer.Create("cast_cd", spells["Bless"].delayInMs + config.shardLatency)
                Misc.SetSharedValue("cast_cd", Timer.Remaining("cast_cd"))
                # CastSpellOnSelf(
                #     "Protection", spells["Protection"].delayInMs + config.shardLatency
                # )

    # check hp
    hp_diff = Player.HitsMax - Player.Hits

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
        Timer.Create("bandage_cd", 2350 + config.shardLatency)

    if (
        0 < hp_diff >= 100
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
        0 < hp_diff >= 60
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

    if Player.WarMode is True:
        if Timer.Check("pot_cd") is False:
            # heal pots
            if 0 < hp_diff >= 110:
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
