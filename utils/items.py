import config


class myItem:
    name = None
    itemID = None
    color = None
    category = None
    weight = None

    def __init__(self, name, itemID, color, category, weight):
        self.name = name
        self.itemID = itemID
        self.color = color
        self.category = category
        self.weight = weight


# ---------------------------------------------------------------------
def MoveItemsByCount(itemListByID, srcContainer, dstContainer):
    """
    Moves items from the source container to the destination container based on the specified count for each item.
    If an item's individual amount is greater than 1, only a single count of the item is transferred.
    If an item's amount is 1, multiple counts of the item may be transferred.
    If the count is -1, the entire amount of the item type will be transferred.

    Args:
        itemListByID (list of tuples): List of tuples containing item IDs and counts to move.
        srcContainer (int): Serial of the source container.
        dstContainer (int): Serial of the destination container.

    Returns:
        bool: True if all items were successfully transferred according to the specified counts, False otherwise.
    """
    moved_items_count = {}  # dictionary to store the count of each moved item
    total_moved_count = 0  # total count of all moved items

    for item_id, count in itemListByID:
        items_found = 0  # keep track of how many items of this type have been moved
        if count == -1:
            # Move the entire amount of the item type
            for containerItem in Items.FindAllByID(item_id, -1, srcContainer, 0, False):
                item_name = containerItem.Name
                item_amount = containerItem.Amount
                Items.Move(containerItem, dstContainer, item_amount)
                # wait for the move to complete
                Misc.Pause(config.dragDelayMilliseconds + config.shardLatency)
                total_moved_count += item_amount
                moved_items_count[item_name] = item_amount
        else:
            # Move according to the specified count
            for containerItem in Items.FindAllByID(item_id, -1, srcContainer, 0, False):
                if items_found >= count:
                    break
                item_name = containerItem.Name
                item_amount = containerItem.Amount
                amount_to_move = min(item_amount, count - items_found)
                Items.Move(containerItem, dstContainer, amount_to_move)
                # wait for the move to complete
                Misc.Pause(config.dragDelayMilliseconds + config.shardLatency)
                items_found += 1
                total_moved_count += amount_to_move
                moved_items_count[item_name] = (
                    moved_items_count.get(item_name, 0) + amount_to_move
                )

    # generate the status message
    if total_moved_count > 0:
        status_message = ">> Moved items:\n"
        for item_name, count in moved_items_count.items():
            status_message += "   - %s: %i\n" % (item_name, count)
    else:
        status_message = ">> No items were moved."

    # send the status message
    Misc.SendMessage(status_message, 77)

    # Return True if all items were moved successfully according to the specified counts
    return total_moved_count == sum(count for _, count in itemListByID)


def RestockAgent(list):
    Restock.ChangeList(list)
    Restock.FStart()


# ---------------------------------------------------------------------
def FindItem(itemID, container, color=-1, ignoreContainer=[]):
    """
    Searches through the container for the item IDs specified and returns the first one found
    Also searches through any subcontainers, which Misc.FindByID() does not
    """

    ignoreColor = False
    if color == -1:
        ignoreColor = True

    if isinstance(itemID, int):
        foundItem = next(
            (
                item
                for item in container.Contains
                if (item.ItemID == itemID and (ignoreColor or item.Hue == color))
            ),
            None,
        )
    elif isinstance(itemID, list):
        foundItem = next(
            (
                item
                for item in container.Contains
                if (item.ItemID in itemID and (ignoreColor or item.Hue == color))
            ),
            None,
        )
    else:
        raise ValueError(
            "Unknown argument type for itemID passed to FindItem().", itemID, container
        )

    if foundItem != None:
        return foundItem

    subcontainers = [
        item
        for item in container.Contains
        if (item.IsContainer and not item.Serial in ignoreContainer)
    ]
    for subcontainer in subcontainers:
        foundItem = FindItem(itemID, subcontainer, color, ignoreContainer)
        if foundItem != None:
            return foundItem


def FindNumberOfItems(itemID, container, color=-1):
    """
    Recursively looks through a container for any items in the provided list
    Returns the a dictionary with the number of items found from the list
    """

    ignoreColor = False
    if color == -1:
        ignoreColor = True

    # Create the dictionary
    numberOfItems = {}

    if isinstance(itemID, int):
        # Initialize numberOfItems
        numberOfItems[itemID] = 0

        # Populate numberOfItems
        for item in container.Contains:
            if item.ItemID == itemID and (ignoreColor or item.Hue == color):
                numberOfItems[itemID] += item.Amount
    elif isinstance(itemID, list):
        # Initialize numberOfItems
        for ID in itemID:
            numberOfItems[ID] = 0

        # Populate numberOfItems
        for item in container.Contains:
            if item.ItemID in itemID and (ignoreColor or item.Hue == color):
                numberOfItems[item.ItemID] += item.Amount
    else:
        raise ValueError(
            "Unknown argument type for itemID passed to FindItem().", itemID, container
        )

    subcontainers = [item for item in container.Contains if item.IsContainer]

    # Iterate through each item in the given list
    for subcontainer in subcontainers:
        numberOfItemsInSubcontainer = FindNumberOfItems(itemID, subcontainer)
        for ID in numberOfItems:
            numberOfItems[ID] += numberOfItemsInSubcontainer[ID]

    return numberOfItems


def MoveItem(Items, Misc, item, destinationBag, amount=0):
    Items.Move(item, destinationBag, amount)
    # wait for the move to complete
    Misc.Pause(config.dragDelayMilliseconds)
