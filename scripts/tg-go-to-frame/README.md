# tg-go-to-frame
Sets the current frame in the Terragen project.

![tg_go_to_frame UI](images/tg_goto_frame_GUI.jpg)

### Requirements
Terragen 4 Professional v4.6.31 (or later) <br>
or Terragen 4 Creative (4.7.15 or later) <br>
or Terragen 4 Free (4.7.15 or later) <br>
https://planetside.co.uk/

### Installation
Install a version of Terragen 4 that includes the remote procedure call (RPC) feature on your computer.

### Usage
When run, the UI presents a single Entry widget called “<b>Go to frame</b>” which accepts integer values. The default value is the current frame, and this value can be retrieved at any time by pressing the <b>Escape key</b>.   The current frame and timeline will automatically update as characters are entered.  The <b>Up Arrow</b> and <b>Down Arrow</b> will advance the current frame forward or backwards respectively by one frame.  Scrolling the <b>middle mouse button</b> will advance the “Go to frame” value, but you must click another key, such as the <b>Enter</b> key, to set the current frame and update the timeline.

### Reference
terragen-rpc <br>
https://github.com/planetside-software/terragen-rpc

Online documentation for Terragen RPC <br>
https://planetside.co.uk/docs/terragen-rpc/

Blog posts on using Terragen RPC <br>
https://planetside.co.uk/blog/hello-rpc-part-1-scripting-for-terragen/ <br>
https://planetside.co.uk/blog/hello-rpc-part-2-error-handling/ <br>
https://planetside.co.uk/blog/script-it-yourself-kelvin-sunlight-colour-with-terragen-rpc/

