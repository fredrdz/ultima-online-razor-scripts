import Misc
from utils.magery import CastSpellOnSelf

# init
spellName = "Magic Reflection"
Misc.SetSharedValue("spell", spellName)
Misc.SetSharedValue("cast_cd", -1)

# mind games
CastSpellOnSelf("Magic Arrow", 0)
Misc.ScriptStop("_defense.py")

# reflect spell
CastSpellOnSelf(spellName)

# reset shared spell
Misc.SetSharedValue("spell", "")
Misc.ScriptRun("_defense.py")
