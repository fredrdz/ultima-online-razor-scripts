curePot = 0x0F07
while True:
    if Player.Poisoned:
        Items.UseItemByID(curePot)
    else:
        Misc.Pause(400)        
