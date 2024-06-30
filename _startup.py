import BuyAgent, Items, Player, Misc
from glossary.items.containers import containers

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
    Misc.SetSharedValue("kill_target", -1)
    # agents
    if BuyAgent.Status() is False:
        BuyAgent.ChangeList("regs")
        BuyAgent.Enable()


# wait 5s to let client load in
Misc.Pause(5000)

# load containers/bags into memory
# pouchs are trapped, so we don't include them
for backpack_item in Player.Backpack.Contains:
    if backpack_item.IsContainer and backpack_item.ItemID != containers["pouch"].itemID:
        Items.UseItem(backpack_item)

# autorun watcher service
Misc.ScriptRun("_watcher.py")
