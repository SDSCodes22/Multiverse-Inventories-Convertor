from nbt.nbt import TAG_Compound, TAG_Byte, TAG_String, TAG_List, TAG_Short
from loguru import logger as log

def create_nbt_item(item):
    """This only handles enchantments and item names bcuz idk how to load anything else from mvinv
    Must have an extra "slot" attribute. This is all according to this excellent page on the MC Wiki: 
    https://minecraft.fandom.com/wiki/Player.dat_format#Item_structure

    Args:
        item (dict): mvinv item data
    """
    root_tag = TAG_Compound()
    # count
    root_tag.tags.append(TAG_Byte(int(item.get("amount", 1)), name="count"))
    # Slot
    root_tag.tags.append(TAG_Byte(int(item.get("slot", 1)), name="Slot"))
    # id
    mc_id = f"minecraft:{str(item.get("type", "AIR")).lower()}"
    root_tag.tags.append(TAG_String(mc_id, name="id"))

    # Check if we need extra data like enchants and custom names
    metaData = item.get("meta", None)
    if metaData == None:
        # No need for enchantments or anything else! We're done
        log.debug(f"Root tag is of type {type(root_tag)}. Also no metadata")
        return root_tag
    # Now time for components tag that contains enchantments and other data
    components_tag = TAG_Compound(name="components")

    #       Enchantments
    enchants = metaData.get("enchants", None)
    if enchants != None:
        enchantment_list_tag = TAG_Compound(name="minecraft:enchantments")
        levels_tag = TAG_Compound(name="levels")
        # Convert to a list so it'll be easier to traverse and append to enchantment_list_tag
        enchantment_list = \
            [
                {"enchantName": k, "level": v} for k, v in enchants.items()
            ]
        for enchant in enchantment_list:
            levels_tag.tags.append(TAG_Byte(enchant["level"], name=enchant["enchantName"]))
        enchantment_list_tag.tags.append(levels_tag)
        components_tag.tags.append(enchantment_list_tag)
    #       Custom name
    customName = metaData.get("display-name", None)
    if customName != None:
        components_tag.tags.append(TAG_String(str(customName), name="minecraft:custom_name"))
    
    #       Potion Effects
    potionEffects = metaData.get("potion-type", None)
    if potionEffects != None:
        potion_contents_tag = TAG_Compound(name="minecraft:potion_contents")
        potion_tag = TAG_String(potionEffects, name="potion")
        potion_contents_tag.tags.append(potion_tag)
        components_tag.tags.append(potion_contents_tag)
    
    #       Enchanted Books
    storedEnchants = metaData.get("stored-enchants", None) # returns dict in form {str(<enchant_id>): int(<level>)}
    if storedEnchants != None:
        stored_enchantments_tag = TAG_Compound(name="minecraft:stored_enchantments")
        levels_tag = TAG_Compound(name="levels")
        for enchant_name, level in storedEnchants.items():
            levels_tag.tags.append(TAG_Byte(value=int(level), name=str(enchant_name)))
        stored_enchantments_tag.tags.append(levels_tag)
        components_tag.tags.append(stored_enchantments_tag)
    # We're done with components tag
    root_tag.tags.append(components_tag)
    log.debug(f"Root tag is of type {type(root_tag)}")
    return root_tag