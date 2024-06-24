"""
SCRIPT: train_Tracking.py
Author: Talik Starr
IN:RISEN
Skill: Tracking
"""

# custom RE packages
import Gumps, Player, Misc, Timer
from glossary.colors import colors

# init
skillName = "Tracking"
skillCooldown = 1000
skillTimer = Timer.Create("skill_cd", 1)
trackGump = 2976808305
trackGumpPlayers = 993494147


def TrainTracking():
    """
    Trains Tracking to Skill Cap
    """
    while Player.IsGhost is False and Player.GetRealSkillValue(
        skillName
    ) < Player.GetSkillCap(skillName):
        # short pause to avoid high cpu usage
        Misc.Pause(100)

        # tracking
        if Timer.Check("skill_cd") is False:
            Player.UseSkill(skillName, False)
            Gumps.WaitForGump(trackGump, 1000)
            Gumps.SendAction(trackGump, 4)
            if Gumps.CurrentGump() == trackGumpPlayers:
                Misc.SendMessage(">> found players", colors["warning"])
                player_list = Gumps.LastGumpGetLineList()
                Gumps.CloseGump(trackGumpPlayers)
                if player_list:
                    player_list = [str(line) for line in player_list]
                    for player in player_list:
                        Misc.SendMessage(f"-- {player}", colors["warning"])
            # skill cooldown
            Timer.Create("skill_cd", skillCooldown)


TrainTracking()
