"""
SCRIPT: train_Resist.py
Author: Talik Starr
IN:RISEN
Skill: Magic Resist
"""

# system packages
import sys
from System import Int32
from System.Collections.Generic import List

# custom RE packages
import Items, Player, Misc, Timer
from glossary.colors import colors
from utils.magery import CastSpellOnSelf, CheckReagents
from utils.pathing import CheckTile, IsPosition

# init
skillName = "Magic Resist"
spellName = "Fire Field"
fireFieldIDs = List[Int32](0x3996)


def TrainResist():
    """
    Trains Magic Resist by casting Fire Field on the player
    Player runs on field and heals with bandages
    """
    while Player.IsGhost is False and Player.GetRealSkillValue(
        skillName
    ) < Player.GetSkillCap(skillName):
        # short pause to avoid high cpu usage
        Misc.Pause(100)

        # check if player has enough reagents to cast Fire Field
        if CheckReagents(spellName) is False:
            Misc.SendMessage(
                ">> not enough reagents to cast %s" % spellName, colors["fail"]
            )
            sys.exit()

        # check if enough mana
        if Player.Mana < 10:
            if not Misc.ScriptStatus("_defense.py"):
                Misc.ScriptRun("_defense.py")
            if Player.WarMode is True:
                Player.WarMode = False

        # setup an item filter to find fire fields
        fieldFilter = Items.Filter()
        fieldFilter.Graphics = fireFieldIDs
        fieldFilter.Enabled = True
        fieldFilter.RangeMin = 0
        fieldFilter.RangeMax = 10
        fieldFilter.OnGround = True

        # find fire fields around player
        fields = Items.ApplyFilter(fieldFilter)

        # hp check
        hp_diff = Player.HitsMax - Player.Hits

        # cast spell on self if no fields found
        if len(fields) == 0:
            # only cast if full hp
            if hp_diff == 0:
                CastSpellOnSelf(spellName)

        # check if player is on a field
        if len(fields) > 0:
            if Timer.Check("fieldMsgDelay") is False:
                Misc.SendMessage(
                    ">> total fire found: %i" % (len(fields)), colors["success"]
                )
                Timer.Create("fieldMsgDelay", 10000)

            farthestField = Items.Select(fields, "Farthest")
            pos = farthestField.Position
            while IsPosition(pos.X, pos.Y) is False:
                pathConfig = {
                    "search_statics": True,
                    "player_house_filter": True,
                    "items_filter": {
                        "Enabled": False,
                    },
                    "mobiles_filter": {
                        "Enabled": True,
                    },
                }
                if CheckTile(pos.X, pos.Y, pathConfig) is False:
                    break
                elif 0 < hp_diff > 60:
                    break
                # classicUO path finding
                Player.PathFindTo(pos)
                Misc.Pause(1000)


TrainResist()
