import Player, Misc

# List of scripts to watch and autorun
scripts_to_watch = [
    "_defense.py",
    # "skill_Lumberjacking.py",
    "train_Alchemy.py",
]

# watch/autorun scripts if stopped
while not Player.IsGhost:
    for script in scripts_to_watch:
        if not Misc.ScriptStatus(script):
            Misc.ScriptRun(script)

    # reduce CPU usage
    Misc.Pause(10000)
