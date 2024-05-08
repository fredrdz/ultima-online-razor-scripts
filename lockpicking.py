#SCRIPT: lockpicking.py
#Author: Talik Starr
#IN:RISEN
#Skill: Lockpicking

#--- PARAMETERS ---
lockPickID = 0x14FC
keyID = 0x100E
boxID = 0x0E7D
skillCooldown = 2500
serverDelay = 100
#---------------------------------------------------------------------
# init; do not modify
lockpickSerial = None
boxSerial = None
keySerial = None
import sys
#---------------------------------------------------------------------
def Lock():
    Items.UseItem(boxSerial)
    Misc.Pause(serverDelay)
    Items.UseItem(keySerial)
    if not Target.WaitForTarget(serverDelay, False):
        if Journal.SearchByType('I can\'t reach that.', "Regular"):
            Misc.SendMessage(">> already locked", 50)
        else:
            Lock()
    Target.TargetExecute(boxSerial)
    if Journal.WaitJournal("You lock it.", 1000):
        Misc.SendMessage(">> box locked", 77)
#---------------------------------------------------------------------    
def Lockpick():
    Misc.SendMessage(">> lockpicking...", 70)
    Items.UseItem(lockpickSerial)
    if not Target.WaitForTarget(skillCooldown + serverDelay, True):
        Lockpick()
    Target.TargetExecute(boxSerial)
#---------------------------------------------------------------------
def InventoryCheck():
    global lockpickSerial, boxSerial, keySerial
        
    if lockPickID is None or Items.BackpackCount(lockPickID, -1) == 0:
        Misc.SendMessage(">> no lockpicks!", 33)
        Misc.Beep()
        sys.exit()
    elif boxID is None or Items.BackpackCount(boxID, -1) == 0:
        Misc.SendMessage(">> no boxes!", 33)
        Misc.Beep()
        sys.exit()
    elif keyID is None or Items.BackpackCount(keyID, -1) == 0:
        Misc.SendMessage(">> missing key!", 33)
        Misc.Beep()
        sys.exit()
    else:
        lockpick = Items.FindByID( lockPickID , -1 , Player.Backpack.Serial )
        box = Items.FindByID( boxID , -1 , Player.Backpack.Serial )
        
        if box is not None:
            key = Items.FindByID( keyID , -1 , box.Serial )
            
        lockpickSerial = lockpick.Serial
        boxSerial = box.Serial
        keySerial = key.Serial  
#---------------------------------------------------------------------    
def IsUnlocked():
    while not Journal.SearchByType("The lock quickly yields to your skill.", "Regular"):
        Misc.Pause(100)
        if Journal.SearchByType("This does not appear to be locked.", "System"):
            return True
        elif Journal.SearchByType("You are unable to pick the lock.", "Regular"):
            return False
    return True
#---------------------------------------------------------------------
# main script loop 
while Player.GetRealSkillValue('Lockpicking') < 100:
    Journal.Clear()
    InventoryCheck()
    Lockpick()
    if IsUnlocked():
        Lock()
