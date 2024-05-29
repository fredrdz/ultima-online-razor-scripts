# custom RE packages
import Gumps, Misc
from glossary.colors import colors
from glossary.gumps import gumps

# System packages
import random


class GumpSelection:
    def __init__(self, GumpID, ButtonID):
        self.GumpID = GumpID
        self.ButtonID = ButtonID


# ---------------------------------------------------------------------
def is_afk_gump():
    afk = gumps["afk"]
    if Gumps.HasGump(afk.Id):
        return True
    return False


def get_afk_gump_button_options():
    gump_text_options = Gumps.LastGumpGetLineList()
    if gump_text_options:
        return [str(line) for line in gump_text_options]
    return None


def solve_afk_gump(text_list):
    afk = gumps["afk"]
    result_list = []
    current_word = ""

    for text in text_list:
        if isinstance(text, str):
            text = text.strip()
            if text:
                if "rightbutton" in text.lower():
                    result_list.append("Right Button")
                elif "wrongbutton" in text.lower():
                    result_list.append("Wrong Button")
                else:
                    current_word += text
                    if "rightbutton" in current_word.lower():
                        result_list.append("Right Button")
                        current_word = ""
                    elif "wrongbutton" in current_word.lower():
                        result_list.append("Wrong Button")
                        current_word = ""

    right_button_index = (
        result_list.index("Right Button") if "Right Button" in result_list else -1
    )

    if isinstance(right_button_index, int):
        if right_button_index != -1:
            Misc.SendMessage(
                ">> afk gump -Right Button- found at index: %i" % right_button_index,
                colors["info"],
            )
            Misc.Pause(random.randint(1000, 2000))
            Gumps.SendAction(afk.Id, right_button_index)
            Gumps.CloseGump(afk.Id)
            return True
        else:
            Misc.SendMessage(
                ">> afk gump -Right Button- not found; solve manually or die",
                colors["fatal"],
            )
    return False


# ---------------------------------------------------------------------
def debug_gump_lines(gump_id):
    if Gumps.HasGump(gump_id):
        gump_lines = Gumps.GetLineList(gump_id)
        if gump_lines:
            for gump_line in gump_lines:
                Misc.SendMessage(
                    ">> debug -- gump line:\n %s\n" % (gump_line), colors["debug"]
                )


def debug_last_gump_lines():
    last_gump_line_list = Gumps.LastGumpGetLineList()
    if last_gump_line_list:
        Misc.SendMessage(
            ">> debug -- last gump line list: " + last_gump_line_list,
            colors["debug"],
        )
        for last_gump_line in last_gump_line_list:
            Misc.SendMessage(
                ">> debug -- last gump line: " + last_gump_line,
                colors["debug"],
            )


def debug_gump(gump_id):
    if Gumps.HasGump(gump_id):
        gump_data = Gumps.GetGumpData(gump_id)
        if gump_data:
            Misc.SendMessage(
                ">> debug -- gump data:\n %s\n" % (gump_data), colors["debug"]
            )

            gump_strings = gump_data.gumpStrings
            if gump_strings:
                for gump_string in gump_strings:
                    Misc.SendMessage(
                        ">> debug -- gump string:\n %s\n" % (gump_string),
                        colors["debug"],
                    )

            gump_switches = gump_data.switches
            if gump_switches:
                for gump_switch in gump_switches:
                    Misc.SendMessage(
                        ">> debug -- gump switch:\n %s\n" % (gump_switch),
                        colors["debug"],
                    )

            gump_text = gump_data.text
            if gump_text:
                for gump_text_id in gump_text:
                    Misc.SendMessage(
                        ">> debug -- gump text:\n %s\n" % (gump_text_id),
                        colors["debug"],
                    )

            gump_text_id = gump_data.textID
            if gump_text_id:
                for gump_text_id in gump_text_id:
                    Misc.SendMessage(
                        ">> debug -- gump text id:\n %s\n" % (gump_text_id),
                        colors["debug"],
                    )


def debug_gump_raw(gump_id):
    if Gumps.HasGump(gump_id):
        gump_raw_data = Gumps.GetGumpRawData(gump_id)
        Misc.SendMessage(
            ">> debug -- gump raw data:\n %s\n" % (gump_raw_data), colors["debug"]
        )

        gump_raw_text = Gumps.GetGumpRawText(gump_id)
        Misc.SendMessage(
            ">> debug -- gump raw text:\n %s\n" % (gump_raw_text), colors["debug"]
        )
