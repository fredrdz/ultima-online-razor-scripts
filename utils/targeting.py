import Misc, Mobiles, Player, Target

from glossary.colors import colors
from glossary.enemies import GetEnemyNotorieties, GetEnemies
from utils.mobiles import GetEmptyMobileList


def AttackFromEnemyFilter():
    """
    Target/Attack the nearest enemy in the enemy RE mobile filter.
    """
    enemy = Target.GetTargetFromList("enemy")
    if enemy is not None:
        if Target.HasTarget():
            Target.TargetExecute(enemy)
        else:
            Player.Attack(enemy)

        Target.SetLast(enemy)
    else:
        Player.HeadMessage(colors["red"], "No enemies nearby!")

    Misc.Pause(100)


def AttackFromEnemyList():
    """
    Target/Attack the nearest enemy in the GUI Targeting "enemy" list.
    """
    enemy = Target.GetTargetFromList("enemy")
    if enemy is not None:
        if Target.HasTarget():
            Target.TargetExecute(enemy)
        else:
            Player.Attack(enemy)

        Target.SetLast(enemy)
    else:
        Player.HeadMessage(colors["red"], "No enemies nearby!")

    Misc.Pause(100)


def FindEnemy():
    """
    Returns the nearest enemy while prioritizing enemies in war mode.
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


def AttackNearest():
    enemy = FindEnemy()
    if enemy is not None:
        Player.Attack(enemy)
