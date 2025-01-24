'''
tg_splatter_craters.py - Randomly splatters the Crater shader throughout
the active Terragen project. Parameter values of the Crater shader are
randomly chosen based on min/max values in the UI.
'''

import os.path
import random
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import TclError
import terragen_rpc as tg

class ToolTip:
    '''
    Opens a tooltip window to display the description of the parameter
    the cursor is hovering over.
    '''
    def __init__(self, widget, text, control_var):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.control_var = control_var
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, _event):
        '''
        Displays the tooltip as cursor hovers over parameter.
        The event argument is not used within this function.
        '''
        if self.control_var.get():
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25

            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip,
                             text=self.text,
                             background="yellow",
                             relief="solid",
                             borderwidth=1,
                             justify="left",
                             anchor="w"
                             )
            label.pack()

    def hide_tooltip(self, _event):
        '''
        Hides the tooltip as cursor exits parameter.
        The event argument is not used within this function.
        '''
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

gui = tk.Tk()
gui.geometry("600x580")
gui.title(os.path.basename(__file__))

frame0 = tk.Frame(gui) # generic
frame1 = tk.Frame(gui) # position
frame2 = tk.Frame(gui) # crater params min max
frame3 = tk.Frame(gui) # other buttons and widgets
frame0.grid(row=0,column=0,padx=4,pady=4,sticky="WENS")
frame1.grid(row=1,column=0,padx=4,pady=4,sticky="WENS")
frame2.grid(row=2,column=0,padx=4,pady=4,sticky="WENS")
frame3.grid(row=3,column=0,padx=4,pady=4,sticky="WENS")

def on_apply() -> None:
    '''
    Triggers the creation of all new shaders to the project.
    Including crater, group, and other shaders assigned to
    the Crater's Rim shader input.

    Returns:
        None
    '''
    final_crater_group_name = get_group_name()
    final_rim_shader_name = get_rim_shader_name()
    compute_terrain_tuple = get_main_input_node()
    add_mountain_or_valley()
    crater_diameter = make_craters(final_crater_group_name, final_rim_shader_name)
    add_fractal_warp(crater_diameter)
    insert_into_network(compute_terrain_tuple)

def insert_into_network(compute_terrain_tuple) -> None:
    '''
    Connect last node added to project to the first Compute terrain
    node in project.

    Args:
        all_compute_terrain_nodes [list]: Node ids of Compute terrain node

    Returns:
        None
    '''
    if insert_into_flow.get() == "Output > Main input":
        set_compute_terrain_node_main_input(compute_terrain_tuple[0])
    elif insert_into_flow.get() == "Merge shader":
        merge_shader_path = add_merge_shader(compute_terrain_tuple)
        main_input_node.set(merge_shader_path)
        set_compute_terrain_node_main_input(compute_terrain_tuple[0])

def add_fractal_warp(crater_diameter) -> None:
    '''
    Triggers a Fractal Warp shader to be added after all crater shaders
    are added. Scale is based on crater diameter.

    Args:
        crater_diameter (float): Crater diameter
    '''
    if append_warp_var.get() is True:
        fractal_warp_path = add_warp_shader(crater_diameter)
        main_input_node.set(fractal_warp_path)

def make_craters(final_crater_group_name, final_rim_shader_name):
    '''
    Triggers calculation of crater parameters and creation of crater nodes.

    Args:
        final_crater_group_name (str): Crater name as determined by Terragen
        final_rim_shader_name (str): Path of shader assigned to rim shader

    Returns:
        crater_diameter (float): Diameter of last crater shader
    '''
    num_craters = int(quantity_var.get())
    for _ in range(num_craters):
        position_string = calc_position()
        crater_diameter = get_random_float(dia_min_var.get(), dia_max_var.get())
        depth = calc_depth(crater_diameter)
        height = calc_rim_height(crater_diameter)
        skirt = calc_rim_skirt(crater_diameter)
        soft = get_random_float(soft_min_var.get(), soft_max_var.get())
        tight = get_random_float(tight_min_var.get(), tight_max_var.get())
        crater_params = [
            position_string,
            crater_diameter,
            depth, height,
            skirt,
            soft,
            tight,
            final_crater_group_name,
            final_rim_shader_name
            ]
        crater_path = add_crater(crater_params)
        main_input_node.set(crater_path)
    return crater_diameter

def calc_position():
    '''
    Calculate the position values

    Returns:
        (str) Calculated xyz coordinate position, i.e. "0.0 1.1 2.2"
    '''
    x_deviation = get_deviation(x_area_var.get())
    z_deviation = get_deviation(z_area_var.get())
    x_min = get_min_coordinate(x_deviation, x_pos_var.get())
    x_max = get_max_coordinate(x_deviation, x_pos_var.get())
    z_min = get_min_coordinate(z_deviation, z_pos_var.get())
    z_max = get_max_coordinate(z_deviation, z_pos_var.get())
    x_coord = get_random_float(x_min, x_max)
    z_coord = get_random_float(z_min, z_max)
    return str(x_coord) + " 0.0 " + str(z_coord)

def calc_depth(crater_diameter):
    '''
    Calculate the depth of the crater, based on the crater's diameter

    Args:
        crater_diamter (float): Crater diameter

    Returns:
        depth (float): Crater depth
    '''
    if depth_check_var.get():
        depth = get_percentage_of_diameter(crater_diameter, depth_percent_var.get())
        if depth_offset_var.get() is True:
            offset_delta = depth * float(depth_percent_var.get())
            depth = get_random_float(depth - offset_delta, depth + offset_delta)
    else:
        depth = get_random_float(depth_min_var.get(), depth_max_var.get())
    return depth

def calc_rim_height(crater_diameter):
    '''
    Calculate the rim height of the crater, based on the crater's diameter

    Args:
        crater_diameter (float): Crater diameter

    Returns:
        height (float): Crater height
    '''
    if rim_height_var.get():
        height = get_percentage_of_diameter(crater_diameter, rim_height_percent_var.get())
        if rim_height_offset_var.get() is True:
            offset_delta = height * float(rim_height_percent_var.get())
            height = get_random_float(height - offset_delta, height + offset_delta)
    else:
        height = get_random_float(rim_height_min.get(), rim_height_max.get())
    return height

def calc_rim_skirt(crater_diameter):
    '''
    Calculate the rim skirt of the crater, based on the crater's diameter.

    Args:
        crater_diameter (float): Crater diameter

    Returns:
        skirt (float): Crater rim skirt
    '''
    if rim_skirt_var.get():
        skirt = get_percentage_of_diameter(crater_diameter, rim_skirt_percent_var.get())
        if rim_skirt_offset_var.get() is True:
            rim_skirt_percent_float = float(rim_skirt_percent_var.get())
            if rim_skirt_percent_float > 1.0:
                rim_skirt_percent_float = 1 / rim_skirt_percent_float # here
            offset_delta = skirt * rim_skirt_percent_float
            skirt = get_random_float(skirt - offset_delta, skirt + offset_delta)
    else:
        skirt = get_random_float(skirt_min_var.get(), skirt_max_var.get())
    return skirt

def add_mountain_or_valley() -> None:
    '''
    Triggers functions to add a Simple Shape shader to the project and
    updates shader path to assign to Main input.

    Returns:
        None
    '''
    if on_mountain_or_valley_var.get():
        sss_node_id, sss_node_name = add_simple_shape_shader()
        calc_sss_params(sss_node_id)
        main_input_node.set(sss_node_name)

def get_group_name():
    '''
    Triggers creation of group node.

    Returns:
        crater_group_name (str): Final group node name or empty string
    '''
    if group_var.get():
        final_crater_group_name = add_group(group_name_var.get())
    else:
        final_crater_group_name = ""
    return final_crater_group_name

def get_rim_shader_name():
    '''
    Triggers creation of rim shader. Determines type of shader to be
    assigned to rim shader, calls func to add shader to project.

    Returns:
        rim_shader_name (str): Final name of shader assigned to rim shader parameter.
    '''
    if rim_shader_check_var.get():
        selected_rim_shader = rim_shader_classes[rim_shader.current()]
        rim_shader_id, rim_shader_name = add_rim_shader(selected_rim_shader)
        set_rim_shader_params(rim_shader_id,selected_rim_shader)
    else:
        rim_shader_name = ""
    return rim_shader_name

def add_rim_shader(shader_class):
    '''
    Adds a shader to the project to be assigned to the crater's
    rim shader input.

    Args:
        shader_class (str): Type of shader to add

    Returns:
        node_id <obj>: Shader node id
        node_name (str): Shader's name as determined by Terragen
    '''
    project = tg.root()
    node_id = tg.create_child(project,shader_class)
    node_name = node_id.name()
    return node_id, node_name

def set_rim_shader_params(rim_shader_id, selected_rim_shader) -> None:
    '''
    Sets certain parameters for various Shader types assigned
    to the crater's Rim shader input.

    Args:
        rim_shader_id <obj>: Crater shader node id
        selected_rim_shader (str): Class of assigned shader

    Returns:
        None
    '''
    try:
        if selected_rim_shader == "fake_stones_shader":
            max_diameter = dia_max_var.get()
            stone_scale = get_percentage_of_diameter(max_diameter, "0.01")
            rim_shader_id.set_param("stone_scale",stone_scale)
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))

def get_main_input_node():
    '''
    Get the first Compute terrain node in the project and whatever is
    assigned to its Main input.

    Returns:
        all_compute_terrain_nodes []: Compute terrain node ids
    '''
    main_input_node.set("")
    compute_terrain_tuple = ()
    insert_mode = insert_into_flow.get()
    if insert_mode == "Don't":
        main_input_node.set("") # could break here instead
    else:
        compute_terrain_tuple = get_compute_terrain_nodes()
        if compute_terrain_tuple:
            if insert_mode == "Output > Main input":
                main_input_node.set(compute_terrain_tuple[1])
            else:
                main_input_node.set("")
    return compute_terrain_tuple

def add_merge_shader(compute_terrain_tuple):
    '''
    Add Merge shader to project, set params, and connect new crater
    network to existing node network.

    Args:
        all_compute_terrain_nodes [list]: Compute terrain node ids
        main_input_node (str): Path of node to assign to Main input

    Returns:
        node_name (str): Name of Merge shader added to project
    '''
    compute_terrain_main_input = compute_terrain_tuple[1]
    try:
        project = tg.root()
        node_id = tg.create_child(project,'merge_shader')
        node_id.set_param('input_node',compute_terrain_main_input)
        node_id.set_param('shader_A',main_input_node.get())
        node_id.set_param('mix_to_A',"1")
        node_id.set_param('merge_colour',"1")
        node_id.set_param('colour_merge_mode',"1")
        node_id.set_param('merge_displacement',"1")
        node_id.set_param('displace_merge_mode',"1")
        node_name = node_id.name()
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return node_name

def info_message(message_title, message_description) -> None:
    '''
    Opens window to display an info message.

    Args:
        message_title (str): Name of program
        message_description (str): Information message

    Returns: None
    '''
    messagebox.showinfo(title = message_title, message = message_description)

def add_simple_shape_shader():
    '''
    Adds a Simple Shape shader to the project.

    Returns:
        node_id <obj>: Simple Shape shader's node id
        node_name (str): Simple Shape shader's name
    '''
    try:
        project = tg.root()
        node_id = tg.create_child(project,'simple_shape_shader')
        node_name = node_id.name()
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return node_id, node_name

def calc_sss_params(node_id) -> None:
    '''
    Calculates the parameter values for a Simple Shape shader and calls
    func to update sss node.

    Returns:
        None
    '''
    position = str(x_pos_var.get()) + " 0.0 " + str(z_pos_var.get())
    shape = "1" # circle / elipse
    size = mountain_valley_size()
    displacement_amp = str(amplitude_var.get())
    displacement_edge_profile = "1" # smooth step
    displacement_edge_width = "100" # max smoothing
    displacement_edge_units = "1" # percent ?
    apply_displacement = "1"
    sss_param_values = [
        position,
        shape,
        size,
        displacement_amp,
        displacement_edge_profile,
        displacement_edge_width,
        displacement_edge_units,
        main_input_node.get(),
        apply_displacement
        ]
    set_sss_params(node_id, sss_param_values)

def set_sss_params(node_id, sss_param_values) -> None:
    '''
    Sets a Simple Shape shader's parameters in the project.

    Args:
        node_id <obj>: Simple Shape shader's node id.
        sss_params [list]: Parameter values as strings.

    Returns:
        None
    '''
    sss_params = [
        "position",
        "type_of_shape",
        "size",
        "displacement_amplitude",
        "displacement_edge_profile",
        "displacement_edge_width",
        "displacement_edge_units",
        "input_node",
        "apply_displacement"
    ]
    for index, value in enumerate(sss_params):
        try:
            node_id.set_param(value, sss_param_values[index])
        except ConnectionError as e:
            info_message("error", "Terragen RPC connection error" + str(e))
        except TimeoutError as e:
            info_message("error", "Terragen RPC timeout error" + str(e))
        except tg.ReplyError as e:
            info_message("error", "Terragen RPC reply error" + str(e))
        except tg.ApiError:
            info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))

def mountain_valley_size():
    '''
    Calculates the size needed for the Simple Shape shader
    acting as the mountain or valley node.

    Returns:
        size_str (str): XY size values
    '''
    max_area = max(float(x_area_var.get()), float(y_area_var.get()))
    size = max_area + float(dia_max_var.get())
    size_str = f"{size} {size}"
    return size_str

def add_group(group_name):
    '''
    Adds a group node to the project.

    Args:
        group_name (str): Name suggested for group by user.

    Returns:
        crater_name (str): Final name as determined by Terragen.
    '''
    try:
        project = tg.root()
        crater_group_id = tg.create_child(project,'group')
        crater_group_id.set_param('name', group_name)
        crater_name = crater_group_id.get_param('name')
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return crater_name

def add_warp_shader(crater_diameter):
    '''
    Adds a warp shader to the project. Sets its parameters based on the crater diameter.

    Args:
        crater_diameter (float): Diameter of last crater added

    Returns:
        fractal_warp_path (str): Path of Warp shader added to project.
    '''
    try:
        project = tg.root()
        fractal_warp_node = tg.create_child(project, 'fractal_warp_shader')
        fractal_warp_node.set_param('input_node', main_input_node.get())
        scale = crater_diameter * .25
        fractal_warp_node.set_param('scale',scale)
        fractal_warp_path = fractal_warp_node.path()
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return fractal_warp_path

def set_compute_terrain_node_main_input(compute_terrain) -> None:
    '''
    Sets the Main input the Compute terrain node after all craters and
    shaders are added to the project.
    
    Args:
        compute_terrain <obj>: Compute terrain node id
    '''
    try:
        compute_terrain_node = tg.node_by_path(compute_terrain)
        compute_terrain_node.set_param('input_node',main_input_node.get())
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))

def get_compute_terrain_nodes():
    '''    
    Gets first compute terrain node and returns its id and path of shader assigned to its main input

    Example:
        ('/Compute Terrain', 'Fractal warp shader 01')

    Return:
        compute_terrain_list (tuple): Compute terrain path, input_node assingment
    '''
    try:
        project = tg.root()
        compute_terrain_node_ids = project.children_filtered_by_class('compute_terrain')
        if compute_terrain_node_ids:
            for node in compute_terrain_node_ids:
                node_path = node.path()
                node_input = node.get_param('input_node')
                compute_terrain_tuple = (node_path, node_input)
                break # quit after first
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return compute_terrain_tuple

def get_compute_terrain_nodes_old1():
    '''    
    Gets all compute terrain nodes in project at root level and
    returns their node path and main input parameter assignment

    Example:
        [('/Compute Terrain', 'Fractal warp shader 01'), ('Compute terrain 01', 'Heightfield 01')]

    Return:
        compute_terrain_list [tuples]: Compute terrain path, input_node assingment
    '''
    compute_terrain_list = []
    try:
        project = tg.root()
        compute_terrain_node_ids = project.children_filtered_by_class('compute_terrain')
        if compute_terrain_node_ids:
            for node in compute_terrain_node_ids:
                node_path = node.path()
                node_input = node.get_param('input_node')
                compute_terrain_tuple = (node_path, node_input)
                compute_terrain_list.append(compute_terrain_tuple)
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return compute_terrain_list

def add_crater(crater_params):
    '''
    Add a Crater shader to the project.

    Args:
        crater_params []: Values to assign to new Crater shader parameters
        main_input_node (str): Path of node to assign as Main input

    Returns:
        crater_id <obj>: Crater shader node id
        crater_path (str): Path of Crater shader
    '''
    try:
        project = tg.root()
        crater_id = tg.create_child(project, 'crater_shader')
        crater_path = crater_id.path()
        set_crater_params(crater_id, crater_params) # HERE 5
    except ConnectionError as e:
        info_message("error", "Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        info_message("error", "Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        info_message("error", "Terragen RPC reply error" + str(e))
    except tg.ApiError:
        info_message("error", "Terragen RPC API error" + str(traceback.format_exc()))
    return crater_path

def set_crater_params(crater_id, crater_params) -> None:
    '''
    Set the parameter values for the current Crater shader.

    Args:
        crater_id <obj>: Crater node id
        crater_params []: Parameter values to assign to Crater shader.
        main_input_node (st): Path of node to assing to Main input
    
    Returns:
        None
    '''
    crater_param_names = [
        "center",
        "diameter",
        "depth",
        "rim_height",
        "rim_skirt",
        "rim_softness",
        "rim_tightness",
        "gui_group",
        "rim_shader"
        ]
    for i, value in enumerate(crater_param_names):
        crater_id.set_param(value,crater_params[i])
    if main_input_node.get():
        crater_id.set_param('input_node',main_input_node.get())

def get_min_coordinate(deviation, center):
    '''
    Subtract the deviation from the coordiate value to determine the minimum axis value

    Args:
        deviation (float): Absolute maximum value to deviate
        center (string): Axis value

    Returns:
        round_value (float): Minimum coordinate value rounded to two decimal places.
    '''
    try:
        minimum_value = float(center) - deviation
    except ValueError:
        minimum_value = -deviation
    rounded_value = round(minimum_value, 2)
    return rounded_value

def get_max_coordinate(deviation, center):
    '''
    Adds the deviation from the coordiate value to determine the minimum axis value

    Args:
        deviation (float): Absolute maximum value to deviate
        center (string): Axis value

    Returns:
        rounded_value (float): Max value rounded to two decimal places.
    '''
    try:
        maximum_value = float(center) + deviation
    except ValueError:
        maximum_value = deviation
    rounded_value = round(maximum_value, 2)
    return rounded_value

def get_deviation(tolerance):
    '''
    Calculates half of the value given it.

    Args:
        tolerance (float): The X or Z area value
    
    Returns:
        half_tolerance (float): Half of the area value
    '''
    try:
        half_tolerance = abs(float(tolerance) * 0.5)
    except ValueError:
        half_tolerance = 0.0
    return half_tolerance

def get_random_float(minimum, maximum):
    '''
    Converts non-floating values to float and generates a random
    floating value between the min and max arguements.

    Args:
        minimum (str): minimum value
        maximum (str): maximum value

    Returns:
        random_float (float): A randomized float value.
    '''
    try:
        min_value = float(minimum)
        max_value = float(maximum)
    except ValueError:
        min_value = 0.0
        max_value = 1.0
    random_float = random.uniform(min_value, max_value)
    rounded_random_float = round(random_float, 2)
    return rounded_random_float

def get_percentage_of_diameter(diameter_value, percent):
    '''
    Calculates a rounded off portion of a percent of the 
    value passed to it.  Typically a diameter and a percentage.

    Args:
        diameter_value (float): Typically a diameter value
        percent (float): Percentage of diameter_value needed

    Returns:
        rounded_percentage_of_diameter (float): A percentge of the diameter_value
    '''
    try:
        diameter_float = float(diameter_value)
        percent_of_diameter_float = float(percent)
    except ValueError:
        diameter_float = 1.0
        percent_of_diameter_float = 0.1
    percent_of_diameter = diameter_float * percent_of_diameter_float
    rounded_percent_of_diameter = round(percent_of_diameter, 2)
    return rounded_percent_of_diameter

def on_clip() -> None:
    ''''
    Gets the contents of the clipboard and sets position variables
    if valid coordinates.

    Returns:
        None
    '''
    try:
        clipboard_text = gui.clipboard_get()
    except TclError:
        clipboard_text = " "
    if clipboard_text:
        if clipboard_text[0:4] == "xyz:":
            trimmed_text = clipboard_text[5:]
            split_text = trimmed_text.split(",")
            x_pos_var.set(split_text[0])
            y_pos_var.set(split_text[1])
            z_pos_var.set(split_text[2])

def on_reset() -> None:
    '''
    Resets the position variables to zero.

    Returns:
        None
    '''
    x_pos_var.set("0.0")
    y_pos_var.set("0.0")
    z_pos_var.set("0.0")

def apply_preset(preset) -> None:
    '''
    Applies values from the preset crater dictionary to the script variables.

    Args:
        preset (str) Name of preset and preset dictionary key

    Returns:
        None
    '''
    param_values = crater_dict[preset]
    dia_min_var.set(param_values[0])
    dia_max_var.set(param_values[1])
    depth_min_var.set(param_values[2])
    depth_max_var.set(param_values[3])
    depth_percent_var.set(param_values[4])
    rim_min_var.set(param_values[5])
    rim_max_var.set(param_values[6])
    rim_height_percent_var.set(param_values[7])
    skirt_min_var.set(param_values[8])
    skirt_max_var.set(param_values[9])
    rim_skirt_percent_var.set(param_values[10])
    soft_min_var.set(param_values[11])
    soft_max_var.set(param_values[12])
    tight_min_var.set(param_values[13])
    tight_max_var.set(param_values[14])

# dia min, dia max, depth min, depth max, depth percent
# rim min, rim max, rim height percent,
# skirt min, skirt max, rim skirt percent,
# soft min, soft max, tight min, tight max
crater_dict = {
    "Very_tiny_craters": (
        "1", "10", "0.005", "0.25", "0.25",
        "0.05", "0.2", "0.1",
        "1", "20", "2",
        "0.15", "1", "2", "8"),
    "Tiny_craters": (
        "30", "100", "3", "12", "0.12",
        "5", "30", "0.1",
        "50", "150", "10",
        "0.6", "1", "3", "5"),
    "ALC_young": (
        "1000", "10000", "100", "1000", "0.2",
        "100", "200", "0.2",
        "500", "4000", "0.4",
        "0.2", "0.4", "10", "16"),
    "Mid_50k-200k": (
        "50000", "250000", "1000", "2000", "0.02",
        "100", "1000", "0.01",
        "1000", "10000", "0.1",
        "0.01", "0.45", "3", "4"),
    "Basins": (
        "250000", "500000", "5000", "12000", "0.06",
        "5000", "25000", "0.1",
        "100000", "300000", "0.05",
        "0.12", "0.05", "0.5", "6"),
    "Sci-fi_basins": (
        "250000", "500000", "5000", "12000", "0.06",
        "10000", "150000", "0.4",
        "100000", "300000", "0.05",
        "0.12", "0.05", "0.5", "6")
}

# var
show_tooltips_var = tk.BooleanVar()
append_warp_var = tk.BooleanVar()
quantity_var = tk.StringVar()
quantity_var.set("1")
group_var = tk.BooleanVar()
group_name_var = tk.StringVar()
group_name_var.set("Craters")
on_mountain_or_valley_var = tk.BooleanVar()
amplitude_var = tk.StringVar()
amplitude_var.set('100.0')
x_pos_var = tk.StringVar()
x_pos_var.set("0.0")
y_pos_var = tk.StringVar()
y_pos_var.set("0.0")
z_pos_var = tk.StringVar()
z_pos_var.set("0.0")
x_area_var = tk.StringVar()
x_area_var.set("1000.0")
y_area_var = tk.StringVar()
y_area_var.set("0.0")
z_area_var = tk.StringVar()
z_area_var.set("1000.0")
dia_min_var = tk.StringVar()
dia_min_var.set("500.0")
dia_max_var = tk.StringVar()
dia_max_var.set("1500.0")
depth_min_var = tk.StringVar()
depth_min_var.set("50.0")
depth_max_var = tk.StringVar()
depth_max_var.set("150.0")
depth_check_var = tk.BooleanVar()
depth_percent_var = tk.StringVar()
depth_percent_var.set("0.1")
depth_offset_var = tk.BooleanVar()
rim_min_var = tk.StringVar()
rim_min_var.set("5.0")
rim_max_var = tk.StringVar()
rim_max_var.set("20.0")
rim_height_var = tk.BooleanVar()
rim_height_percent_var = tk.StringVar()
rim_height_percent_var.set("0.1")
rim_height_offset_var = tk.BooleanVar()
skirt_min_var = tk.StringVar()
skirt_min_var.set("500.0")
skirt_max_var = tk.StringVar()
skirt_max_var.set("1500.0")
rim_skirt_var = tk.BooleanVar()
rim_skirt_percent_var = tk.StringVar()
rim_skirt_percent_var.set("0.1")
rim_skirt_offset_var = tk.BooleanVar()
rim_shader_check_var = tk.BooleanVar()
soft_min_var = tk.StringVar()
soft_min_var.set("0.0")
soft_max_var = tk.StringVar()
soft_max_var.set("1.0")
tight_min_var = tk.StringVar()
tight_min_var.set("0.0")
tight_max_var = tk.StringVar()
tight_max_var.set("16.0")
rim_shader_classes = [
    "alpine_fractal_shader_v2", "displacement_shader", "fake_stones_shader", "image_map_shader",
    "power_fractal_shader_v3", "strata_and_outcrops_shader_v2", "twist_and_shear_shader"]
main_input_node = tk.StringVar() # a node path i.e. "/Null 01"
main_input_node.set("")

# menu bar
menubar = tk.Menu(gui)
preset_menu = tk.Menu(menubar,tearoff=0)
preset_menu.add_command(
    label="Very tiny craters 1m-10m",
    command=lambda: apply_preset("Very_tiny_craters")
    )
preset_menu.add_command(label="Tiny craters 30m-100m",command=lambda: apply_preset("Tiny_craters"))
preset_menu.add_command(label="ALC young 1k-10k",command=lambda: apply_preset("ALC_young"))
preset_menu.add_command(label="Mid 50k-200k",command=lambda: apply_preset("Mid_50k-200k"))
preset_menu.add_command(label="Basins 250k-500k",command=lambda: apply_preset("Basins"))
preset_menu.add_command(
    label="Sci-Fi Basins 250k-500k",
    command=lambda: apply_preset("Sci-fi_basins")
    )
menubar.add_cascade(label="Presets",menu=preset_menu)

# frame0 - generic widgets
show_tooltips = tk.Checkbutton(frame0,text="Show tooltips",variable=show_tooltips_var)
show_tooltips.grid(row=0,column=0,padx=4,pady=4,sticky="w")

crater_number = tk.Label(frame0,text="Number of craters:")
crater_number.grid(row=1,column=0,padx=4,pady=4,sticky="w")
crater_number_tooltip = ToolTip(
    crater_number,
    text="Add this amount of craters to the project.",
    control_var=show_tooltips_var
    )
quantity = tk.Entry(frame0,textvariable=quantity_var)
quantity.grid(row=1,column=1,padx=4,pady=4,sticky="w")

crater_group = tk.Checkbutton(frame0,text="Group",variable=group_var)
crater_group.grid(row=2, column=0,padx=4,pady=4,sticky="w")
crater_group_tooltip = ToolTip(
    crater_group,
    text="When checked, the craters added to the project are \ngrouped" \
         " together under this group name.",
    control_var=show_tooltips_var
    )
crater_group_name = tk.Entry(frame0,textvariable=group_name_var)
crater_group_name.grid(row=2, column=1, padx=4, pady=4, sticky="w")

on_mountain_in_valley = tk.Checkbutton(
    frame0,
    text="On mountain or in valley?",
    variable=on_mountain_or_valley_var
    )
on_mountain_in_valley.grid(row=3, column=0, padx=4, pady=4, sticky="w")
on_mountain_in_valley_tooltip = ToolTip(
    on_mountain_in_valley,
    text="When checked, a Simple shape shader is first added to the" \
         " \nproject which the craters rest on. Positive values create " \
            "a \nhill and negative values create a valley. Can provide a" \
                " subtle \nslope for downstream erosion nodes to work on.",
            control_var=show_tooltips_var
            )
amplitude = tk.Entry(frame0, textvariable=amplitude_var)
amplitude.grid(row=3, column=1, padx=4, pady=4, sticky="w")

# frame 1 - position widgets
area_center = tk.Label(frame1,text="Area centre x,y,z: ")
area_center.grid(row=0,column=0,padx=4,pady=4,sticky="w")
area_center_tooltip = ToolTip(
    area_center,
    text="Center position coordinates of the area volume.",
    control_var=show_tooltips_var
    )
x_position = tk.Entry(frame1,textvariable=x_pos_var,width=10)
x_position.grid(row=0,column=1,padx=4,pady=4,sticky="w")
y_position = tk.Entry(frame1,textvariable=y_pos_var,width=10)
y_position.grid(row=0,column=2,padx=4,pady=4,sticky="w")
z_position = tk.Entry(frame1,textvariable=z_pos_var,width=10)
z_position.grid(row=0,column=3,padx=4,pady=4,sticky="w")

clip = tk.Button(frame1,text="Clip",command=on_clip)
clip.grid(row=0,column=4,padx=4,pady=4,sticky="w")
clip_tooltip = ToolTip(clip, text="Get coordinates from clipboard.", control_var=show_tooltips_var)

reset = tk.Button(frame1,text="Reset",command=on_reset)
reset.grid(row=0,column=5,padx=4,pady=4,sticky="w")
reset_tooltip = ToolTip(reset, text="Reset coordinates to origin", control_var=show_tooltips_var)

area_volume = tk.Label(frame1,text="Area volume x,y,z:")
area_volume.grid(row=1,column=0,padx=4,pady=4,sticky="w")
area_volume_tooltip = ToolTip(
    area_volume,
    control_var=show_tooltips_var,
    text="The center of each crater is randomly generated within this" \
         " \narea, around the area centre coordinates."
         )
x_area = tk.Entry(frame1,textvariable=x_area_var,width=10)
x_area.grid(row=1,column=1,padx=4,pady=4,sticky="w")
y_area = tk.Entry(frame1,textvariable=y_area_var,width=10)
y_area.grid(row=1,column=2,padx=4,pady=4,sticky="w")
y_area.config(state="readonly")
z_area = tk.Entry(frame1,textvariable=z_area_var,width=10)
z_area.grid(row=1,column=3,padx=4,pady=4,sticky="w")

# frame 2 - crater params
tk.Label(frame2,text="Minimum").grid(row=0,column=1,padx=4,pady=4,sticky="w")
tk.Label(frame2,text="Maximum").grid(row=0,column=2,padx=4,pady=4,sticky="w")
tk.Label(frame2,text="or % of diameter").grid(row=0,column=4,padx=4,pady=4,sticky="w")

diameter = tk.Label(frame2,text="Diameter:")
diameter.grid(row=1,column=0,padx=4,pady=4,sticky="w")
diameter_tooltip = ToolTip(
    diameter,
    control_var=show_tooltips_var,
    text="The diameter of each crater is randomly generated within" \
         " \nthe min/max values. Terragen default = 1000 metres."
         )
diameter_min = tk.Entry(frame2,textvariable=dia_min_var,width=10)
diameter_min.grid(row=1,column=1,padx=4,pady=4,sticky="w")
diameter_max = tk.Entry(frame2,textvariable=dia_max_var,width=10)
diameter_max.grid(row=1,column=2,padx=4,pady=4,sticky="w")

depth_l = tk.Label(frame2,text="Depth:")
depth_l.grid(row=2,column=0,padx=4,pady=4,sticky="w")
depth_l_tooltip = ToolTip(
    depth_l,
    control_var=show_tooltips_var,
    text="The depth value of each crater is randomly generated within" \
         " \nthe min/max values. Terragen default = 100 metres."
         )
depth_min = tk.Entry(frame2,textvariable=depth_min_var,width=10)
depth_min.grid(row=2,column=1,padx=4,pady=4,sticky="w")
depth_max = tk.Entry(frame2,textvariable=depth_max_var,width=10)
depth_max.grid(row=2,column=2,padx=4,pady=4,sticky="w")
depth_check = tk.Checkbutton(frame2, variable=depth_check_var)
depth_check.grid(row=2,column=3,padx=4,pady=4,sticky="w")
depth_check_tooltip = ToolTip(
    depth_check,
    control_var=show_tooltips_var,
    text="When checked, the percentage \nof diameter value is used" \
      "\ninstead of the min/max values."
      )
depth_percent = tk.Entry(frame2,textvariable=depth_percent_var,width=10)
depth_percent.grid(row=2,column=4,padx=4,pady=4,sticky="w")
depth_offset = tk.Checkbutton(frame2,text="\u00B1 Offset",variable=depth_offset_var)
depth_offset.grid(row=2,column=5,padx=4,pady=4,sticky="w")
depth_offset_tooltip = ToolTip(
    depth_offset,
    control_var=show_tooltips_var,
    text="When checked, and the crater depth is based on a % \nof the" \
         " diameter, a random offset is applied to depth."
         )

rim_height = tk.Label(frame2,text="Rim height:")
rim_height.grid(row=3,column=0,padx=4,pady=4,sticky="w")
rim_height_tooltip = ToolTip(
    rim_height,
    control_var=show_tooltips_var,
    text="The rim height value of each crater is randomly generated" \
         " \nwithin the min/max values. Terragen default = 10 metres."
         )

rim_height_min = tk.Entry(frame2,textvariable=rim_min_var,width=10)
rim_height_min.grid(row=3,column=1,padx=4,pady=4,sticky="w")
rim_height_max = tk.Entry(frame2,textvariable=rim_max_var,width=10)
rim_height_max.grid(row=3,column=2,padx=4,pady=4,sticky="w")

rim_height_check = tk.Checkbutton(frame2,variable=rim_height_var)
rim_height_check.grid(row=3,column=3,padx=4,pady=4,sticky="w")
rim_height_check_tooltip = ToolTip(
    rim_height_check,
    control_var=show_tooltips_var,
    text="When checked, the percentage \nof diameter value is used" \
         " \ninstead of the min/max values."
         )
rim_height_percent = tk.Entry(frame2,textvariable=rim_height_percent_var,width=10)
rim_height_percent.grid(row=3,column=4,padx=4,pady=4,sticky="w")
rim_height_offset = tk.Checkbutton(frame2,text="\u00B1 Offset",variable=rim_height_offset_var)
rim_height_offset.grid(row=3,column=5,padx=4,pady=4,sticky="w")
rim_height_offset_tooltip = ToolTip(
    rim_height_offset,
    control_var=show_tooltips_var,
    text="When checked, and the rim height is based on a % \nof the" \
         " diameter, a random offset is applied to rim height."
         )

rim_skirt = tk.Label(frame2,text="Rim skirt:")
rim_skirt.grid(row=4,column=0,padx=4,pady=4,sticky="w")
rim_skirt_tooltip = ToolTip(
    rim_skirt,
    control_var=show_tooltips_var,
    text="The rim skirt value of each crater is randomly generated" \
         " \nwithin the min/max values. Terragen default = 1000 metres."
         )

rim_skirt_min = tk.Entry(frame2,textvariable=skirt_min_var,width=10)
rim_skirt_min.grid(row=4,column=1,padx=4,pady=4,sticky="w")
rim_skirt_max = tk.Entry(frame2,textvariable=skirt_max_var,width=10)
rim_skirt_max.grid(row=4,column=2,padx=4,pady=4,sticky="w")

rim_skirt_check = tk.Checkbutton(frame2,variable=rim_skirt_var)
rim_skirt_check.grid(row=4,column=3,padx=4,pady=4,sticky="w")
rim_skirt_check_tooltip = ToolTip(
    rim_skirt_check,
    control_var=show_tooltips_var,
    text="When checked, the percentage \nof diameter value is used" \
         " \ninstead of the min/max values"
         )
rim_skirt_percent = tk.Entry(frame2,textvariable=rim_skirt_percent_var,width=10)
rim_skirt_percent.grid(row=4,column=4,padx=4,pady=4,sticky="w")
rim_skirt_offset = tk.Checkbutton(frame2,text="\u00B1 offset",variable=rim_skirt_offset_var)
rim_skirt_offset.grid(row=4,column=5,padx=4,pady=4,sticky="w")
rim_skirt_offset_tooltip = ToolTip(
    rim_skirt_offset,
    control_var=show_tooltips_var,
    text="When checked, and the rim skirt is based on a % \nof the" \
         " diameter, a random offset is applied to rim skirt."
         )

rim_softness = tk.Label(frame2,text="Rim softness:")
rim_softness.grid(row=5,column=0,padx=4,pady=4,sticky="w")
rim_softness_tooltip = ToolTip(
    rim_softness,
    control_var=show_tooltips_var,
    text="The rim softness value of each crater is randomly generated" \
         " \nwithin the min/max values. Terragen default value is 0.125"
         )
rim_soft_min = tk.Entry(frame2,textvariable=soft_min_var,width=10)
rim_soft_min.grid(row=5,column=1,padx=4,pady=4,sticky="w")
rim_soft_max = tk.Entry(frame2,textvariable=soft_max_var,width=10)
rim_soft_max.grid(row=5,column=2,padx=4,pady=4,sticky="w")

rim_tightness = tk.Label(frame2,text="Rim tightness:")
rim_tightness.grid(row=6,column=0,padx=4,pady=4,sticky="w")
rim_tightness_tooltip = ToolTip(
    rim_tightness,
    control_var=show_tooltips_var,
    text="The rim tightness value of each crater is randomly generated" \
         " \nwithin the min/max values. Terragen default value is 4."
         )
rim_tight_min = tk.Entry(frame2,textvariable=tight_min_var,width=10)
rim_tight_min.grid(row=6,column=1,padx=4,pady=4,sticky="w")
rim_tight_max = tk.Entry(frame2,textvariable=tight_max_var,width=10)
rim_tight_max.grid(row=6,column=2,padx=4,pady=4,sticky="w")

rim_shader_check = tk.Checkbutton(frame2,text="Rim shader",variable=rim_shader_check_var)
rim_shader_check.grid(row=7, column=0, padx=4, pady=4, sticky="w")
rim_shader_check_tooltip = ToolTip(
    rim_shader_check,
    control_var=show_tooltips_var,
    text="When checked, a new shader of the selected \ntype is assigned" \
         " to all the craters in this group."
         )
rim_shader = ttk.Combobox(
    frame2,
    values=[
        "Alpine","Displacement","Fake stones","Image map",
        "Power fractal shader_v3","Strata_and_outcrops","Twist_and_shear"
        ]
        )
rim_shader.grid(row=7, column=1, padx=4, pady=4, sticky="w")
rim_shader.current(0)

# frame 3 - other widgets and buttons
insert = tk.Label(frame3,text="Insertion mode:")
insert.grid(row=0,column=0,padx=4,pady=4,sticky="w")
insert_tooltip = ToolTip(
    insert,
    control_var=show_tooltips_var,
    text="Don't - will not insert craters into the workflow. \nOutput" \
         " > Main input inserts crater into the workflow \nMerge " \
            "shader inserts craters via merge."
            )

insert_into_flow = ttk.Combobox(frame3,values=["Don't","Output > Main input","Merge shader"])
insert_into_flow.grid(row=0,column=1,padx=4,pady=4,sticky="w")
insert_into_flow.current(1)

append_warp = tk.Checkbutton(frame3,text="Append fractal warp shader?",variable=append_warp_var)
append_warp.grid(row=1,column=0,padx=4,pady=4,sticky="w")
append_warp_tooltip = ToolTip(
    append_warp,
    control_var=show_tooltips_var,
    text="When checked, a Fractal warp shader is added to the \nproject" \
         " after the last crater.  Its Scale value is approximately" \
             " \n1/4 of the maximum Diameter parameter value."
             )

apply = tk.Button(frame3,text="Apply",command=on_apply)
apply.grid(row=2,column=0,padx=4,pady=4,sticky="w")
apply_tooltip = ToolTip(
    apply,
    text="Clicking this button will add the craters to the project.",
    control_var=show_tooltips_var
    )

gui.config(menu=menubar)
gui.mainloop()
