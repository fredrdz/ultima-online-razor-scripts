from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Poison"
scriptName = "cast_Poison.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
