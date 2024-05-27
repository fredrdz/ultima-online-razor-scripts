from System.Collections.Generic import List
from System import Environment
cont = Items.FindBySerial(Target.PromptTarget())
Items.UseItem(cont)
Misc.Pause(1100)
list =[]

def access(fname):
    rv = False
    try:
        with open(fname, 'r') as f:
            rv = True
    except:
        pass
    return rv

def getenv(name):
    rv = str(Environment.GetEnvironmentVariable(name))
    return rv
    
theFile = 'ContainedList'
    
def getInfo():
    for item in cont.Contains:
        name = Items.GetPropStringByIndex(item,0)
        if name == '':
            name = item.Name.split('(')[0]
        id = item.ItemID
        if not ('[{},{}]'.format(name,hex(id))) in list:
            list.append('[{},{}]'.format(name,hex(id)))
            thefile = "/".join([getenv('userprofile'), 'Documents', '{}.txt'.format(theFile)])
            file = open(thefile, 'w+')                
            file.write('\n'.join(list)) 
            file.write('\n')
            file.close()

    for l in list:
        Misc.SendMessage(l,50)
        
getInfo()