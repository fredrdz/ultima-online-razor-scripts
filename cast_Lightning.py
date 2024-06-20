from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Lightning"
scriptName = "cast_Lightning.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
