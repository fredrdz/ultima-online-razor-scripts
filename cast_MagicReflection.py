import Misc
from utils.magery import CastSpellOnSelf

# init
spellName = "Magic Reflection"
Misc.SetSharedValue("spell", spellName)
Misc.SetSharedValue("cast_cd", -1)

# reflect spell
CastSpellOnSelf(spellName)

# reset shared spell
Misc.SetSharedValue("spell", "")
