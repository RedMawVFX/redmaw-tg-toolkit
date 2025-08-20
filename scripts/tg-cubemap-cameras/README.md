# tg-cubemap-cameras

### Description
This script adds six camera nodes and a render node to the Terragen project in order to render cubemap images based on the source camera’s position.

### Requirements
The toolkit requires a version of Terragen 4 with the remote procedure call (RPC) feature. <br>
It also requires the Python programming language and the modules listed below. <br>

Terragen 4 Professional (v4.6.31 or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/ <br>

Python <br>
https://www.python.org/ <br>

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc <br>

### Installation
This script is included with the redmaw-tg-toolkit repository.  No additional installation steps are necessary.  See the Installation notes for the redmaw-tg-toolkit repository. <br>
This script shows up under the Cameras tab of the tg_dashboard.pyw script and has been assigned the keyboard shortcut “6”. <br>
There is no UI for this script. <br>

### Usage
Select the camera node in the Node Network window that you wish the cubemap cameras to be based on, then run the script.<br>

Six cubemap cameras will be created and inherit the position value of the selected camera. Each camera will face a different direction: forward, backward, left, right, up and down. <br>

A render node is added to the project with the forward facing cubemap camera assigned to it. <br>

For more information please see this blog post about setting up cubemaps: URL <br>

### Known Issues
By default, the RPC feature stacks newly created nodes on top of each other in the center of the Node Network window.  You can force the Terragen UI to refresh itself by clicking a button in the top Toolbar, like “Node Network”, and when refreshed, the new nodes will no longer be stacked on one another.

### Reference
Support Diaries: Cubemaps <br>
https://planetside.co.uk/blog/support-diaries-cubemaps/