from utils.magery import CastSpellRepeatably, StopAllCastsExcept

# init
spellName = "Magic Arrow"
scriptName = "cast_MagicArrow.py"

# stop other attack scripts before starting this one
StopAllCastsExcept(scriptName)

# go ham
CastSpellRepeatably(spellName)
