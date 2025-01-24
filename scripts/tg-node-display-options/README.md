# tg-node-display-options
Sets the preview options for all nodes of a selected class in the current Terragen project.

Some class types, like camera, have multiple preview parameters. Checkbuttons allow individual control over each parameter.

Only a node’s display options in the 3D Preview are affected by this script, its render state remains unaffected.

The script's UI is colour coded to match the corresponding node colour in the Terragen UI.

![tg_node_display_options GUI](images/tg_node_display_options_gui.jpg)

### Requirements <br>
Terragen 4 Professional (4.6.31 or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/ <br>

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc <br>

### Installation <br>
Install Terragen 4 on your computer. <br>
Install the terragen_rpc module, via the pip install command. <br>
Download this repository via “git clone [repository url]” <br>
Terragen 4 should be running when you run this script. <br>

In this repository you’ll find two Python scripts, which are identical except for their file extensions.  The file ending in .PY will open a command window when run, while the file ending in .PYW will not.  I recommend using the file with the .PYW extension when the script is run or called from an external file or controller device like a Tourbox.

### Usage
Click a radio button to select the type of node (class) you want to affect. For example, checking the “TGO reader” button will allow the preview options of all TGO formatted objects in the project to be affected.  Most types of nodes have only one preview option, but a few have more than one.  The Camera class includes three preview options: Body, Frustum, and Path. For those options to be affected, make sure their check buttons have been checked.  

To turn the preview option on for the selected type of node, check “<b>On</b>” and click the “<b>Apply</b>” button.  To turn the preview display off, check “<b>Off</b>” and click the “<b>Apply</b>” button.  You can toggle between the on and off states for the node’s preview option by checking the “<b>Toggle</b>” button and clicking the “<b>Apply</b>” button.

### Known Issues
The script doesn’t keep track of the display option’s original value.

### Reference
terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

Online documentation for Terragen RPC <br>
https://planetside.co.uk/docs/terragen-rpc/

Blog posts on using Terragen RPC <br>
https://planetside.co.uk/blog/hello-rpc-part-1-scripting-for-terragen/ <br>
https://planetside.co.uk/blog/hello-rpc-part-2-error-handling/ <br>
https://planetside.co.uk/blog/script-it-yourself-kelvin-sunlight-colour-with-terragen-rpc/


