import Items, Misc, Restock, SellAgent
import config


class myItem:
    def __init__(self, name, itemID, color, category, weight):
        self.name = name
        self.itemID = itemID
        self.color = color
        self.category = category
        self.weight = weight


# ---------------------------------------------------------------------
def MoveItemsByCount(itemListByID, srcContainer, dstContainer):
    """
    Moves items from the source container to the destination container based on the requested count of each item.
    Works with stackable and non-stackable items:
        If an item's amount is 1, multiple counts of the same item may be transferred.
        If an items's amount is greater than 1, the requested amount of a single item will be transferred.

    If the requested count is -1, all items or amounts (if stackable) of that type will be transferred.
    Color is optional and defaults to 0 (natural color). Use -1 to ignore color.

    Args:
        itemListByID (list of tuples): List of tuples containing item IDs, optionally hue color, and counts to move.
        srcContainer (int): Serial of the source container.
        dstContainer (int): Serial of the destination container.

    Returns:
        bool: True if all items were successfully transferred according to the specified counts, False otherwise.
    """
    # init vars
    moved_items_count = {}  # dictionary to store the count of each moved item
    total_moved_count = 0  # total count of all moved items
    # anyColor = -1
    naturalColor = 0

    # some cleanup to avoid issues with dragging items
    Misc.ClearDragQueue()

    for item in itemListByID:
        if len(item) == 2:
            item_id, count = item
            color = naturalColor
        elif len(item) == 3:
            item_id, color, count = item
        else:
            raise ValueError("Invalid item tuple. Must contain 2 or 3 elements.")

        items_found = 0  # keep track of how many items of this type have been moved
        if count == -1:
            # Move the entire amount of the item type
            for containerItem in Items.FindAllByID(
                item_id, color, srcContainer, False, True
            ):
                item_name = containerItem.Name
                item_amount = containerItem.Amount
                Items.Move(containerItem, dstContainer, item_amount)
                # wait for the move to complete
                Misc.Pause(config.dragDelayMilliseconds + config.shardLatency)
                total_moved_count += item_amount
                moved_items_count[item_name] = (
                    moved_items_count.get(item_name, 0) + item_amount
                )
        else:
            # Move according to the specified count
            for containerItem in Items.FindAllByID(
                item_id, color, srcContainer, False, True
            ):
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

    # Calculate total requested count, handling both 2-element and 3-element tuples
    total_requested_count = 0
    count = 0
    for item in itemListByID:
        if len(item) == 2:
            _, count = item
        elif len(item) == 3:
            _, _, count = item
        total_requested_count += count

    # Return True if all items were moved successfully according to the specified counts
    return total_moved_count == total_requested_count


def EnableSellingAgent(list: str):
    if not isinstance(list, str):
        raise TypeError("The 'list' parameter must be a string.")

    SellAgent.ChangeList(list)
    if SellAgent.Status() is False:
        SellAgent.Enable()


def RestockAgent(list: str):
    if not isinstance(list, str):
        raise TypeError("The 'list' parameter must be a string.")

    Restock.ChangeList(list)
    Restock.FStart()
    while Restock.Status():
        Misc.Pause(100)


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

    if foundItem is not None:
        return foundItem

    subcontainers = [
        item
        for item in container.Contains
        if (item.IsContainer and item.Serial not in ignoreContainer)
    ]
    for subcontainer in subcontainers:
        foundItem = FindItem(itemID, subcontainer, color, ignoreContainer)
        if foundItem is not None:
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
