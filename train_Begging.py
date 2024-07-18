"""
SCRIPT: train_Begging.py
Author: Talik Starr
IN:RISEN
Skill: Begging
"""

import Journal, Player, Misc, Mobiles, Target, Timer

# custom RE packages
from config import shardLatency
from glossary.colors import colors

# init
skillName = "Begging"


def FindBeggingTarget():
    """
    Finds the nearest NPC to beg from
    """
    begFilter = Mobiles.Filter()
    begFilter.Enabled = True
    begFilter.RangeMin = 0
    begFilter.RangeMax = 5
    begFilter.IsHuman = True
    begFilter.IsGhost = False

    begMobiles = Mobiles.ApplyFilter(begFilter)

    if len(begMobiles) > 0:
        return Mobiles.Select(begMobiles, "Nearest")

    return None


def TrainBegging():
    """
    Trains Begging skill to its skill cap
    """

    while not Player.IsGhost:
        # check if skill is maxed out
        if Player.GetRealSkillValue(skillName) == Player.GetSkillCap(skillName):
            break

        # find begging target
        begging_target = FindBeggingTarget()

        # beg from target
        if begging_target:
            Misc.SendMessage(f">> begging from {begging_target.Name}", colors["debug"])
            Player.UseSkill(skillName, False)
            Target.WaitForTarget(1000, False)
            Target.TargetExecute(begging_target.Serial)
            Misc.Pause(3150 + shardLatency)

    if Player.GetRealSkillValue(skillName) == Player.GetSkillCap(skillName):
        Misc.SendMessage(f">> maxed out {skillName} skill", colors["notice"])
        return


TrainBegging()
