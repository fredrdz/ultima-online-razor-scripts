from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Fireball"
scriptName = "cast_Fireball.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
