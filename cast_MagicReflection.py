import Misc, Player
from utils.magery import CastSpellOnSelf

spellName = "Magic Reflection"
Misc.SetSharedValue("spell", "")
Misc.SetSharedValue("cast_cd", -1)
Player.SetWarMode(False)
Player.SetWarMode(True)
CastSpellOnSelf(spellName)
