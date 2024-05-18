"""
Author: TheWarDoctor95
Other Contributors:
Last Contribution By: TheWarDoctor95 - March 23, 2019

Description: Finds the nearest enemy to attack. Prioritizes enemies in war mode
"""

from System.Collections.Generic import List
from glossary.enemies import GetEnemyNotorieties, GetEnemies
from utils.mobiles import GetEmptyMobileList


def FindEnemy():
    """
    Returns the nearest enemy
    """
    enemies = GetEnemies(Mobiles, 0, 12, GetEnemyNotorieties())

    if len(enemies) == 0:
        return None
    elif len(enemies) == 1:
        return enemies[0]
    else:
        enemiesInWarMode = GetEmptyMobileList(Mobiles)
        enemiesInWarMode.AddRange([enemy for enemy in enemies if enemy.WarMode])

        if len(enemiesInWarMode) == 0:
            return Mobiles.Select(enemies, "Nearest")
        elif len(enemiesInWarMode) == 1:
            return enemiesInWarMode[0]
        else:
            return Mobiles.Select(enemiesInWarMode, "Nearest")


enemy = FindEnemy()
if enemy is not None:
    Player.Attack(enemy)
