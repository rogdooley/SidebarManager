# SidebarManager

This is a Python program for managing MacOS Sidebar favorites. This was inspired by [finder-sidebar-editor](https://github.com/Ajordat/finder-sidebar-editor/tree/master) and [mysides](https://github.com/mosen/mysides).

One can create a file that contains the layout of the desired Finder Favorites. The file format for import is based on the format from `mysides list`. Each line consists of a label, a space, a ->, and then a `file url` (`Applications -> file:///Applications/`). 

*Note:* Currently will not import `nwnode` uris like the one for AirDrop (`domain-AirDrop -> nwnode://domain-AirDrop`). 

I would strongly recommend backing up one's Finder Favorites prior to running this. 

### Requirements:

[PyObjC](https://pypi.org/project/pyobjc/)
```
pip install pyobjc
```

### Example Usage:

#### Export current Finder Favortites to a file:
```shell
python3 SidebarManager.py -e -f favorites.txt
```

#### Import and replace all Finder Favorites from a file:
```shell
python3 SidebarManager.py -i -f new-favorites.txt
```

#### Add a Favorite After an Existing One:
```shell
python3 SidebarManager.py -A "My Folder" "file:///Users/fred/MyFolder/" "Downloads"
```

#### Add a Favorite Without a Specific Position:
```shell
python3 SidebarManager.py -a "New Folder" "file:///Users/fred/NewFolder/"
```

#### Remove a Favorite:
```shell
python3 SidebarManager.py -r "My Folder"
```
