# blender-synty-characters-to-godot
Cleaning up and prepare Synty assets for the Godot engine. Transforming the fbx files into gLTF, ready to use in Godot.

## Installation
Zip the source directory and add it as Addon in Blender by Edit -> Preferences -> Add-ons -> Install. In the Add-ons list there should be an entry names "Import-Export: Synty to Godot", enable it.

## Usage
Open the properties shelf by pressing the N-Key. There is a new entry named Misc -> Snyty to Godot:  

### Settings
* Custom normals: If the file was transformed from FBX ASCII to FBX Binary with Autodesk FBX Converter you must disable the option.

### Batch
For converting multiple FBX files at one use this options.  
* Source dir: The source directory where all fbx files are located
* Target dir: Target directory to save the gLTF files to
* Batch charactes in directory: Starts the batch process

### Single
For converting a single FBX file. The order of the buttons reproduces the steps used in the batch process.  
* Clean scene: Cleans the scene for a fresh import
* Import fbx: Import a single fbx file
* Cleanup current character: Cleans the Pose and Armature
* Export gLTF: Exports the file ready to use for Godot

## Tutorial
A tutorial for the a further workflow to add Mixamo animations to the character can be found here on my website https://flemo-interactive.com/synty-characters-with-mixamo-animations/