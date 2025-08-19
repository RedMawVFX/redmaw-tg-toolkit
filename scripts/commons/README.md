# commons
A collection of utility type scripts for the toolkit.

## node_network_layout.py

### Description
By default, when the remote procedure call (RPC) feature adds a node to the Terragen project, the node is positioned in the UI at the current center of the Node Network view.  This can result in nodes overlapping or stacking on top of one another.  

This module attempts to properly position the node passed to it, without overlapping or stacking on top of other nodes.  

### Requirements
Tkinter and the terragen_rpc_module.

### Installation
No installation required.  This script should remain in the commons folder of the redmaw-tg-toolkit, where it is called upon by other scripts in the toolkit.

### Usage
Use this module when you write a script that adds nodes to the Terragen project.  

At the start of your script, import the “set_gui_node_pos” function from the node_network_layout script as follows:<br>
from commons.node_network_layout import set_gui_node_pos

Within your script, the proper workflow is to add the new node, set its parameters as you wish, then call the “set_gui_node_pos” function and pass it the following information: the new node id, the type of node it is, and the node’s parent id.  All three of these arguments were needed to create the new node in the first place.

Example:<br>
import terragen_rpc<br>
from commons.node_network_layout import set_gui_node_pos<br>

project = terragen_rpc.root()<br>
new_camera = terragen_rpc.create_child(project, "camera") # adds a camera node to the project<br>
new_camera.set_param("gui_group", "Cameras") # makes the camera part of the Cameras group<br>
set_gui_node_pos(new_camera, "camera", project) # calls the function to position the node in the UI
