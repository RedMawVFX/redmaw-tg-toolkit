# redmaw-tg-toolkit
A collection of Python scripts to use with Terragen, including a handy configurable dashboard script from which to launch them.

![tg_dashboard gui](/images/tg_dashboard_gui.jpg)

### Requirements
The toolkit requires a version of Terragen 4 with the remote procedure call (RPC) feature. <br>
It also requires the Python programing language and the modules listed below. <br>

Terragen 4 Professional (v4.6.31 or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/

Python <br>
https://www.python.org/

Tom’s Obvious, Minimal Language module <br>
https://pypi.org/project/toml/

Pillow <br>
https://pypi.org/project/Pillow/

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc


### Installation
The general recommendation for downloading and installing this toolkit is as follows:
<ul>
From the GitHub redmaw-tg-toolkit repository click the green "Code" button and select "Download ZIP" <br>
Save the ZIP archive to your computer. <br>
Extract the folder structure and files from the ZIP archive.
</ul>

You can install the dependency modules via the Git Bash shell as follows:
<ul>
Windows: <ul>py -m pip install toml <br> py -m pip install Pillow <br> py -m pip install terragen-rpc<br></ul><br>
MacOS:<ul> python3 -m pip install toml<br> python3 -m pip install Pillow <br> python3 -m pip install terragen-rpc<br></ul>
</ul>

### Usage

In this repository you’ll find two Python scripts, a config file, a scripts folder and an images folder. <br><br>
The script folder contains all the individual scripts and supporting data to run them. <br><br>
The <b>tg_dashboard</b> scripts are identical except for their file extensions.  The file ending in .PY will open a command window when run, while the file ending in .PYW will not.  I recommend using the file with the .PYW extension when the script is run or called from an external file or a creative controller device like a Tourbox. <br>

Run the tg_dashboard script.  The UI will present a button for each script in the config file.  Click the button to execute the script.

Many scripts written for use with Terragen will make use of its Remote Procedure Call (RPC) feature.  It’s best to have Terragen 4 running when you make use of the scripts.

### Customizing the tg-dashboard script
The tg_dashboard script makes organizing and running your Python scripts for Terragen just one button click away.  The script will automatically generate a User Interface with button widgets and tabs according to the contents of its TOML formatted config file.

The config file is a text file which can be easily edited.  The config file stores the fullpath, name/label, and keyboard shortcut to the scripts you want to run.  By default the config file mirrors the layout of Terragen’s toolbar, but can be easily customized by commenting out lines of code or removing them completely in the config file.

![tg_dashboard UI without empty tabs](/images/tg_dashboard_no_empty_tabs.jpg) <br> <br>
![tg_dashboard UI one tab](/images/tg_dashboard_one_tab.jpg)
