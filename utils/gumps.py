class GumpSelection:
    gumpID = None
    buttonID = None

    def __init__(self, gumpID, buttonID):
        self.gumpID = gumpID
        self.buttonID = buttonID


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
            ">> debug -- last gump line list: " + last_gump_line,
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
