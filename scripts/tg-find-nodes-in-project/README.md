# tg-find-nodes-in-project
Finds nodes in the active Terragen project.  Once nodes have been found they can be added to or removed from the currently selected nodes in the project.

The UI includes a search feature, the ability to resample the current contents in the project, and various ways to select nodes from the list.

![tg_find_nodes_in_project GUI](images/tg_find_nodes_in_project_gui.jpg)

### Requirements
Terragen 4 Professional v4.6.31 (or later) <br>
or Terragen 4 Creative v4.7.15 (or later) <br>
or Terragen 4 Free 4.7.15 (or later) <br>
https://planetside.co.uk/

terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

### Installation
Install Terragen 4 on your computer. <br>
Install the terragen_rpc module, via the pip install command. <br>
Download this repository via “git clone [repository url]” <br>
Terragen 4 should be running when you run this script. <br>

### Usage
When the script is executed the UI will present a list of all the nodes at the root level of the project. You can refine the items displayed in the list by entering text in the “<b>Search pattern</b>” field, or click on the “<b>Clear</b>” button to clear the search pattern and display all the nodes.  The “<b>Refresh</b>” button updates the list with the current nodes in the project.

Clicking the “<b>All</b>” button will select all the nodes displayed in the list, while clicking “<b>None</b>” will deselect all the nodes in the list.  Clicking “<b>Invert</b>” will toggle the selection state of the nodes in the list.

Clicking the “<b>Add to selection</b>” button will add the selected nodes to the currently selected nodes in the project.  Clicking the “<b>Remove from selection</b>” button deselects the nodes from the currently selected nodes in the project.

### Known Issues
The script does not recursively look for nodes within the internal node network of another node.  It only retrieves nodes at the root level of the project.

### Reference
terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

Online documentation for Terragen RPC <br>
https://planetside.co.uk/docs/terragen-rpc/

Blog posts on using Terragen RPC <br>
https://planetside.co.uk/blog/hello-rpc-part-1-scripting-for-terragen/ <br>
https://planetside.co.uk/blog/hello-rpc-part-2-error-handling/ <br>
https://planetside.co.uk/blog/script-it-yourself-kelvin-sunlight-colour-with-terragen-rpc/
