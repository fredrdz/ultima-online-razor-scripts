class Craftable:
    Name = None
    MinSkill = None
    ResourcesNeeded = None
    GumpPath = None

    def __init__(self, Name, MinSkill, ResourcesNeeded, GumpPath):
        self.Name = Name
        self.MinSkill = MinSkill
        self.ResourcesNeeded = ResourcesNeeded
        self.GumpPath = GumpPath
