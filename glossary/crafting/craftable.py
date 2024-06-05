class Craftable:
    def __init__(
        self, Name, Item, RetainsMark, RetainsColor, MinSkill, ResourcesNeeded, GumpPath
    ):
        self.Name = Name
        self.Item = Item
        self.RetainsMark = RetainsMark
        self.RetainsColor = RetainsColor
        self.MinSkill = MinSkill
        self.ResourcesNeeded = ResourcesNeeded
        self.GumpPath = GumpPath
