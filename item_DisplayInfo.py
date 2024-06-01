import Items, Misc, Target
from glossary.colors import colors

itemSerial = Target.PromptTarget("Select item to read props from:", colors["notice"])
item = Items.FindBySerial(itemSerial)
Misc.SendMessage(">> --ITEM INFO--", colors["info"])
Misc.SendMessage(">> item ID: %i" % item.ItemID, colors["info"])
Misc.SendMessage(">> hue: %i" % item.Hue, colors["info"])
Misc.SendMessage(">> item position: %s" % item.Position, colors["info"])
Misc.SendMessage(">> name: %s" % item.Name, colors["info"])
Misc.SendMessage(">> serial: %i" % item.Serial, colors["info"])
Misc.SendMessage(">> durability: %i" % item.Durability, colors["info"])
Misc.SendMessage(">> is container: %s" % item.IsContainer, colors["info"])
Misc.SendMessage(">> is corpse: %s" % item.IsCorpse, colors["info"])
Misc.SendMessage(">> is in bank: %s" % item.IsInBank, colors["info"])
Misc.SendMessage(">> is lootable: %s" % item.IsLootable, colors["info"])
Misc.SendMessage(">> is potion: %s" % item.IsPotion, colors["info"])
Misc.SendMessage(">> is resource: %s" % item.IsResource, colors["info"])
Misc.SendMessage(">> is two handed: %s" % item.IsTwoHanded, colors["info"])
Misc.SendMessage(">> is movable: %s" % item.Movable, colors["info"])
Misc.SendMessage(">> is on ground: %s" % item.OnGround, colors["info"])
Misc.SendMessage(">> weight: %i" % item.Weight, colors["info"])

if len(item.Properties) > 0:
    for prop in item.Properties:
        Misc.SendMessage(">> %s" % prop, colors["info"])
else:
    Misc.SendMessage(">> no properties found", colors["info"])
