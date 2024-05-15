"""
SCRIPT: train_Veterinary.py
Author: Talik Starr
IN:RISEN
Skill: Veterinary
"""

from config import targetClearDelayMilliseconds
from glossary.items.healing import FindBandage
from glossary.colors import colors


def TrainVeterinary():
    """
    Trains Veterinary to the skill cap
    """
    if Player.GetRealSkillValue("Veterinary") == Player.GetSkillCap("Veterinary"):
        Misc.SendMessage(">> maxed out veterinary skill", colors["notice"])
        return

    bandages = FindBandage(Player.Backpack)

    if bandages is None:
        Misc.SendMessage(">> no bandages to train with", colors["error"])
        return

    animal_one_serial = Target.PromptTarget("Select first animal to train on")
    animal_one_mobile = Mobiles.FindBySerial(animal_one_serial)
    Mobiles.Message(
        animal_one_mobile,
        colors["info"],
        "Selected first animal for Veterinary training",
    )

    # Misc.SendMessage(
    #     ">> debug -- 1:hp: %i/%i" % (animal_one_mobile.Hits, animal_one_mobile.HitsMax),
    #     colors["debug"],
    # )

    animal_two_serial = Target.PromptTarget("Select second animal to train on")
    animal_two_mobile = Mobiles.FindBySerial(animal_two_serial)
    Mobiles.Message(
        animal_two_mobile,
        colors["info"],
        "Selected second animal for Veterinary training",
    )

    animal_targets = [animal_one_mobile, animal_two_mobile]
    current_animal_index = 0

    all_stop_sent = False
    all_kill_sent = False

    while not Player.IsGhost and Player.GetRealSkillValue(
        "Veterinary"
    ) < Player.GetSkillCap("Veterinary"):
        if animal_targets[current_animal_index].Hits < 10:
            if not all_stop_sent:
                Player.ChatSay(colors["chat"], "All Stop")
                all_stop_sent = True
                all_kill_sent = False
        else:
            if not all_kill_sent:
                Player.ChatSay(colors["chat"], "All Kill")
                Target.WaitForTarget(2000, False)
                Target.TargetExecute(animal_targets[current_animal_index])
                all_kill_sent = True
                all_stop_sent = False

        # clear any previously selected target and the target queue
        Target.ClearLastandQueue()

        # wait for the target to finish clearing
        Misc.Pause(targetClearDelayMilliseconds)

        Items.UseItem(bandages)
        Target.WaitForTarget(2000, False)
        Target.TargetExecute(animal_targets[current_animal_index])

        # Rotate to the next animal
        current_animal_index = (current_animal_index + 1) % len(animal_targets)

        bandages = FindBandage(Player.Backpack)
        if bandages is None:
            Player.ChatSay(colors["chat"], "All Stop")
            Misc.SendMessage(">> ran out of bandages to train with", colors["error"])
            return

        Misc.Pause(2500)

    if Player.GetRealSkillValue("Veterinary") == Player.GetSkillCap("Veterinary"):
        Player.ChatSay(colors["chat"], "All Stop")
        Misc.SendMessage(">> veterinary training complete!", colors["success"])


# Start Veterinary training
TrainVeterinary()
