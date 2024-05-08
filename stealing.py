# WIP
#SCRIPT: stealing.py
#Author: Talik Starr
#IN:RISEN
#Skill: Stealing

#--- PARAMETERS ---
short_delay = 20
journal_delay = 120
snoop_delay = 600
containers = [0xe76, 0xe75, 0xe74, 0xe78, 0xe7d, 0xe77]
bags = [0x0E76, 0xE75, 0xE74, 0xE78, 0xE77, 0x0E79]

# 0x0E7D trap box
# 0x0E79 pouch 
# 0x0E75 backpack
# 0x0E76 bag
#---------------------------------------------------------------------
# init; do not modify beyond this point
lockpickSerial = None
boxSerial = None
keySerial = None
import sys
#---------------------------------------------------------------------
def Steal():
    Journal.Clear()
    attempted = False
    Items.WaitForProps(item,500)
    
    while not attempted:
        
        if Items.GetPropValue(item, 'Blessed'):
            Player.HeadMessage(66 , 'Blessed Item')
            ignoreList.append(item.Serial)
            break
            
        #Player.HeadMessage(66,'Attempting')
        Player.UseSkill('Stealing')
        Misc.Pause(journal_delay)
        if Journal.SearchByType('You must wait a few moments to use another skill.', 'Regular'):
            Player.HeadMessage(66 , 'Skill Timer')
            Misc.Pause(journal_delay)
            Journal.Clear()
        elif Journal.SearchByType('You can\'t steal that.', 'System'):
            Player.HeadMessage(66 , 'Blessed Item')
            ignoreList.append(item)
            Journal.Clear()
            attempted = True
        else:
            Target.WaitForTarget(1500)
            while Player.DistanceTo(mark) > 1:
                Misc.Pause(short_delay)
            Target.TargetExecute(item)
            attempted = True

    is_steal_success()
#---------------------------------------------------------------------
#---------------------------------------------------------------------
def find():
    fil = Mobiles.Filter()
    fil.Enabled = True
    fil.RangeMax = 1
    fil.IsHuman = True
    fil.IsGhost = False
    fil.Friend = False
    fil.Notorieties = List[Byte](bytes(1,3,4,5,6))
    list = Mobiles.ApplyFilter(fil)

    return list
#---------------------------------------------------------------------
def IsStolen():
    while not Journal.SearchByType("success message", "Regular"):
        Misc.Pause(100)
        if Journal.SearchByType("neutral message", "System"):
            return True
        elif Journal.SearchByType("fail message", "Regular"):
            return False
    return True
#---------------------------------------------------------------------
def Is_Steal_Success(): 
    Misc.Pause(journal_delay)
    if Journal.Search('You fail to steal the item.'):
        Player.HeadMessage(33, 'FAILED')
    elif Journal.Search('You successfully steal the item.'):
        Player.HeadMessage(66, '└[∵┌]└[ ∵ ]┘[┐∵]┘')
        Player.HeadMessage(66, 'GOT EM')
        Player.ChatSay(52, "[organizeme")
        if recallAfterSteal:
            escape()
        sys.exit()
    else:
        Player.HeadMessage(66, 'third thing')
#---------------------------------------------------------------------
# main process
if Player.GetRealSkillValue('Snooping') < 100:
    Misc.SendMessage('not a theif', 33)
    Misc.Beep()
    sys.exit()

while Player.GetRealSkillValue('Stealing') < 100:
    Journal.Clear()
    InventoryCheck()
    Steal()
    if IsStolen():
        ReturnItem()
