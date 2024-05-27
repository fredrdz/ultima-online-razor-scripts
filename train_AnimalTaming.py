"""
SCRIPT: train_AnimalTaming.py
Author: Talik Starr
IN:RISEN
Skill: Animal Taming
"""

import Journal, Player, Misc, Mobiles, Target, Timer
from System import Int32
from System.Collections.Generic import List

# custom RE packages
from glossary.colors import colors
from glossary import tameables

## Script options ##
# Change to the name that you want to rename the tamed animals to
renameTamedAnimalsTo = "bob"
# Add any name of pets to ignore
petsToIgnore = [
    "SpiritAirlines",
]
# Change to the number of followers you'd like to keep.
# The script will auto-release the most recently tamed animal if the follower number exceeds this number
# Some animals have a follower count greater than one, which may cause them to be released if this number is not set high enough
numberOfFollowersToKeep = 1
# Set to the maximum number of times to attempt to tame a single animal. 0 == attempt until tamed
maximumTameAttempts = 0
# Set the minimum taming difficulty to use when finding animals to tame
minimumTamingDifficulty = 75
# Change depending on the latency to your UO shard
journalEntryDelayMilliseconds = 100
targetClearDelayMilliseconds = 100

animalTamingTimerMilliseconds = 13000


def FindAnimalToTame():
    """
    Finds the nearest tameable animal nearby
    """
    global renameTamedAnimalsTo
    global minimumTamingDifficulty

    animalFilter = Mobiles.Filter()
    animalFilter.Enabled = True
    animalFilter.Bodies = List[Int32](
        tameables.GetAnimalIDsAtOrOverTamingDifficulty(minimumTamingDifficulty)
    )
    animalFilter.RangeMin = 0
    animalFilter.RangeMax = 12
    animalFilter.IsHuman = 0
    animalFilter.IsGhost = 0
    animalFilter.CheckIgnoreObject = True

    tameableMobiles = Mobiles.ApplyFilter(animalFilter)

    # Exclude animals that have already been tamed by this player
    tameableMobilesTemp = tameableMobiles[:]
    for tameableMobile in tameableMobiles:
        if tameableMobile.Name in petsToIgnore:
            tameableMobilesTemp.Remove(tameableMobile)

    tameableMobiles = tameableMobilesTemp

    if len(tameableMobiles) == 0:
        return None
    elif len(tameableMobiles) == 1:
        return tameableMobiles[0]
    else:
        return Mobiles.Select(tameableMobiles, "Nearest")


def TrainAnimalTaming():
    """
    Trains Animal Taming to GM
    """

    # user variables
    global renameTamedAnimalsTo
    global numberOfFollowersToKeep
    global maximumTameAttempts
    global journalEntryDelayMilliseconds
    global targetClearDelayMilliseconds

    # script variables
    global animalTamingTimerMilliseconds

    # initialize variables
    animalBeingTamed = None
    tameHandled = False
    tameOngoing = False
    timesTried = 0

    # initialize skill timers
    Timer.Create("animalTamingTimer", 1)

    # initialize the journal and ignore object list
    Journal.Clear()
    Misc.ClearIgnore()

    # toggle war mode to make sure the player isn't going to kill the animal being tamed
    Player.SetWarMode(True)
    Player.SetWarMode(False)

    while not Player.IsGhost and Player.GetRealSkillValue(
        "Animal Taming"
    ) < Player.GetSkillCap("Animal Taming"):
        if (
            animalBeingTamed is not None
            and Mobiles.FindBySerial(animalBeingTamed.Serial) is None
        ):
            Misc.SendMessage("Animal was killed or disappeared")
            animalBeingTamed = None

        if not maximumTameAttempts == 0 and timesTried > maximumTameAttempts:
            Mobiles.Message(
                animalBeingTamed,
                colors["error"],
                "Tried more than %i times to tame. Ignoring animal"
                % maximumTameAttempts,
            )
            Mobiles.IgnoreObject(animalBeingTamed)
            animalBeingTamed = None
            timesTried = 0

        # if there is no animal being tamed, try to find an animal to tame
        if animalBeingTamed is None:
            animalBeingTamed = FindAnimalToTame()
            if animalBeingTamed is None:
                # no animals in the area
                # pause for a while so that this is constantly running until something is available to tame
                Misc.Pause(1000)
                continue
            else:
                Mobiles.Message(
                    animalBeingTamed, colors["status"], "Found animal to tame"
                )

        # tame the animal if a tame is not currently being attempted and enough time has passed since last using Animal Taming
        if not tameOngoing and not Timer.Check("animalTamingTimer"):
            # clear any previously selected target and the target queue
            Target.ClearLastandQueue()
            # wait for the target to finish clearing
            Misc.Pause(targetClearDelayMilliseconds)

            # use taming skill
            Player.UseSkill("Animal Taming")
            Target.WaitForTarget(2000, False)
            Target.TargetExecute(animalBeingTamed)

            # check if Animal Taming was successfully triggered
            if Journal.SearchByType("Tame which animal?", "System"):
                timesTried += 1

                # restart the timer so that it will go off when we'll be able to use the skill again
                Timer.Create("animalTamingTimer", animalTamingTimerMilliseconds)

                # set tameOngoing to true to start the journal checks that will handle the result of the taming
                tameOngoing = True
            else:
                continue

        if tameOngoing:
            if Journal.SearchByType(
                "The %s accepts you as its master." % animalBeingTamed.Name,
                "System",
            ) or Journal.SearchByType("That wasn't even challenging.", "System"):
                # animal was successfully tamed
                if animalBeingTamed.Name != renameTamedAnimalsTo:
                    Misc.PetRename(animalBeingTamed, renameTamedAnimalsTo)
                if Player.Followers > numberOfFollowersToKeep:
                    # release recently tamed animal
                    Player.ChatSay(colors["chat"], "%s Release" % animalBeingTamed.Name)
                    Misc.Pause(500)
                # Misc.IgnoreObject(animalBeingTamed)
                animalBeingTamed = None
                timesTried = 0
                tameHandled = True
            elif Journal.SearchByType(
                "You fail to tame the creature.", "System"
            ) or Journal.SearchByType(
                "You must wait to perform another action.", "System"
            ):
                tameHandled = True
            elif (
                Journal.SearchByType("That is too far away.", "Regular")
                or Journal.SearchByName(
                    "You are too far away to continue taming.", animalBeingTamed.Name
                )
                or Journal.SearchByName(
                    "Someone else is already taming this", animalBeingTamed.Name
                )
            ):
                # animal moved too far away, set to None so that another animal can be found
                animalBeingTamed = None
                timesTried = 0
                Timer.Create("animalTamingTimer", 1)
                tameHandled = True
            elif Journal.SearchByType("That animal looks tame already.", "System"):
                Player.ChatSay(colors["chat"], "All Release")
                Misc.Pause(500)
                animalBeingTamed = None
                timesTried = 0
                Timer.Create("animalTamingTimer", 1)
                tameHandled = True
            elif (
                Journal.SearchByType(
                    "You have no chance of taming this creature", "System"
                )
                or Journal.SearchByType("Target cannot be seen", "System")
                or Journal.SearchByType(
                    "This animal has had too many owners and is too upset for you to tame.",
                    "System",
                )
                or Journal.SearchByType(
                    "You do not have a clear path to the animal you are taming, and must cease your attempt.",
                    "System",
                )
            ):
                # ignore the object and set to None so that another animal can be found
                # Misc.IgnoreObject(animalBeingTamed)
                animalBeingTamed = None
                timesTried = 0
                Timer.Create("animalTamingTimer", 1)
                tameHandled = True

            if tameHandled:
                Journal.Clear()
                tameHandled = False
                tameOngoing = False

        # wait a little bit so that the while loop doesn't consume as much CPU
        Misc.Pause(100)

        if Player.GetRealSkillValue("Animal Taming") == Player.GetSkillCap(
            "Animal Taming"
        ):
            Misc.SendMessage(">> maxed out taming skill", colors["notice"])
            return


# Start Animal Taming
TrainAnimalTaming()
