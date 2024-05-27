"""
SCRIPT: train_Forensic.py
Author: Talik Starr
IN:RISEN
Skill: Forensic Evaluation
"""

import Items, Player, Target, Timer, Misc

# init
Timer.Create("skillCD", 1)

# a filter to find corpses
corpseFilter = Items.Filter()
corpseFilter.Enabled = True
corpseFilter.OnGround = True
corpseFilter.Movable = False
corpseFilter.RangeMax = 3
corpseFilter.IsCorpse = True

while not Player.IsGhost and Player.GetRealSkillValue(
    "Forensic Evaluation"
) < Player.GetSkillCap("Forensic Evaluation"):
    # slight wait to avoid high CPU usage
    Misc.Pause(100)

    # toggle off warmode
    if Player.WarMode is True:
        Player.SetWarMode(False)

    # find a corpse
    corpses = Items.ApplyFilter(corpseFilter)

    # if found, use skill on it
    if corpses:
        # check for skill cooldown
        if not Timer.Check("skillCD"):
            Player.UseSkill("Forensic Evaluation")
            Target.WaitForTarget(2000, False)
            Target.TargetExecute(corpses[0])
            Timer.Create("skillCD", 1050)
    else:
        Misc.SendMessage(">> no corpses found", 33)
        Misc.Beep()
        Misc.Pause(3000)
