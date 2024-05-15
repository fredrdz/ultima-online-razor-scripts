'''
Author: TheWarDoctor95
Other Contributors:
Last Contribution By: TheWarDoctor95 - April 26, 2019

Description: Trains Blacksmithy to its cap
'''

import config
from glossary.items.ores import ores
from glossary.crafting.blacksmithing import blacksmithTools, FindBlacksmithTool, blacksmithCraftables
from glossary.colors import colors
from utils.items import FindItem, FindNumberOfItems, MoveItem

# Set to serial of bag or 'pet' for the mount that you are on
# Set to None if you don't want to keep slayers
slayerBag = "pet"
petName = "Packy"


def FindPet(name):
    """
    Finds pet to use for storage
    """

    petFilter = Mobiles.Filter()
    petFilter.Enabled = True
    petFilter.RangeMin = 0
    petFilter.RangeMax = 1
    petFilter.Name = name

    pet = Mobiles.ApplyFilter(petFilter)[0]
    return pet

def SmeltItems( itemID ):
    '''
    Smelts all items in the player's backpack that match the item ID given
    Returns True if all items were smelted successfully, False if not all the items were smelted
    '''

    tool = FindBlacksmithTool( Player.Backpack )
    if tool is None:
        Misc.SendMessage(">> no tools to train with", colors["fatal"])
        return False

    itemToSmelt = FindItem( itemID, Player.Backpack )
    while itemToSmelt != None and tool != None:
        # Make sure the tool isn't broken. If it is broken, this will return None
        tool = Items.FindBySerial( tool.Serial )
        if tool is None:
           tool = FindBlacksmithTool( Player.Backpack )
           if tool is None:
                Misc.SendMessage(">> no tools to train with", colors["fatal"])
               return False

        Items.UseItem( tool )
        Gumps.WaitForGump( 949095101, 2000 )
        Gumps.SendAction( 949095101, 14 )

        Target.WaitForTarget( 2000, True )
        Target.TargetExecute( itemToSmelt.Serial )

        # wait for the smelting to finish
        Misc.Pause( 1000 )

        # close the Blacksmithing gump
        Gumps.WaitForGump( 949095101, 2000 )
        Gumps.SendAction( 949095101, 0 )

        itemToSmelt = FindItem( itemID, Player.Backpack )

    return True


def TrainBlacksmithing():
    '''
    Trains Blacksmithy to its skill cap
    '''

    if Player.GetRealSkillValue( 'Blacksmith' ) == Player.GetSkillCap( 'Blacksmith' ):
        Misc.SendMessage(">> maxed out blacksmithy skill", colors["notice"])
        return

    tool = FindBlacksmithTool( Player.Backpack )
    if tool is None:
        Misc.SendMessage(">> no tools to train with", colors["fatal"])
        return

    while not Player.IsGhost and Player.GetRealSkillValue( 'Blacksmith' ) < Player.GetSkillCap( 'Blacksmith' ):
        # make sure the tool isn't broken. If it is broken, this will return None
        tool = Items.FindBySerial( tool.Serial )
        if tool is None:
            tool = FindBlacksmithTool( Player.Backpack )
            if tool is None:
                Misc.SendMessage(">> no tools to train with", colors["fatal"])
                break

        # Select the item to craft
        itemToCraft = None
        if Player.GetSkillValue( 'Blacksmith' ) < 40.0:
            Misc.SendMessage(">> skill too low...", colors["fatal"])
            Misc.SendMessage(">> use gold to train with an NPC", colors["fatal"])
            break
        elif Player.GetSkillValue( 'Blacksmith' ) < 45.0:
            itemToCraft = blacksmithCraftables[ 'mace' ]
        elif Player.GetSkillValue( 'Blacksmith' ) < 50.0:
            itemToCraft = blacksmithCraftables[ 'maul' ]
        elif Player.GetSkillValue( 'Blacksmith' ) < 55.0:
            itemToCraft = blacksmithCraftables[ 'cutlass' ]
        elif Player.GetSkillValue( 'Blacksmith' ) < 59.5:
            itemToCraft = blacksmithCraftables[ 'longsword' ]
        elif Player.GetSkillValue( 'Blacksmith' ) < 95.6:
            itemToCraft = blacksmithCraftables[ 'short spear' ]
        elif Player.GetSkillValue( 'Blacksmith' ) < 106.4:
            itemToCraft = blacksmithCraftables[ 'platemail gorget' ]
        elif Player.GetSkillValue( 'Blacksmith' ) < 108.9:
            itemToCraft = blacksmithCraftables[ 'platemail gloves' ]
        elif Player.GetSkillValue( 'Blacksmith' ) < 116.3:
            itemToCraft = blacksmithCraftables[ 'platemail arms' ]
        elif Player.GetSkillValue( 'Blacksmith' ) < 118.8:
            itemToCraft = blacksmithCraftables[ 'platemail legs' ]
        else:
            itemToCraft = blacksmithCraftables[ 'platemail (tunic)' ]

        enoughResourcesToCraftWith = True
        ironIngots = FindNumberOfItems( 0x1BF2, Player.Backpack, 0x0000 )
        if ironIngots[ 0x1BF2 ] < itemToCraft.resourcesNeeded[ 'ingots' ]:
            if itemToCraft.name == 'short spear':
                smeltSuccessful = SmeltItems( 0x1403 )
                if not smeltSuccessful:
                    return
                ironIngots = FindNumberOfItems( 0x1BF2, Player.Backpack, 0x0000 )
                if ironIngots[ 0x1BF2 ] < itemToCraft.resourcesNeeded[ 'ingots' ]:
                    enoughResourcesToCraftWith = False
            else:
                enoughResourcesToCraftWith = False

        if not enoughResourcesToCraftWith:
            Misc.SendMessage(">> out of resources", colors["fatal"])
            return

        Items.UseItem( tool )
        for path in itemToCraft.gumpPath:
            Gumps.WaitForGump( path.gumpID, 2000 )
            Gumps.SendAction( path.gumpID, path.buttonID )

        # close the Blacksmithing gump
        Gumps.WaitForGump( itemToCraft.gumpPath[ 0 ].gumpID, 5000 )
        Gumps.SendAction( itemToCraft.gumpPath[ 0 ].gumpID, 0 )

        itemType = None
        if itemToCraft.name == 'mace':
            itemType = 0x0F5C
        elif itemToCraft.name == 'maul':
            itemType = 0x143B
        elif itemToCraft.name == 'cutlass':
            itemType = 0x1441
        elif itemToCraft.name == 'longsword':
            itemType = 0x0F61
        elif itemToCraft.name == 'short spear':
            itemType = 0x1403
        elif itemToCraft.name == 'platemail gorget':
            itemType = 0x1413
        elif itemToCraft.name == 'platemail gloves':
            itemType = 0x1414
        elif itemToCraft.name == 'platemail arms':
            itemType = 0x1410
        elif itemToCraft.name == 'platemail legs':
            itemType = 0x1411
        elif itemToCraft.name == 'platemail (tunic)':
            itemType = 0x1415
        item = FindItem( itemType, Player.Backpack )

        if slayerBag != None and Journal.SearchByType( 'You have successfully crafted a slayer', 'Regular' ):
            Journal.Clear()
            item = FindItem( 0x1403, Player.Backpack )
            if slayerBag == 'pet':
                pet = FindPet()
                MoveItem( Items, Misc, item, pet.Backpack )
                Misc.Pause( config.dragDelayMilliseconds )
            else:
                MoveItem( Items, Misc, item, slayerBag )

        if Player.Weight > Player.MaxWeight:
            smeltSuccessful = SmeltItems( itemType )
            if not smeltSuccessful:
                return

        Misc.Pause( 100 )

# Start Blacksmithing training
TrainBlacksmithing()
