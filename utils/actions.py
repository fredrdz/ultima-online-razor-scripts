from glossary.colors import colors
from utils.pathing import get_position, wait_on_position, Position
import clr

clr.AddReference("System.Speech")
from System.Speech.Synthesis import SpeechSynthesizer


# ---------------------------------------------------------------------


def Chat_on_position(chat_msg, position=None, sys_msg=None):
    if not position:
        position = get_position()

    wait_on_position(position)

    if sys_msg:
        Misc.SendMessage(">> %s" % sys_msg, colors["notice"])

    Player.ChatSay(colors["chat"], chat_msg)
    Misc.Pause(1000)


def audio_say(text):
    spk = SpeechSynthesizer()
    spk.Speak(text)


def Sell_items(name="Vendor", craftItem=None, x=0, y=0):
    if craftItem is None:
        Misc.SendMessage(">> no item(s) to sell", colors["fail"])
        return

    if x == 0 and y == 0:
        sell_position = get_position("no vendor sell position configured...")
    else:
        sell_position = Position(int(x), int(y))

    count = Items.BackpackCount(craftItem)
    if count > 1:
        Misc.SendMessage(">> " + str(count) + " items to sell", colors["status"])
        while Items.BackpackCount(craftItem) > 1:
            Chat_on_position("%s Sell" % name, sell_position)
