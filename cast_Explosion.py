from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Explosion"
scriptName = "cast_Explosion.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
