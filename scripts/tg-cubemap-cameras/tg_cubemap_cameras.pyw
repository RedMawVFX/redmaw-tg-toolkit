''' tg_cubemap_cameras.py
    Inserts six camera nodes into project based on the selected camera node's position,
    and a render node for them to use.
'''

import sys
import os
import re
from tkinter import messagebox
import terragen_rpc as tg

# Add the parent directory (scripts) to sys.path in order to import from commons
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from commons.node_network_layout import auto_position_node

class CameraConfig:
    def __init__(self, key, source_position, cubemap_group, rotation_value):
        self.key = key
        self.position = source_position
        self.rotation = rotation_value
        self.cubemap_group = cubemap_group
        self.use_horizontal_fov = "1"
        self.horizontal_fov = "90"
        self.name = key

    def apply_to(self, camera):
        safe_rpc_call(camera.set_param, "gui_group", self.cubemap_group.name())
        safe_rpc_call(camera.set_param, "position", self.position)
        safe_rpc_call(camera.set_param, "rotation", " ".join(str(x) for x in self.rotation))
        safe_rpc_call(camera.set_param, "use_horizontal_fov", self.use_horizontal_fov)
        safe_rpc_call(camera.set_param, "horizontal_fov", self.horizontal_fov)
        safe_rpc_call(camera.set_param, "name", self.name)

class RenderConfig:
    def __init__(self, camera):
        self.camera = camera

    def apply_to(self, render_node, camera):
        safe_rpc_call(render_node.set_param, "name", "Render Cubemaps")
        safe_rpc_call(render_node.set_param, "camera", camera.name())
        safe_rpc_call(render_node.set_param, "image_width", "800")
        safe_rpc_call(render_node.set_param, "image_height", "800")
        safe_rpc_call(render_node.set_param, "lock_aspect_ratio", "1")
        output_image_file = self.determine_output_image(render_node)
        safe_rpc_call(render_node.set_param, "output_image_filename", output_image_file)
        safe_rpc_call(render_node.set_param, "motion_blur", "0")
        safe_rpc_call(render_node.set_param, "gui_group", "Renderers")

    def determine_output_image(self, renderer):
        ''' sets the render node's output image filename to 
            include the camera name assigned to it.

        Args:
            renderer <obj>: render node id
        
        Returns:
            new_filename (str): filename
        '''
        existing_filename = safe_rpc_call(renderer.get_param, "output_image_filename")
        camera = "${CAMERA}_"
        # Replace ".%04d" with "_${CAMERA}_.%04d"
        new_filename = re.sub(r"\.%04d", f"_{camera}.%04d", existing_filename)
        return new_filename
    
    def set_gui_group_param(self, render_node, group_name="Renderers"):
        safe_rpc_call(render_node.set_param, "gui_group", group_name)

class NotesConfig:
    def __init__(self, node):
        self.node = node

    def apply_to(self):
        safe_rpc_call(self.node.set_param, "name", "Cubemap Notes")
        safe_rpc_call(
            self.node.set_param,
            "gui_note_text",
            (
                "Render GI cache file from Spherical camera first.\n"
                "Then assign cache file to the Cubemap renderer.\n"
                "Be sure to REFRESH ui in order to see updated node placement."
            )
        )

cubemap_cameras_dict = {
    "Cube_Face_Forward": (0, 0, 0),
    "Cube_Face_Back": (0, 180, 0),
    "Cube_Face_Left": (0, 270, 0),
    "Cube_Face_Right": (0, 90, 0),
    "Cube_Face_Up": (90, 0, 0),
    "Cube_Face_Down": (-90, 0, 0)
}

def message_info(title, message):
    messagebox.showinfo(title, message)

def message_retry(title, message):
    return messagebox.askretrycancel(title, message)

def safe_rpc_call(fn, *args, **kwargs):
    ''' all terragen_rpc calls are routed thru this
        function, encased in a try except block in
        order to capture communication breakdowns.
    '''
    try:
        return fn(*args, **kwargs)
    except ConnectionError as e:
        message_info("RPC Message", "Terragen RPC Connection error: " + str(e))
    except TimeoutError as e:
        message_info("RPC Message", "Terragen RPC timeout error: " + str(e))
    except tg.ReplyError as e:
        message_info("RPC Message", "Terragen RPC server reply error: " + str(e))
    except tg.ApiError:
        message_info("RPC Message", "Terragen RPC API error")
        raise

def camera_handler(cubemap_group, source_pos, context):
    ''' Handler to create new cubemap cameras, set their params,
     and position them in node network.

    Args:
        cubemap_group <obj>: group id
        source_pos (str): source camera's position
    '''

    for key, value in cubemap_cameras_dict.items():
        print(f"Creating {key} camera...")
        config = CameraConfig(key, source_pos, cubemap_group, value)
        camera = create_child(class_name="camera", context=context)
        config.apply_to(camera)
        auto_position_node(node=camera, class_name="camera", context=context)
        if key == "Cube_Face_Forward":
            render_node_handler(camera, context)

def render_node_handler(camera, context):
    '''
    Inserts a render node into the project for the cubemap cameras to access.

    Args:
        camera <obj>: camera node id
        cubemap_group <obj>: group node id
        context <obj>: node id or none
    Returns:
        renderer <obj>: render node id
    '''

    print("Creating render node...")
    render_config = RenderConfig(camera)
    render_node = create_child(class_name="render", context=context)
    render_config.apply_to(render_node, camera)
    auto_position_node(render_node, class_name="render", context=context)
    # ensures the render node gets captured by a newly created group
    render_config.set_gui_group_param(render_node, "Renderers")

def cubemap_notes_handler(class_name: str, context):
    ''' Inserts a note into the project reminding user to refresh the UI
        in order to see the changes.
    '''
    cubemap_note = get_node_in_class_by_name(class_name, "Cubemap Notes", context=context)
    if cubemap_note:
        print ("Cubemap note already exists!")
        return # already has a note
    new_note = create_child(class_name=class_name, context=context)
    note_config = NotesConfig(new_note)
    note_config.apply_to()
    auto_position_node(node=new_note, class_name=class_name, context=context)

def cubemap_group_handler(context, use_cubemap_group=False):
    ''' choose which group to use for the cubemaps, the
        default Cameras group or a custom group named Cubemaps
        Assign False to use the default Cameras group 
        or True to use Cubemaps group
    '''

    if use_cubemap_group:
        cubemap_group = create_child(class_name="group", context=context)
        safe_rpc_call(cubemap_group.set_param, "name", "Cube Face Cameras")
        auto_position_node(node=cubemap_group, class_name="group", context=context)
    else:
        cubemap_group = get_node_in_class_by_name(
            class_name="group",
            node_name="Cameras",
            context=context
        )

    return cubemap_group

def get_node_in_class_by_name(class_name: str, node_name, context):
    ''' return the node that matches the given class_name and node name

    Args:
        class_name (str): class name, i.e. "group"
        node_name (str): node's name, i.e. "Renderers"
        context <obj>: node id, i.e. root level node
    '''
    nodes_in_class = safe_rpc_call(context.children_filtered_by_class, class_name)
    if nodes_in_class:
        for node in nodes_in_class:
            if node.name() == node_name:
                return node

def create_child(class_name: str, context):
    '''
    Wrapper to create a new node at the root level of the project or internal node network

    Args:
        class_name (str): class name of node
        context <obj>: node id i.e. root of project or node id for internal node network
    
    Returns:
        new_node <obj>: node id
    '''
    new_node = safe_rpc_call(tg.create_child, context, class_name)
    return new_node

def get_user_selection():
    return safe_rpc_call(tg.current_selection)

def determine_context(selected_nodes):
    '''context is determined by getting the
       parent of one node. It will either be 
       the project root node or the parent'''
    parent = safe_rpc_call(selected_nodes[0].parent)
    return parent

def get_nodes_in_context(context, class_name: str):
    ''' Wrapper for children filtered by class
    Args:
        context <obj>: root node or parent node
        class_name "str": class type i.e. "render"

    Returns:
        [list]: of objects
    '''
    return safe_rpc_call(context.children_filtered_by_class, class_name)

def selection_handler_single_node_in_class(class_name: str):
    ''' Handles user selection, ensuring the return of a single
        node matching the specified class type.

    Args:
        class_name (str): type of node, i.e. "render"
    
    Returns:
        common_nodes[0] <obj>: single node id matching class type
        context <obj>: node id
    '''
    while True:
        # get user selection
        while True:
            selected_nodes = get_user_selection()
            if selected_nodes:
                break
            else:
                retry = message_retry("tg_cubemap_cameras.pyw", "No nodes selected. Try again?")
                if not retry:
                    print("User cancelled selection.")
                    sys.exit()

        # determine context,  i.e. root level or internal node network
        context = determine_context(selected_nodes) # returns an <obj>

        # get nodes in class type within context
        cameras = get_nodes_in_context(context, class_name)

        # indentify selected nodes matching nodes in class type within context
        common_nodes = []
        for node in selected_nodes:
            if node in cameras:
                common_nodes.append(node)

        # this use case; only one node should be selected
        if len(common_nodes) != 1:
            retry = message_retry(
                "tg_cubemap_cameras.pyw",
                f"Invalid node(s) selected!\nPlease select only one {class_name} node\nand press Retry."
            )

            if retry:
                continue
            else:
                print("User cancelled after multiple nodes found.")
                sys.exit()

        return common_nodes[0], context

# main
# get selected nodes
source_cam, context = selection_handler_single_node_in_class(class_name="camera")

# get selected camera's position
source_pos = safe_rpc_call(source_cam.get_param, "position")

# choose group for cubemap cameras
cubemap_group = cubemap_group_handler(context=context)

# insert cubemap cameras into project
camera_handler(cubemap_group, source_pos, context=context)

# insert cubemap notes
cubemap_notes_handler(class_name="note", context=context)
