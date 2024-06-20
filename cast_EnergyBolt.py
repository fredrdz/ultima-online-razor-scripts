from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Energy Bolt"
scriptName = "cast_EnergyBolt.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
