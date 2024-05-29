# system packages
from System import Byte
from System.Collections.Generic import List

import clr

clr.AddReference("System.Speech")
from System.Speech.Synthesis import SpeechSynthesizer

# custom RE packages
import Items, Misc, Mobiles, Player, Timer
from glossary.colors import colors
from utils.pathing import (
    Get_position,
    Wait_on_position,
    Position,
    IsPosition,
    RazorPathing,
)


# ---------------------------------------------------------------------


def Chat_on_position(chat_msg, pos, sys_msg=None):
    if not pos:
        pos = Get_position()
    elif isinstance(pos, tuple):
        pos = Position(*pos)

    Wait_on_position(pos)

    if sys_msg:
        Misc.SendMessage(">> %s" % sys_msg, colors["notice"])

    Player.ChatSay(colors["chat"], chat_msg)
    Misc.Pause(1000)


def Audio_say(text):
    spk = SpeechSynthesizer()
    spk.Speak(text)


def Sell_items(name="Vendor", craftItem=None):
    # some validations
    if craftItem is None:
        Misc.SendMessage(">> no item configured for selling", colors["fatal"])
        return False

    if name == "Vendor":
        Misc.SendMessage(">> no vendor name specified", colors["fatal"])
        return False

    # mobile filter for finding npc vendor
    vendorFilter = Mobiles.Filter()
    vendorFilter.Enabled = True
    vendorFilter.Name = name
    vendorFilter.Notorieties = List[Byte](bytes([1]))
    vendorFilter.RangeMin = 0
    vendorFilter.RangeMax = 12
    vendorFilter.IsHuman = True
    vendorFilter.IsGhost = False
    vendorFilter.Warmode = False
    vendorFilter.CheckIgnoreObject = True

    vendorMobiles = Mobiles.ApplyFilter(vendorFilter)
    if not vendorMobiles:
        Misc.SendMessage(">> vendor not found", colors["fatal"])
        return False

    vendorMobile = vendorMobiles[0]

    Mobiles.Message(
        vendorMobile,
        colors["info"],
        "Vendor selected for selling items",
    )

    pos = vendorMobile.Position

    # go to the vendor
    Timer.Create("pathingTimeout", 10000)
    if IsPosition(pos.X, pos.Y) is False:
        if RazorPathing(pos.X, pos.Y) is False:
            Misc.SetSharedValue("pathFindingOverride", (pos.X, pos.Y))
            Misc.ScriptRun("pathfinding.py")
            while Misc.ScriptStatus("pathfinding.py") is True:
                Misc.Pause(100)
                if Timer.Check("pathingTimeout") is False:
                    Misc.SendMessage(">> pathing timed out", colors["fatal"])
                    Misc.ScriptStop("pathfinding.py")
                    return False

    # count items to sell and sell them
    count = Items.BackpackCount(craftItem)
    if count > 1:
        Misc.SendMessage(">> " + str(count) + " items to sell", colors["status"])
        Timer.Create("sellTimeout", 5000)
        while Items.BackpackCount(craftItem) > 1:
            Chat_on_position("%s Sell" % name, (pos.X, pos.Y))
            if Timer.Check("sellTimeout") is False:
                Misc.SendMessage(">> selling timed out", colors["fatal"])
                return False
        else:
            Misc.SendMessage(">> all items sold", colors["success"])
            return True
    else:
        Misc.SendMessage(">> no items to sell", colors["notice"])
        return True
