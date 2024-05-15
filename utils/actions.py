from glossary.colors import colors
from utils.pathing import get_position, wait_on_position


def chat_on_position(chat_msg, position=None, sys_msg=None):
    if not position:
        position = get_position()

    wait_on_position(position)

    if sys_msg:
        Misc.SendMessage(">> %s" % sys_msg, colors["notice"])

    Player.ChatSay(colors["chat"], chat_msg)
    Misc.Pause(500)
