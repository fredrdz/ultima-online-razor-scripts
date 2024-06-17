import Player, Misc

# set shared values based on player name
if Player.Name == "Talik Starr":
    Misc.SetSharedValue("young_runebook", 0x4003B289)


# ---------------------------------------------------------------------
# autorun watcher service
Misc.Pause(5000)  # wait 5s before running the scripts to let client load in
Misc.ScriptRun("_watcher.py")
