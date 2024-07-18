from utils.items import myItem

potions = {
    "keg of greater strength potions": myItem(
        "keg of greater strength potions", 0x1940, 0x03B8, "potion", 1
    ),
    "bottle of toxic poison": myItem(
        "bottle of toxic poison", 0x0EFB, 0x0785, "potion", 1
    ),
    # cure
    "lesser cure potion": myItem("lesser cure potion", 0x0F07, 0x0000, "potion", 1),
    "cure potion": myItem("cure potion", 0x0F07, 0x0000, "potion", 1),
    "greater cure potion": myItem("greater cure potion", 0x0F07, 0x0000, "potion", 1),
    # heal
    "lesser heal potion": myItem("lesser heal potion", 0x0F0C, 0x0000, "potion", 1),
    "heal potion": myItem("heal potion", 0x0F0C, 0x0000, "potion", 1),
    "greater heal potion": myItem("greater heal potion", 0x0F0C, 0x0000, "potion", 1),
    # mana
    "mana potion": myItem("mana potion", 0x0F09, 0x0388, "potion", 1),
    "greater mana potion": myItem("greater mana potion", 0x0F0D, 0x0387, "potion", 1),
    # poison
    "lesser poison potion": myItem("lesser poison potion", 0x0F0A, 0x0000, "potion", 1),
    # agility
    "lesser agility potion": myItem(
        "lesser agility potion", 0x0F08, 0x0000, "potion", 1
    ),
    "agility potion": myItem("agility potion", 0x0F08, 0x0000, "potion", 1),
    "greater agility potion": myItem(
        "greater agility potion", 0x0F08, 0x0000, "potion", 1
    ),
}
