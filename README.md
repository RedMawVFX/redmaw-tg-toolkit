# redmaw-tg-toolkit
A collection of Python scripts to use with Terragen.

### Requirements
The toolkit requires Terragen 4, the Python programing language and a few dependency modules to be installed. <br>

Python <br>
https://www.python.org/

Tom’s Obvious, Minimal Language module <br>
https://pypi.org/project/toml/

Pillow <br>
https://pypi.org/project/Pillow/

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc


A version of Terragen that includes the remote procedure call (RPC) feature is also required. <br>

Terragen 4 Professional (v4.6.31 or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/

### Installation
The general recommendation for downloading and installing this toolkit is as follows:
<ul>
From the GitHub redmaw-tg-toolkit repository click the green "Code" button and select "Download ZIP" <br>
Save the ZIP archive to your computer.
Extract the folder structure and files from the ZIP archive.
</ul>

Alternatively, you can install the toolkit from the Git Bash shell as follows:
<ul>
Windows: py -m pip install redmaw-tg-toolkit <br>
MacOS: python3 -m pip install redmaw-tg-toolkit
</ul>

You'll also need to have Python installed, and the following dependancy modules. See the links above.<br>
<ul>
Tom’s Obvious, Minimal Language module. <br>
Pillow, a fork of the Python Imaging Library or PIL. <br>
terragen_rpc module. <br>
</ul>

In this repository you’ll find two Python scripts, a config file, and a scripts folder.
The script folder contains all the individual scripts and supporting data to run them.
The <b>tg_dashboard</b> scripts are identical except for their file extensions.  The file ending in .PY will open a command window when run, while the file ending in .PYW will not.  I recommend using the file with the .PYW extension when the script is run or called from an external file or a creative controller device like a Tourbox. <br>

### Customizing the tg-dashboard script
This script makes organizing and running your Python scripts for Terragen just one button click away.  The script will automatically generate a User Interface with button widgets and tabs according to the contents of its TOML formatted config file.

The config file is a text file which can be easily edited.  The config file stores the fullpath, name/label, and keyboard shortcut to the scripts you want to run.  By default the config file mirrors the layout of Terragen’s toolbar, but can be easily customized by commenting out lines of code or removing them completely in the config file.

### Usage

Run the tg_dashboard script.  The UI will present a button for each script in the config file.  Click the button to execute the script.

Many scripts written for use with Terragen will make use of its Remote Procedure Call (RPC) feature.  It’s best to have Terragen 4 running when you make use of this script.
