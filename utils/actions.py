from glossary.colors import colors


def Bank(x, y):
    Misc.SendMessage(">> waiting for bank", colors["status"])
    while Player.Position.X != x or Player.Position.Y != y:
        Misc.Pause(100)

    Player.ChatSay(colors["chat"], "bank")
    Misc.Pause(300)


def VendorSell(name, x, y):
    Misc.SendMessage(">> waiting for selling position", colors["status"])
    while Player.Position.X != x or Player.Position.Y != y:
        Misc.Pause(100)

    Player.ChatSay(colors["chat"], name + " sell")
    Misc.Pause(500)
