def Overweight(limit):
    if Player.Weight >= limit:
        Misc.Beep()
        return True

    return False
