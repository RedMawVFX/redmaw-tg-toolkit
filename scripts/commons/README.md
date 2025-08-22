# commons
A collection of utility type scripts for the toolkit.

## node_network_layout.py

### Description
By default, when the remote procedure call (RPC) feature adds a node to the Terragen project, the node is positioned in the UI at the current center of the Node Network view.  This can result in nodes overlapping or stacking on top of one another.  

This module attempts to properly position the node passed to it, without overlapping or stacking on top of other nodes.
 

### Requirements
Python <br>
https://www.python.org/

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc


### Installation
No installation required.  This script should remain in the commons folder of the redmaw-tg-toolkit, where it is called upon by other scripts in the toolkit.

### Usage
Use this module when you write a script that adds nodes to the Terragen project.<br>

At the start of your script, import the “auto_position_node” function from the node_network_layout script as follows:<br>
from commons.node_network_layout import auto_position_node<br>

Within your script, the proper workflow is to add the new node, set its parameters as you wish, then call the “auto_position_node” function and pass it the following information: the new node id, and the type of node it is.<br>

Example:<br>
import terragen_rpc as tg<br>
from commons.node_network_layout import auto_position_node<br>

project = tg.root()<br>
new_camera = tg.create_child(project, "camera") # adds a camera node to the project <br>
new_camera.set_param("gui_group", "Cameras") # makes the camera part of the Cameras group<br>
auto_position_node(new_camera, "camera") # calls the function to position the node in the UI<br>
