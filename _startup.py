import BuyAgent, Player, Misc

# set shared values based on player name
if Player.Name == "Talik Starr":
    # stats
    Misc.SetSharedValue("str", 120)
    Misc.SetSharedValue("dex", 60)
    Misc.SetSharedValue("int", 120)
    # items
    Misc.SetSharedValue("young_runebook", 0x4003B289)
    # misc
    Misc.SetSharedValue("cast_cd", -1)
    # agents
    if BuyAgent.Status() is False:
        BuyAgent.ChangeList("regs")
        BuyAgent.Enable()


# ---------------------------------------------------------------------
# autorun watcher service
Misc.Pause(5000)  # wait 5s before running the scripts to let client load in
Misc.ScriptRun("_watcher.py")
