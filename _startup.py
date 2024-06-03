import Player, Misc

# set shared values based on player name
if Player.Name == "Talik Starr":
    Misc.SetSharedValue("young_runebook", 0x4003B289)


# ---------------------------------------------------------------------
# autorun some scripts
Misc.Pause(5000)  # wait 5s before running the scripts to let client load in
Misc.ScriptRun("_defense.py")
# Misc.ScriptRun("train_AnimalTaming.py")
Misc.ScriptRun("train_Fletching.py")
