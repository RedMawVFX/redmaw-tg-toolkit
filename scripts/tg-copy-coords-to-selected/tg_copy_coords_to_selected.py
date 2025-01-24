'''
tg_copy_coords_to_selected.py - Copies xyz coordinates from the clipboard to the 
selected nodes. Selected nodes without xyz coordinate parameters are ignored.
'''

import sys
import os.path
import traceback
import tkinter as tk
from tkinter import messagebox
import terragen_rpc as tg

gui = tk.Tk()
gui.withdraw()

def info_message(message_title, message_description) -> None:
    '''
    Opens window to display an info message.

    Args:
        message_title (str): Name of program
        message_description (str): Information message

    Returns: None
    '''
    messagebox.showinfo(title = message_title, message = message_description)

def filter_selected_node_ids(selected_node_ids):
    '''
    Nodes of certain classes and the default background node should remain
    unaffected even if selected by user. Removes those nodes from selection.

    Args:
        selected_node_ids (list): Node object ids

    Returns:
        filtered_node_ids (list): Node object ids that are okay to modify.
    '''
    nodes_to_exclude_ids = get_nodes_to_exclude()
    background_sphere_id = get_background_sphere()
    if background_sphere_id:
        nodes_to_exclude_ids.extend(background_sphere_id)
    filtered_node_ids = remove_common_node_ids(selected_node_ids, nodes_to_exclude_ids)
    return filtered_node_ids

def get_background_sphere():
    '''
    Gets the default background sphere node id.

    Returns:
        (list): background node id or None
    '''
    try:
        background_sphere_id = tg.node_by_path("/Background")
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return [background_sphere_id]

def remove_common_node_ids(selected_node_ids, nodes_to_exclude_ids):
    '''
    Removes node ids common to both lists.

    Args:
        selected_node_ids (list): Node ids selected by user.
        nodes_to_exclude_ids (list): Node ids that match excluded classes.

    Return:
        (list): Node ids that are okay to modify.
    '''
    return [item for item in selected_node_ids if item not in nodes_to_exclude_ids]

def get_nodes_to_exclude():
    '''
    Builds list of node ids that match exclude class types.

    Return:
        nodes_to_exclude (list): Node ids to exclude.
    '''
    nodes_to_exclude = []
    classes_to_exclude = ["planet", "easy_cloud", "cloud_layer_v3", "cloud_layer_v2"]
    try:
        project = tg.root()
        for c in classes_to_exclude:
            node_ids = tg.children_filtered_by_class(project, c)
            if node_ids:
                nodes_to_exclude.extend(node_ids)
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return nodes_to_exclude

def get_clipboard_contents():
    '''
    Retrieves and validates clipboard contents.

    Returns:
        xyz_coords (str): xyz coordinates, i.e. "0.0 1.1 2.2"
    '''
    clipboard_content = gui.clipboard_get()
    if clipboard_content[0:4] == "xyz:":
        trimmed_content = clipboard_content[5:]
        split_content = trimmed_content.split(",")
        xyz_coords = str(split_content[0] + " " + split_content[1] + " " + split_content[2])
    else:
        script_name = get_filename()
        info_message(script_name, "Invalid coordinates in clipboard.")
        sys.exit()
    return xyz_coords

def get_user_selection():
    '''
    Gets the node ids selected by the user.

    Returns:
        selected_node_ids (list): Selected node ids
    '''
    try:
        selected_node_ids = tg.current_selection()
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    if len(selected_node_ids) == 0:
        script_name = get_filename()
        info_message(script_name, "No nodes selected.")
        sys.exit()
    return selected_node_ids

def set_params(filtered_node_ids, xyz_coords) -> None:
    '''
    Updates xyz coordinate parameters for nodes.

    Args:
        filtered_node_ids (list): The node ids to update
        xyz_coords (str): xyz coordinate values

    Returns:
        None
    '''
    xyz_coord_types = ["position", "center", "centre", "translate", "area_centre"]
    try:
        for node in filtered_node_ids:
            params = node.param_names()
            for xyz_type in xyz_coord_types:
                if xyz_type in params:
                    node.set_param(xyz_type, xyz_coords)
                    break
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))

def get_filename():
    '''
    Gets the script's filename via Python os module.
    
    Returns:
        script_name (str): Script name.
    '''
    script_name = os.path.basename(__file__)
    return script_name

def main():
    '''
    Main entry point for the script. Acquires clipboard data, user selection and 
    modifies xyz coordinate values of filtered nodes.
    '''
    xyz_coords = get_clipboard_contents()
    selected_node_ids = get_user_selection()
    filtered_node_ids = filter_selected_node_ids(selected_node_ids)
    if filtered_node_ids:
        set_params(filtered_node_ids, xyz_coords)

main()
