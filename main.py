""" 
Pseudocode:
- for file in ./players
    - get uuid from filename
    - get playerName from file
    - get the relevant inventory data from ./smp_world using the lookup format "{playerName}.json"
    - Convert Inventory to TAG_Compound (in format of player.dat):
        - load items
        - load enchantments
        - load enchanted books
        - load tipped arrows + potions
        - load custom item names
    - Do above but for echest
    - save file in format {uuid}.dat in new folder called output
"""

from nbt import nbt
from nbt.nbt import TAG_Compound, NBTFile, TAG_List
from os import path, listdir
from loguru import logger as log
import json
from json import JSONDecodeError
from helpers import create_nbt_item

# Define paths
PLAYERS_PATH = path.join(path.dirname(__file__), "players")
WORLD_PATH = path.join(path.dirname(__file__), "smp_world")
TEMPLATE_PATH = path.join(path.dirname(__file__), 'TEMPLATE.dat')
OUTPUT_PATH = path.join(path.dirname(__file__), "output")

# Now let's make a hashmap {Name: UUID} for debug purposes
uuid_files: list[str] = [f for f in listdir(PLAYERS_PATH) if path.isfile(path.join(PLAYERS_PATH, f))]
uuid_dict: dict[str, str] = {}
for i in uuid_files:
    file_data = None
    with open(path.join(PLAYERS_PATH, i), 'r') as file:
        try:
            file_data = json.load(file)
            if file_data == None:
                raise(JSONDecodeError("File is empty", file.read(), 0))
            # set to lastKnownName or "null"
            uuid_dict[file_data["playerData"].get("lastKnownName", "null")] = i[:-5] # filename minus the .json ending = uuid
        except JSONDecodeError:
            log.warning(f"Filename {i} is empty!")
log.info(f"Loaded {len(uuid_dict.keys())} player UUIDs to process")

# Now we have their UUIDs let's load files
playerInventoryPaths = [path.join(WORLD_PATH, f"{k}.json") for k, _ in uuid_dict.items()]

# Iterate through each player to create a relevant NBT file
player_nbt_list: dict[str, NBTFile] = {}
for json_path in playerInventoryPaths:
    # 1. Load the JSON file as a Python Object
    try: 
        with open(json_path, 'r') as json_file:
            json_data = json.load(json_file) #? acc variable
    except JSONDecodeError:
        log.warning(f"File {json_path} is empty!")
        continue
    except FileNotFoundError:
        log.warning(f"File {json_path} not found. This player probably never joined the world this season.")
        continue
    # 2. Load Items in Inventory
    inv_items: list[TAG_Compound] = []
    inventory = json_data["SURVIVAL"].get("inventoryContents", None)
    if inventory == None or len(inventory.keys()) == 0: # If their inventory is empty
        log.warning(f"Player with file {json_path} has nothing in their inventory, skipping!")
    else:
        # convert it to a list to make it easier
        items = []
        for slot, item in inventory.items():
            item["slot"] = int(slot)
            items.append(item)
        # now iterate through items to create NBT equivatalnts
        inv_items = [create_nbt_item(item) for item in items]
        for item in inv_items:
            if not isinstance(item, TAG_Compound):
                log.error(f"ITEM IS NOT A TAG_COMPOUND AFTER MOVING INVENTORY. IT IS {type(item)}")
    # Now we're not done, you see, mvinv stores inventory items in 3 places - armorContents, inventoryContents and offHandItem
    # offHandItem has a slot of -106 for some reason
    offHandItem = json_data["SURVIVAL"].get("inventoryContents", None)
    if offHandItem == None: # If their inventory is empty
        log.warning(f"Player with file {json_path} has nothing in their offhand, skipping!")
    else:
        offHandItem["slot"] = -106
        inv_items.append(create_nbt_item(offHandItem))
        for item in inv_items:
            if not isinstance(item, TAG_Compound):
                log.error(f"ITEM IS NOT A TAG_COMPOUND AFTER OFF HAND ITEM. IT IS {type(item)}")
    # now armorContent
    armorContents = json_data["SURVIVAL"].get("armorContents", None)
    if armorContents == None or len(armorContents.keys()) == 0:
        log.warning(f"Player with file {json_path} has no armor, skipping!")
    else:
        # Convert to list for better iteration
        armor_list = []
        for slot, item in armorContents.items():
            item["slot"] = 100 + int(slot)
            armor_list.append(item)
        inv_items += [create_nbt_item(armor_piece) for armor_piece in armor_list]
        for item in inv_items:
            if not isinstance(item, TAG_Compound):
                log.error(f"ITEM IS NOT A TAG_COMPOUND AFTER ADDING ARMOR ITEMS. IT IS {type(item)}")
    # Now we finally have inv_items a list of tag compounds, though not in the proper form yet, it's useful

    #       Get e-chest items
    echest: list[TAG_Compound] = []
    echestContents = json_data["SURVIVAL"].get("enderChestContents", None)
    if echestContents == None or len(echestContents.keys()) == 0:
        log.warning(f"Player with file {json_path} has nothing in their e-chest, skipping!")
    else:
        # Convert to list for better iteration
        echest_list = []
        for slot, item in echestContents.items():
            item["slot"] = int(slot)
            echest_list.append(item)
    
        echest = [create_nbt_item(item) for item in echest_list]
        for item in echest:
            if not isinstance(item, TAG_Compound):
                log.error(f"ITEM IS NOT A TAG_COMPOUND IN ECHEST LIST!!! IT IS {type(item)}")
    
    # now let's review, we have 2 lists with tag compounds that have the inventory and echest contents. Well, what are we waiting for!
    # Let us now set the items!
    inventory_tag = TAG_List(type=TAG_Compound, name="Inventory")
    echest_tag = TAG_List(type=TAG_Compound, name="EnderItems")
    if len(inv_items) != 0:
        for item in inv_items:
            inventory_tag.tags.append(item)
    if len(echest) != 0:
        for item in echest:
            echest_tag.tags.append(item)

    # Now load the TEMPLATE NBT file and set these tags
    nbtfile = NBTFile(TEMPLATE_PATH, 'rb')
    nbtfile["Inventory"] = inventory_tag
    nbtfile["EnderItems"] = echest_tag

    # get playername
    playername = path.basename(json_path)[:-5]
    player_nbt_list[playername] = nbtfile
# Now we have a list of NBT Files for each player, all that is left is to save it!

for playerName, nbtFile in player_nbt_list.items():
    filename = path.join(OUTPUT_PATH, f"{uuid_dict[playerName]}.dat")
    nbtFile.write_file(filename)
