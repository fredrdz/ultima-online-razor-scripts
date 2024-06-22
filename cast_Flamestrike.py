from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Flamestrike"
scriptName = "cast_Flamestrike.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
