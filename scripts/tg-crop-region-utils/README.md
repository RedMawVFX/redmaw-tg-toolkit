# tg-crop-region-utils
A collection of render node utilities.

### Description
The <b>tg_toggle_all_crop_regions.pyw</b> script toggles the “Do crop region” checkbox for all render nodes in the project, effectively enabling or disabling the crop region.

### Requirements
The toolkit requires a version of Terragen 4 with the remote procedure call (RPC) feature. <br>
It also requires the Python programming language and the modules listed below. <br>

Terragen 4 Professional (v4.6.31 or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/ <br>

Python <br>
https://www.python.org/ <br>

Tom’s Obvious, Minimal Language module <br>
https://pypi.org/project/toml/ <br>

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc <br>

### Installation
This script is included with the redmaw-tg-toolkit repository.  No additional installation steps are necessary.  See the Installation notes for the redmaw-tg-toolkit repository.

### Usage
This script shows up under the Renderers tab of the tg_dashboard.pyw script and has been assigned the keyboard shortcut “l”.  When the tg_dashboard has “focus” pressing the “l” key will toggle the “Do crop region” checkbox for all renderers in the project.
