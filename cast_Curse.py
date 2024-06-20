from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Curse"
scriptName = "cast_Curse.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
