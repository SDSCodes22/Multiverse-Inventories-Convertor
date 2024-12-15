# Multiverse-Inventories Exporter
Are you switching from Multiverse to Vanilla, Bungeecord or others, but want to keep your players' inventories? This simple python script allows you to export your players' inventories to minecraft NBT `.dat` files so that Bukkit and default Minecraft can understand.

# Installation Guide
1. Ensure you have [Python](https://python.org) installed
2. Clone this repository to your local machine
3. Create a new virtual environment using: (Unix)
```
cd <cloned repository directory>
python3 -m venv venv
source venv/bin/activate
``` 
4. Install dependencies from `requirements.txt`:
```
pip3 install -r requirements.txt
```

# Usage Guide
## For importing a specific world
*It may look complicated, but it is not. Just follow the instructions carefully*
1. Go to your server host and locate the directory: `/plugins/Multiverse-Inventories/worlds/`
2. Find the primary world that contains the players' inventories e.g. `smp_world`
3. Download the folder to your local device. It should be filled with `.json` files with playernames e.g. `player1.json`
4. Place this folder in the same directory as `main.py`
5. Rename this folder to `smp_world`
6. On your server host, find the folder `/plugins/Multiverse-Inventories/players` and download the folders. It should contain files with names such as the following: 
`021e8ff9-fc52-3a20-a271-1d72a73dda5a.json`
7. Place this `players` folder in the same directory as `main.py`
8. Create a new, empty folder and call it `output`
9. Your project structure should look a bit like this: 
```
.
├── README.md
├── TEMPLATE.dat
├── .gitignore
├── helpers.py
├── main.py
├── requirements.txt
├── output
│   ├── (this should be empty)
├── players
│   ├── 00000000-0000-0000-0009-01f72b721d2a.json
│   └── ...
└── smp_world
    ├── playername.json
    └── ...
```
10. Now, run the program using `python3 main.py`

11. You will see that the `output` folder now has files. Rename this folder to `playerdata`.
12. Go back to your server host and find the world folder that is set as `level-name` in your `server.properties`
13. The folder should have a sub-folder called `playerdata` with .dat files.
14. Upload the output folder which you renamed `playerdata` here, to replace the existing playerdata folder.

## For importing Groups
**NOTE: THIS IS UNTESTED CURRENTLY**

Use the above steps, but for steps 1 and 2, instead:
1. Go to `/plugins/Multiverse-Inventories/groups`
2. Find the folder of the world group that you want to export.

# Limitations
- Complicated to use, especially for non-developers
- Only Handles the following NBT Data: Enchantments, Custom Names, Potions, Enchanted Books
- Does not handle the following NBT Data: armor trim data, written book content, aquatic mob content (e.g. axolotl colour) + more.
- Not user-intuitive
- Cannot import nbt data to multiverse-inventories
- No direct plugin integration 

# Contributing
I am not the most skilled developer and this implementation isn't the best. Please feel free to contribute and improve this project. I am considering making this a web application in the future for ease of use. Thanks.