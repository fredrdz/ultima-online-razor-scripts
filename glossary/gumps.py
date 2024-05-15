class GumpOption:
    def __init__(self, name, id):
        self.Name = name
        self.Id = id


class Gump:
    def __init__(self, name, id, options):
        self.Name = name
        self.Id = id
        self.Options = {option.Name: option for option in options}


runebookOpts = [
    GumpOption("Rename Book", 1),
    GumpOption("Slot 1", 2),
    GumpOption("Slot 2", 8),
    GumpOption("Slot 3", 14),
    GumpOption("Slot 4", 20),
    GumpOption("Slot 5", 26),
    GumpOption("Slot 6", 32),
    GumpOption("Slot 7", 38),
    GumpOption("Slot 8", 44),
    GumpOption("Slot 9", 50),
    GumpOption("Slot 10", 56),
    GumpOption("Slot 11", 62),
    GumpOption("Slot 12", 68),
    GumpOption("Slot 13", 74),
    GumpOption("Slot 14", 80),
    GumpOption("Slot 15", 86),
    GumpOption("Slot 16", 92),
]

afkOpts = [
    GumpOption("Button 0", 0),
    GumpOption("Button 1", 1),
    GumpOption("Button 2", 2),
    GumpOption("Button 3", 3),
    GumpOption("Button 4", 4),
    GumpOption("Button 5", 5),
    GumpOption("Button 6", 6),
    GumpOption("Button 7", 7),
    GumpOption("Button 8", 8),
    GumpOption("Button 9", 9),
]
gumps = {
    "runebook": Gump("runebook", 1431013363, runebookOpts),
    "afk": Gump("afk", 408109089, afkOpts),
}
