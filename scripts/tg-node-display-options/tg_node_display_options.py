'''
tg_node_display_options.py - Hides or unhides the preview display all nodes
of a selected class type.

This script utilizes Terragen's remote procedure call feature to modify the 
preview display state for all items of a selected class in the project.

Some class types, like camera, have multitple preview parameters. Checkbuttons
allow individual control over each parameter.

The script's UI is colour coded to match the corresponding node colour in the
Terragen UI.
'''
import os.path
import platform
import traceback
import tkinter as tk
from tkinter import messagebox
import terragen_rpc as tg

gui = tk.Tk()
gui.title(os.path.basename(__file__))
gui.geometry("566x362" if platform.system() == "Darwin" else
             "514x368")
# object, shader, camera, node network, lighting, renderer node colours
gui_colours = ["#bdbdbd", "#ff7c8f", "#877c9b", "#666666", "#e4cfa6", "#be7c67"]
gui.configure(bg=gui_colours[3])

object_frame = tk.LabelFrame(gui, text="OBJECTS", relief="flat", bg=gui_colours[0])
shader_frame = tk.LabelFrame(gui, text="SHADERS", relief="flat", bg=gui_colours[1])
camera_frame = tk.LabelFrame(gui, text="CAMERAS", relief="flat", bg=gui_colours[2])
button_frame = tk.LabelFrame(
    gui,
    text="Select On/Off/Toggle and click Apply",
    relief="flat"
    )
object_frame.grid(row=0, column=0, padx=4, pady=4, sticky="WENS")
shader_frame.grid(row=1, column=0, padx=4, pady=4, sticky="WENS")
camera_frame.grid(row=2, column=0, padx=4, pady=4, sticky="WENS")
button_frame.grid(row=3, column=0, padx=4, pady=4, sticky="WENS")

class_dict = {
    'bounding_box' : ["preview_options_main_hidden"],
    'card' : ["preview_options_main_hidden"],
    'cube' : ["show_b-box_in_preview"],
    'disc' : ["show_b-box_in_preview"],
    'grass_clump' : ["preview_options_main_hidden"],
    'lake' : ["handle_in_preview"],
    'lwo_reader' : ["preview_options_main_hidden"],
    'obj_reader' : ["preview_options_main_hidden"],
    'octahedron' : ["show_b-box_in_preview"],
    'planet' : ["show_b-box_in_preview"],
    'poly_sphere' : ["preview_options_main_hidden"],
    'populator_v4' : ["show_b-box_in_preview"],
    'rock' : ["preview_options_main_hidden"],
    'sphere' : ["show_b-box_in_preview"],
    'tgo_reader' : ["preview_options_main_hidden"],
    'heightfield_shader' : ["show_b-box_in_preview"],
    'simple_shape_shader' : ["show_b-box_in_preview", "draw_shape_edges_in_preview"],
    'camera' : ["show_camera_body_in_preview", "show_frustum_in_preview", "show_path_in_preview"]
}

class_labels_dict = {
    'bounding_box' : "Bounding box",
    'card' : "Card",
    'cube' : "Cube",
    'disc' : "Disc",
    'grass_clump' : "Grass clump",
    'lake' : "Lake",
    'lwo_reader' : "LWO reader",
    'obj_reader' : "OBJ reader",
    'octahedron' : "Octahedron",
    'planet' : "Planet",
    'poly_sphere' : "Poly sphere",
    'populator_v4' : "Populator",
    'rock' : "Rock",
    'sphere' : "Sphere",
    'tgo_reader' : "TGO reader",
    'heightfield_shader' : "Heightfield",
    'simple_shape_shader' : "Simple Shape",
    'camera' : "Camera"
}

def popup_warning(title, message) -> None:
    '''
    Opens a window and displays a message.

    Args:
        title (str): Characters displayed at the top of the window.
        message (str): Characters displayed in the body of the window.

    Returns:
        None
    '''
    messagebox.showwarning(title, message)

def get_nodes_in_class(selected_class):
    '''
    Retrieves all nodes in the project matching the selected class.

    Args:
        selected_class (str): Class selected by user, i.e. Camera

    Returns:
        node_ids (list): Node ids of the selected class type.
    '''
    try:
        project = tg.root()
        node_ids = project.children_filtered_by_class(selected_class)
        return node_ids
    except ConnectionError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC connection error" + str(e))
        return None
    except TimeoutError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC timeout error" + str(e))
        return None
    except tg.ReplyError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC reply error" + str(e))
        return None
    except tg.ApiError:
        popup_warning(
            os.path.basename(__file__),
            "Terragen RPC API error" + str(traceback.format_exc())
            )
        return None

def action_on(node, param, num_params=0) -> None:
    '''
    Sets display options for selected node to visible.

    Args:
        node (obj): node object id
        param (str): single parameter to update
        num_params (int): total number of paramaters to update for this class type
    
    Returns:
        None
    '''
    if param == "preview_options_main_hidden":
        reset_other_preview_options(node, flag="on")
        set_node_param(node, param, "0")
    elif (num_params == 1) or (num_params > 1 and checkbox_status(param) == 1):
        set_node_param(node, param, "1")

def action_off(node, param, num_params=0) -> None:
    '''
    Sets display options for selected node to invisible.

    Args:
        node (obj): node object id
        param (str): single parameter to update
        num_params (int): total number of paramaters to update for this class type
    
    Returns:
        None
    '''
    if param == "preview_options_main_hidden":
        reset_other_preview_options(node, flag="off")
        set_node_param(node, param, "1")
    elif (num_params == 1) or (num_params > 1 and checkbox_status(param) == 1):
        set_node_param(node, param, "0")

def action_toggle(node, param, num_params=0) -> None:
    '''
    Toggles display options for selected node between visiable and invisible.

    Args:
        node (obj): node object id
        param (str): single parameter to update
        num_params (int): total number of paramaters to update for this class type
    
    Returns:
        None
    '''
    if (num_params == 1) or (num_params > 1 and checkbox_status(param) == 1):
        toggled_state = invert_param_value(node, param)
        set_node_param(node, param, toggled_state)

def take_action(node_ids, params) -> None:
    '''
    Loops through each node and all display parameters being affected. 
    Triggers action to take based on action mode selected.

    Args:
        node_ids (list): Node object ids matching selected class type
        params (list): String of selected class type parameters to modify

    Returns:
        None
    '''
    action = action_var.get()
    for node in node_ids:
        for param in params:
            match action:
                case "On":
                    action_on(node, param, num_params=len(params))
                case "Off":
                    action_off(node, param, num_params=len(params))
                case "Toggle":
                    action_toggle(node, param, num_params=len(params))

def reset_other_preview_options(node_id, flag=None) -> None:
    '''
    Some nodes have multiple preview options which need to be set to zero.
    When the node is hidden the "preview_options_main_hidden" param is 1.
    When the node is visible the "preview_options_main_texture" 
    
    Args:
        node_id (obj): The node id to update
        flag (str): on means hidden, off means visible

    Returns:
        None
    '''
    other_preview_options = [
        "preview_options_main_bounding_box",
        "preview_options_main_wireframe",
        "preview_options_wf_bounding_box",
        "preview_options_main_smooth_shaded",
        "preview_options_main_textured",
    ]
    for option in other_preview_options:
        if flag == "on" and option == "preview_options_main_textured":
            set_node_param(node_id, option, "1")
        else:
            set_node_param(node_id, option, "0")

def set_node_param(node_id, param, update_value) -> None:
    '''
    Updates the node's display parameter.

    Args:
        node_id (obj): node to update
        param (str): parameter to update
        update_value(str): new parameter value
    
    Returns:
        None
    '''
    try:
        node_id.set_param(param, update_value)
    except ConnectionError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC connection error" + str(e))
        return None
    except TimeoutError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC timeout error" + str(e))
        return None
    except tg.ReplyError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC reply error" + str(e))
        return None
    except tg.ApiError:
        popup_warning(
            os.path.basename(__file__),
            "Terragen RPC API error" + str(traceback.format_exc())
            )
        return None

def checkbox_status(param):
    '''
    Gets the current state of the checkbox corresponding to the param.

    Args:
        param (str): Node parameter matching checkbox

    Returns:
        (int): 0 not checked, 1 checked
    '''
    match param:
        case "show_camera_body_in_preview":
            return body_var.get()
        case "show_frustum_in_preview":
            return frustum_var.get()
        case"show_path_in_preview":
            return path_var.get()
        case "show_b-box_in_preview":
            return bounding_box_var.get()
        case "draw_shape_edges_in_preview":
            return profile_edge_var.get()

def toggle_param(node_id, parameter):
    '''
    Determines the current state of a parameter and 
    inverts it.

    Args:
        node_id (obj): Selected node id
        parameter (str): parameter to check

    Returns:
        current_state (str): Inverted value of state.
    '''
    current_state = node_id.get_param(parameter)
    if current_state == "0":
        set_node_param(node_id, parameter ,"1")
    else:
        set_node_param(node_id, parameter ,"0")
    return current_state

def invert_param_value(node_id, parameter):
    '''
    Toggles a parameter value between zero and one. Parameters with
    multiple value preview options are toggled between hidden and
    bounding box.

    Args:
        node_id (obj): Node id
        paramater (str): Node parameter

    Return:
        current_state (str): 0 = hidden, 1 = visible b-box
    '''
    current_state = node_id.get_param(parameter)
    if current_state == "0":
        current_state = "1"
    else:
        current_state = "0"
    return current_state

def set_apply_button_colour() -> None:
    '''
    Sets the background colour of the Apply button.
    
    Returns:
        None
    '''
    node_type = rb_var.get()
    if node_type == 17:
        apply.config(bg=gui_colours[2])
    elif node_type >= 15:
        apply.config(bg=gui_colours[1])
    else:
        apply.config(bg=gui_colours[0])

def on_apply() -> None:
    '''
    Triggers actions to update the display parameters of all nodes in the
    project which match the selected class type.

    Returns:
        None
    '''
    selected_class = class_list[rb_var.get()] # re camera
    params = class_dict[selected_class] # re body, fustrum, path
    node_ids = get_nodes_in_class(selected_class) # ids for cam01, 02 etc
    if node_ids:
        take_action(node_ids, params)

# tkinter variables
class_list = list(class_dict.keys())
rb_var = tk.IntVar()
bounding_box_var = tk.IntVar()
bounding_box_var.set(1)
profile_edge_var = tk.IntVar()
profile_edge_var.set(1)
body_var = tk.IntVar()
body_var.set(1)
frustum_var = tk.IntVar()
frustum_var.set(1)
path_var = tk.IntVar()
path_var.set(1)
action_var = tk.StringVar()
action_var.set("On")
apply_button_var = tk.StringVar()
apply_button_var.set(gui_colours[0])

# radio buttons
for count, (key, value) in enumerate(class_dict.items()):
    if count == 17:
        rb = tk.Radiobutton(
            camera_frame,
            text=class_labels_dict[key],
            variable=rb_var,
            value=count,
            bg=gui_colours[2],
            command=set_apply_button_colour
            )
        rb.grid(row=0, column=0, padx=4, pady=4, sticky="w")
    elif count >= 15:
        if count == 15:
            row = 0
        rb = tk.Radiobutton(
            shader_frame,
            text=class_labels_dict[key],
            variable=rb_var,
            value=count,
            bg=gui_colours[1],
            command=set_apply_button_colour
            )
        rb.grid(row=row, column=0, padx=4, pady=4, sticky="w")
        row +=1
    else:
        rb = tk.Radiobutton(
            object_frame,
            text=class_labels_dict[key],
            variable=rb_var,
            value=count,
            bg=gui_colours[0],
            command=set_apply_button_colour
            )
        row = count // 5 + 1
        col = count % 5
        rb.grid(row=row, column=col, padx=4, pady=4, sticky="w")

# checkbuttons
tk.Label(shader_frame, text="", width=11, bg=gui_colours[1]).grid(row=1, column=2)
bounding_box = tk.Checkbutton(
    shader_frame,
    text="B-box",
    variable=bounding_box_var,
    width=10,
    bg=gui_colours[1]
    )
bounding_box.grid(row=1,column=3, padx=4, pady=4, sticky="w")
profile_edge = tk.Checkbutton(
    shader_frame,
    text="Profile edge",
    variable=profile_edge_var,
    bg=gui_colours[1]
    )
profile_edge.grid(row=1, column=4, padx=4, pady=4, sticky="w")

tk.Label(camera_frame, text="", width=16, bg=gui_colours[2]).grid(row=1, column=2)
body = tk.Checkbutton(
    camera_frame,
    text="Body",
    variable=body_var,
    width=8,
    justify="left",
    bg=gui_colours[2]
    )
body.grid(row=0, column=3, padx=4, pady=4, sticky="w")
frustum = tk.Checkbutton(
    camera_frame,
    text="Frustum",
    variable=frustum_var,
    width=9,
    justify="left",
    bg=gui_colours[2]
    )
frustum.grid(row=0, column=4, padx=4, pady=4, sticky="w")
path = tk.Checkbutton(
    camera_frame,
    text="Path",
    variable=path_var,
    width=8,
    justify="left",
    bg=gui_colours[2]
    )
path.grid(row=0, column=5, padx=4, pady=4, sticky="w")

# buttons
apply = tk.Button(button_frame, text="Apply", command=on_apply, bg=apply_button_var.get())
apply.grid(row=0, column=0, padx=4, pady=4, sticky="w")

tk.Label(button_frame, text="", width=19).grid(row=0, column=1)

# action options
actions = ["On", "Off", "Toggle"]
for index, item in enumerate(actions):
    rb = tk.Radiobutton(
        button_frame,
        text=item,
        variable=action_var,
        value=actions[index],
        width=8,
        justify="left",
        )
    rb.grid(row=0, column=index+2, padx=4, pady=4, sticky="w")

gui.mainloop()
