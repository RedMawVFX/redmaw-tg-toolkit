# tg_transform_to_orgin

## A fully functional EXAMPLE script written in Python showing how to reposition a terrain feature at the origin of the project in Terragen 4 Professional.

Terragen 4 Professional (version 4.6.31) introduces a remote procedure call (RPC) feature which allows third party applications to communicate with the active version of Terragen.

## In this example you'll learn how to: 
* Create a GUI with labels and buttons
* Handle exceptions (errors)
* Add a Transform input shader node to the Terragen project and use its Translate parameters to offset the terrain.

## Usage:
![tg_transform_to_origin GUI](images/tg_transform_to_origin_GUI.JPG) <br />
1. Right click in the 3D Preview above a terrain feature, and select Copy Coordinates.
2. Select a node in the Node Network pane.  A Transform input shader node will be added after the selected node.
3. Click the Apply Offset button.
4. In the Node Network pane, connect the output from the Transform input shader to the Main input of a downstream node.

## Known issues:
Future releases of terragen_rpc will include methods to automatically connect the output of a node to another node, effectively eliminating Step 4 above.

## Reference:
terragen-rpc <br />
https://github.com/planetside-software/terragen-rpc

Online documentation for Terragen RPC <br />
https://planetside.co.uk/docs/terragen-rpc/

Blog posts on using Terragen RPC <br />
https://planetside.co.uk/blog/hello-rpc-part-1-scripting-for-terragen/ <br />
https://planetside.co.uk/blog/hello-rpc-part-2-error-handling/

Terragen 4 <br />
https://planetside.co.uk/