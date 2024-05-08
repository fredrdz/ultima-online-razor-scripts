def Bank(x, y):
    Misc.SendMessage(">> waiting for bank", 50)
    while Player.Position.X != x or Player.Position.Y != y:
        Misc.Pause(100)

    Player.ChatSay(77, "bank")
    Misc.Pause(300)


def VendorSell(name, x, y):
    Misc.SendMessage(">> waiting for selling position", 50)
    while Player.Position.X != x or Player.Position.Y != y:
        Misc.Pause(100)

    Player.ChatSay(77, name + " sell")
    Misc.Pause(500)
