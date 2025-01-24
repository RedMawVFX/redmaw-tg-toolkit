# tg-time-of-day
This script modifies the heading and elevation of a selected Sunlight node based
the time of day and on lat-long coordinates.  

The script was originally designed as an example and introduction to coding a
Python script and using Terragen's RPC module, terrgen_rpc. 

The version in this repository has minor updates to its UI, compared to the version
of the script in the Wiki tutorial.  It is the same functionally.

### Requirements
Terragen 4 Professional (v4.6.31 or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

Python Sun Position for Solar Energy and Research module by John Clark Craig<br>
(the module has been included in this repository) <br>
https://levelup.gitconnected.com/python-sun-position-for-solar-energy-and-research-7a4ead801777

### Installation <br>
Install Terragen 4 on your computer. <br>
Install the terragen_rpc module, via the pip install command. <br>
Download this repository via “git clone [repository url]” <br>
Terragen 4 should be running when you run this script.

In this repository you’ll find two Python scripts, which are identical except for their file extensions.  The file ending in .PY will open a command window when run, while the file ending in .PYW will not.  I recommend using the file with the .PYW extension when the script is run or called from an external file or controller device like a Tourbox.

### Usage
Select a Sunlight node from the listbox. <br>
Enter the time of day and location information you want. <br>
Click the "Apply to Sun" button. <br>

### Reference
terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

Online documentation for Terragen RPC <br>
https://planetside.co.uk/docs/terragen-rpc/

Blog posts on using Terragen RPC <br>
https://planetside.co.uk/blog/hello-rpc-part-1-scripting-for-terragen/ <br>
https://planetside.co.uk/blog/hello-rpc-part-2-error-handling/ <br>
https://planetside.co.uk/blog/script-it-yourself-kelvin-sunlight-colour-with-terragen-rpc/

