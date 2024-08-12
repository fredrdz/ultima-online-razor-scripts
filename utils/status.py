import Player, Misc


def Overweight(limit=Player.MaxWeight):
    if Player.Weight >= limit:
        Misc.Beep()
        return True

    return False
