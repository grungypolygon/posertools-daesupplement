# Collada Import Plus

Supplement python script to address some shortcomings of Poser's Collada import.

## Features

* Restore object hierarchy on import. 
* Import objects without geometry as grouping objects.
* Adjust the imported objects' axis if different than Poser's Y-Up axis.
* Adjust the imported objects' scale. 

Features TODO:

* Support matrix notation of objects' position, rotation and scale in COLLADA file. 
* Import objects' animated positions, rotations and scalings.   

This script has been created for personal use for using [Blender](http://www.blender.org/)
as prop creation tool. So I don't know how well it works with COLLADA files created by other
tools.

For now, if you export a COLLADA file in Blender, make sure you select the "TransRotLoc"
transformation type or "Both".

## Requirements

PoserPro 2014 SR4 (10.0.4.27796) or later

## Installation

There are two ways to use this script.

### Python Script Button

* Open the Python Scripts panel in Poser via the Window->Python Scripts Menu.
* Click an empty ('...') button.
* Select the "COLLADA ImportPuls.py" file from the GrungyPolygon folder.

The button will now start the script when clicked. 

This one is more of a temporary way. Unless you edit Poser's "mainButtons.py" script,
the button will be blank again on the next program start.

### Poser Scripts Menu

* Copy the GrungyPolygon folder to Poser's "Runtime\Python\poserScripts\ScriptsMenu" folder.
* Restart Poser

The script will now show up as "COLLADA ImportPlus" under the "GrungyPolygon" submenu in 
Poser's "Scripts" menu. 

Ignore the "collada" menu entry. It's a needed module file and I haven't yet found a way to 
prevent Poser from showing it in the menu.

Note: If you have both versions of Poser installed (64bit and 32bit) you'll have to place 
the folder in each version's runtime folder.

## Usage

When the script is started, you'll be prompted for a couple of options. Each option can
be deactivated if not needed.

### Adjust axis

Poser uses a Y-Up axis system. Meaning that objects moving up travel along the positive
Y-Axis. Other 3D software packages, such as Blender may use different conventions such
as Z-Up. Right now, only Z-Up conversion is supported.
  
### Adjust scale
  
One of Poser's native units equals 8.6 feet or 262.128 cm. If the COLLADA file stores
positions for example in meters, Poser does not convert this.
 
On import, set the value to how many Poser units one unit in the Collada file corresponds to.
e.g. Blender uses meter as unit so set the value to 2.62128

### Adjust hierarchy

COLLADA files store a scene's object hierarchy. Poser seems to drop that information on import.
This option will recreate the parent-child relationships between objects.
 
As a side effect COLLADA objects without geometry, such as Blender "Empty" objects, will be
imported as grouping objects.

