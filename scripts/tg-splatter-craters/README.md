# tg-splatter-craters
Randomly splatters instances of the Crater shader throughout the active Terragen project.

Parameter values of each Crater shader are randomly chosen based on minimum and maximum values in the UI.

![tg_splatter_craters UI](images/tg_splatter_craters_gui.jpg)

### Requirements
Terragen 4 Professional (v4.6.31 or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

### Installation
Install Terragen 4 on your computer. <br>
Install the terragen_rpc module, via the pip install command. <br>
Download this repository via “git clone [repository url]” <br>
Terragen 4 should be running when you run this script. <br>

### Usage
When the Tooltip checkbutton is checked, hovering over a parameter will display a help window for that parameter.

![tg_splatter_craters Tooltips](images/tg_splatter_craters_tooltips.jpg)

To add Crater shaders to the active Terragen project enter the quantity you want in the <b>Number of craters</b> field.  The shaders can be grouped together.

Each crater is randomly positioned around the <b>Area centre x,y,z</b> coordinates and within the <b>Area volume x,y,z</b>.

Parameters for each Crater shader are randomly generated between the <b>Minimum</b> and <b>Maximum</b> value. Some parameter values can be based on the crater’s diameter by checking the <b>or % of diameter</b> checkbutton. Furthermore, those values can be randomized by checking the <b>+/- Offset</b> checkbutton.

Certain types of displacement shaders can be assigned to the Crater shader’s <b>Rim shader</b> parameter.  Select a shader class from the list and check the checkbutton.  The displacement shader will be assigned to all crater shaders generated when the Apply button is clicked.

If desired the Crater shaders can be inserted into the node network workflow. The <b>Output > Main input</b> option will attempt to connect the added crater shaders in between the first Compute terrain node in the project and whatever shader was assigned to its Main input when the Apply button is clicked.  The <b>Merge shader</b> option will attempt the same via a Merge shader node.  When the <b>Don’t</b> option is chosen, no attempt is made to connect the Crater shaders to the existing node network.

When checked, the <b>Append fractal warp shader?</b> checkbutton will add a Fractal Warp shader node after all the Craters.  

Click the <b>Apply</b> button to add the Crater shaders and other nodes to the project.

The menu includes a set of <b>Presets</b>. These values are meant to be artistically fun and are not scientifically accurate.  

![tg_splatter_craters Presets](images/tg_splatter_craters_presets.jpg)

### Reference
Planetside Software Forum post (with more information about this script) <br>
https://planetside.co.uk/forums/index.php/topic,30977.0.html <br>

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

Online documentation for Terragen RPC <br>
https://planetside.co.uk/docs/terragen-rpc/

Blog posts on using Terragen RPC <br>
https://planetside.co.uk/blog/hello-rpc-part-1-scripting-for-terragen/ <br>
https://planetside.co.uk/blog/hello-rpc-part-2-error-handling/ <br>
https://planetside.co.uk/blog/script-it-yourself-kelvin-sunlight-colour-with-terragen-rpc/



