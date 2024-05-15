from glossary.items.tools import tools
from glossary.colors import colors
from utils.items import FindItem

fishingPole = FindItem(tools["fishing pole"].itemID, Player.Backpack)

if fishingPole is None:
    Misc.SendMessage(">> no fishing pole to use", colors["fatal"])
else:
    Items.UseItem(fishingPole)
    Target.WaitForTarget(2000, True)
    Target.TargetExecuteRelative(Player.Serial, 2)

Misc.Pause(50)
