from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Harm"
scriptName = "cast_Harm.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
