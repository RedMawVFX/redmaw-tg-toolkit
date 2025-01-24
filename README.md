# redmaw-tg-toolkit
A collection of Python scripts to use with Terragen.

# tg-dashboard
This script makes organizing and running your Python scripts for Terragen just one button click away.  The script will automatically generate a User Interface with button widgets and tabs according to the contents of its TOML formatted config file.

The config file is a text file which can be easily edited.  The config file stores the fullpath, name/label, and keyboard shortcut to the scripts you want to run.  By default the config file mirrors the layout of Terragen’s toolbar, but can be easily customized by commenting out lines of code or removing them completely in the config file.

### Requirements
This script only requires a Python installation, and the Tom’s Obvious, Minimal Language module; but to get the most out of it you’ll also need Terragen 4 and Terragen’s Remote Procedure Call module, terragen_rpc.

Python <br>
https://www.python.org/

Tom’s Obvious, Minimal Language module <br>
https://pypi.org/project/toml/

Terragen 4 Professional (v4.6.31 or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

### Installation
Install Python on your computer. <br>
Install Tom’s Obvious, Minimal Language module, via the pip install command. <br>
Install Terragen 4 on your computer. <br>
Install the terragen_rpc module, via the pip install command.

In this repository you’ll find two Python scripts and a config file.  You should edit the config file to so that the full file paths reflect your computer system and script installation.  <br>
The Python scripts are identical except for their file extensions.  The file ending in .PY will open a command window when run, while the file ending in .PYW will not.  I recommend using the file with the .PYW extension when the script is run or called from an external file or controller device like a Tourbox. <br>
You’ll also find several examples of the config file in the dev folder.

### Usage

Run the script.  The UI will present a button for each script in the config file.  Click the button to execute the script.

Many scripts written for use with Terragen will make use of its Remote Procedure Call (RPC) feature.  It’s best to have Terragen 4 running when you make use of this script.

### Reference
Tom's Obvious, Minimal Language file format <br>
https://en.wikipedia.org/wiki/TOML
