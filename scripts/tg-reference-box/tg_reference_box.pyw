'''
tg_add_reference_box.py - Adds a user defined reference box to the current project.

This script utilizes Terragen's remote procedure call feature to add a 
bounding box class object to the project.

Includes a UI to set the scale of the reference box.  Position of reference
box is based on origin or valid coordinates in the clipboard.

The menubar includes a list of presets.
'''

import sys
import os.path
import platform
import traceback
import tkinter as tk
import terragen_rpc as tg

# Add the parent directory (scripts) to sys.path in order to import from commons
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from commons.node_network_layout import auto_position_node

if platform.system() == "Darwin":
    # we'll use these to create coloured buttons on the Mac
    from PIL import Image, ImageTk

gui = tk.Tk()
gui.geometry("459x692" if platform.system() == "Darwin" else
             "345x690")
gui.title(os.path.basename(__file__))

frame0 = tk.LabelFrame(gui, text="Size of reference box in metres")
frame1 = tk.LabelFrame(gui, text="Rotate reference box")
frame2 = tk.LabelFrame(gui, text="Click to add reference box & set preview colour.")
frame3 = tk.LabelFrame(gui, text="Other stuff")
frame4 = tk.LabelFrame(gui, text="Messages")
frame0.grid(row=0, column=0, padx=8, pady=8, sticky="WENS")
frame1.grid(row=1, column=0, padx=8, pady=8, sticky="WENS")
frame2.grid(row=2, column=0, padx=8, pady=8, sticky="WENS")
frame3.grid(row=3, column=0, padx=8, pady=8, sticky="WENS")
frame4.grid(row=4, column=0, padx=8, pady=8, sticky="WENS")

colour_dict = {
    "red" : "1 0 0",
    "lime" : "0 1 0",
    "blue" : "0 0 1",
    "fuchsia" : "1 0 1",
    "aqua" : "0 1 1",
    "yellow" : "1 1 0",
    "purple" : "0.5 0 1",
    "orangered" : "1 0.5 0",
    "green" : "0 0.5 0",
    "white" : "1 1 1 ",
    "gray" : "0.5 0.5 0.5",
    "black" : "0 0 0"
}

# radiobutton, size modifier xyz, zero axis, align at base
preset_dict = {
    "human" : (1, "-0.5", "1.0", "-0.5", False, True),
    "moai" : (1, "0.6", "3.0", "0.6", False, True),
    "f150" : (1, "1.03", "0.92", "4.89", False, True),
    "liberty" : (10, "6.15", "36.02", "3.56", False, True),
    "747" : (100, "-35.6", "-80.6", "-29.29", False, True),
    "godzilla" : (100, "-60.0", "-50.0", "0.0", False, True),
    "eiffel" : (100, "25.0", "200.0", "25.0", False, True),
    "mile" : (2000, "-390.66", "-390.66", "-390.66", False, True),
    "helen" : (10000, "-300.0", "-8700.0", "-300.0", False, True),
    "everest" : (20000, "-10000.0", "-11151.1", "0.0", False, True),
    "fuji" : (50000, "0.0", "-46224.0", "0.0", False, True),
    "olympus" : (500000, "101895.0", "-478100.0", "101895.0", False, True)
}

def on_clear_button_click() -> None:
    '''
    Clears the clipboard content.

    Returns:
        None
    '''
    gui.clipboard_clear()
    gui.clipboard_append(" ") # to avoid an empty clipboard error once cleared
    set_message("clear")

def on_colour_button_click(colour) -> None:
    '''
    Triggers actions to add a bounding box to the project.

    Returns:
        None
    '''
    scale_final = calc_scale()
    add_bounding_box(colour, scale_final)

def calc_scale():
    '''
    Calculates xyz axis scale for bounding box.

    Returns:
        scale_final (str): xyz axis scale values. string of float values.
    '''
    base_scale = size_var.get()
    try:
        modified_x_size = float(base_scale) + float(size_modifier_x_var.get())
    except ValueError:
        modified_x_size = float(base_scale)
    try:
        if zero_y_var.get() is True:
            modified_y_size = 0
        else:
            modified_y_size = float(base_scale) + float(size_modifier_y_var.get())
    except ValueError:
        modified_y_size = float(base_scale)
    try:
        modified_z_size = float(base_scale) + float(size_modifier_z_var.get())
    except ValueError:
        modified_z_size = float(base_scale)

    scale_final = str(modified_x_size) + " " + str(modified_y_size) + " " + str(modified_z_size)
    scale_final_rounded = round_coords_string(scale_final)
    return scale_final_rounded

def add_bounding_box(colour, scale_final) -> None:
    '''
    Adds a bounding box to the project.

    Args:
        colour (str): colour name text, i.e. red
        scale_final (str): scale values as xyz, i.e. 1 1 1

    Returns:
        None
    '''
    try:
        project = tg.root()
        bbox = tg.create_child(project,"bounding_box")
        set_bbox_params(colour, scale_final, bbox)
        auto_position_node(bbox, "bounding_box")
    except ConnectionError as e:
        set_message("error", msg="Terragen RPC connection error" + str(e))
    except TimeoutError as e:
        set_message("error", msg="Terragen RPC timeout error" + str(e))
    except tg.ReplyError as e:
        set_message("error", msg="Terragen RPC reply error" + str(e))
    except tg.ApiError:
        set_message("error", msg="Terragen RPC API error" + str(traceback.format_exc()))

def set_bbox_params(colour, scale_final, bbox) -> None:
    '''
    Sets parameters for the bounding box.

    Args:
        colour (str): colour name text, i.e. red
        scale_final (str): scale values as xyz, i.e. 1 1 1
        bbox (list): bounding box node id

    Returns:
        None
    '''
    if name_var.get():
        scale_elements = scale_final.split(" ")
        pos_x_rounded = (round(float(scale_elements[0])))
        pos_y_rounded = (round(float(scale_elements[1])))
        pos_z_rounded = (round(float(scale_elements[2])))
        bbox_name = f"refBox {colour} ~{pos_x_rounded}x{pos_y_rounded}x{pos_z_rounded} m"
        bbox.set_param("name",bbox_name)
    bbox.set_param("preview_options_use_preview_colour","1")
    bbox.set_param("preview_options_preview_colour",colour_dict[colour])
    bbox.set_param("preview_options_main_bounding_box", "1")
    bbox.set_param("scale",scale_final)
    pos = calc_translate_coords(scale_final)
    if pos:
        bbox.set_param("translate",pos)
    rot = rotate_slider.get()
    if int(rot) != 0:
        bbox.set_param("rotate","0 " + str(rot) + " 0")
    set_message("add", msg=(
        f"{colour} reference box added at: \n"
        f"position (xyz): {pos}\n"
        f"scale (xyz): {scale_final}\n"
        f"rotation (y): {rot} degrees"
    ))

def calc_translate_coords(scale_final):
    '''
    Determines the final position of the box based on valide
    clipboard data if any and if box is aligned at its base.

    Args:
        scale_final (str): Diminsions of the box.

    Returns:
        postion (str): xyz coordinates of the box.
    '''
    pos_x = pos_y = pos_z = 0.0
    try:
        clipboard_text = gui.clipboard_get()
    except tk.TclError:
        clipboard_text = " " # not sure why clipboard isn't always returning contents as expected
    if clipboard_text:
        if clipboard_text[0:4] == "xyz:":
            trimmed_text = clipboard_text[5:]
            split_text = trimmed_text.split(",")
            pos_x = float(split_text[0])
            pos_y = float(split_text[1])
            pos_z = float(split_text[2])
            # position = str(split_text[0] + " " + split_text[1] + " " + split_text[2])
    if align_on_base_var.get() is True:
        scale_elements = scale_final.split(" ") # string of float values
        if scale_elements[1] != "0.0":
            half_of_y_scale = float(scale_elements[1]) * 0.5
            pos_y = pos_y + abs(half_of_y_scale)
    pos_x_rounded = round(pos_x, 2)
    pos_y_rounded = round(pos_y, 2)
    pos_z_rounded = round(pos_z, 2)
    position = str(pos_x_rounded) + " " + str(pos_y_rounded) + " " + str(pos_z_rounded)
    return position

def round_coords_string(coords, decimal = 2):
    '''
    Rounds off the coordinate values to a desired number of places

    Args:
        coords (str): Typically position or scale values, i.e. "0.01 1.12 2.23"
        decimal (int): Number of places of the decimal fraction to keep

    Returns:
        (str) Coordinates at the desired number of decimal places, i.e. "1.0 2.0 3.0"
    '''
    split_coords = coords.split(" ")
    x_coord_rounded = round(float(split_coords[0]), decimal)
    y_coord_rounded = round(float(split_coords[1]), decimal)
    z_coord_rounded = round(float(split_coords[2]), decimal)
    return str(x_coord_rounded) + " " + str(y_coord_rounded) + " " + str(z_coord_rounded)

def on_show_hide_button_click(flag) -> None:
    '''
    Enables or disables all bounding boxes in the project.

    Args:
        flag (str): "off" disable, "on" enable

    Returns:
        None
    '''
    try:
        all_boxes = get_all_boxes()
        if all_boxes:
            enable_disable_boxes(all_boxes, flag)
            set_message(flag, qty=str(len(all_boxes)))
        else:
            set_message("None")
    except ConnectionError as e:
        my_message.set("Terragen RPC connection error" + str(e))
        update_text_box()
    except TimeoutError as e:
        my_message.set("Terragen RPC timeout error" + str(e))
        update_text_box()
    except tg.ReplyError as e:
        my_message.set("Terragen RPC reply error" + str(e))
        update_text_box()
    except tg.ApiError:
        my_message.set("Terragen RPC API error" + str(traceback.format_exc()))
        update_text_box()

def enable_disable_boxes(all_boxes, flag) -> None:
    '''
    Sets the value of the enable parameter for the bounding boxes.

    Args:
        all_boxes (list): ids of all boxes in the project
        flag (str): "off" disable, "on" enable

    Returns:
        None
    '''
    for box in all_boxes:
        if flag == "off":
            box.set_param("enable", "0")
        else:
            box.set_param("enable", "1")

def set_message(flag, qty=None, msg=None) -> None:
    '''
    Sets the text for the message box based on the flag.

    Args:
        flag (str): "off", "on", "None", "removed", "clear", "rotation", "modifier", "error"
        qty (str): number of bounding boxes in project acted upon
        msg (str): specific message to display

    Return:
        None
    '''
    match flag:
        case "off":
            my_message.set(qty + " bounding boxes disabled.")
        case "on":
            my_message.set(qty + " bounding boxes enabled.")
        case "None":
            my_message.set("No bounding boxes found.")
        case "removed":
            my_message.set(qty + " bounding boxes removed.")
        case "clear":
            my_message.set("Clipboard contents cleared.")
        case "rotation":
            my_message.set("Rotation value set to zero.")
        case "modifier":
            my_message.set("Modifier values reset to zero.")
        case "add":
            my_message.set(msg)
        case "error":
            my_message.set(msg)
        case "preset_key":
            my_message.set(msg)
    update_text_box()

def on_remove() -> None:
    '''
    Deletes all bounding boxes in the project.

    Returns:
        None
    '''
    all_boxes = get_all_boxes()
    if all_boxes:
        for box in all_boxes:
            tg.delete(box)
        set_message("removed", qty=str(len(all_boxes)))
    else:
        set_message("None")

def get_all_boxes():
    '''
    Gets all node ids for bounding boxes in the project.

    Returns:
        all_boxes (list): Bounding box node ids
    '''
    try:
        project = tg.root()
        all_boxes = project.children_filtered_by_class("bounding_box")
        return all_boxes
    except ConnectionError as e:
        set_message("error", msg="Terragen RPC connection error" + str(e))
        return None
    except TimeoutError as e:
        set_message("error", msg="Terragen RPC timeout error" + str(e))
        return None
    except tg.ReplyError as e:
        set_message("error", msg="Terragen RPC reply error" + str(e))
        return None
    except tg.ApiError:
        set_message("error", msg="Terragen RPC API error" + str(traceback.format_exc()))
        return None

def on_reset_modifier_button_click() -> None:
    '''
    Resets the modifier value to zero.

    Returns:
        None
    '''
    size_modifier_x_var.set("0")
    size_modifier_y_var.set("0")
    size_modifier_z_var.set("0")
    set_message("modifier")

def on_reset_rotation_button_click() -> None:
    '''
    Resets the rotation slider's value to zero.

    Returns:
        None
    '''
    rotate_slider.set(0)
    set_message("rotation")

def update_text_box() -> None:
    '''
    Displays the current message for whatever feature was ran.

    Return:
        None
    '''
    new_text = my_message.get()
    message_tb.delete("1.0", "end")
    message_tb.insert("1.0",new_text)

def apply_preset(preset_key) -> None:
    '''
    Applies values from the chosen preset to each parameter.

    Args:
        preset_key (str): Item to use a key to the preset dictionary.

    Returns:
        None
    '''
    size_var.set(preset_dict[preset_key][0])
    size_modifier_x_var.set(preset_dict[preset_key][1])
    size_modifier_y_var.set(preset_dict[preset_key][2])
    size_modifier_z_var.set(preset_dict[preset_key][3])
    zero_y_var.set(preset_dict[preset_key][4])
    align_on_base_var.set(preset_dict[preset_key][5])
    set_message("preset_key", msg=f"{preset_key} preset paramaters applied.")

def update_rotation_slider_from_entry(_) -> None:
    '''
    Syncs the value of the rotation slider and entry widgets.

    Args:
        (_): The unused FocusOut or Return event calling this function. 

    Returns:
        None
    '''
    try:
        value = float(rotate_entry.get())
        if -360 <= value <= 360:
            rotate_slider.set(value)
        else:
            rotate_entry.delete(0, tk.END)
            rotate_entry.insert(0, str(rotate_slider.get()))
    except ValueError:
        pass # ignore invalid input

def update_rotation_entry_from_slider(_) -> None:
    '''
    Syncs the value of the rotation slider and entry widgets.

    Args:
        (_): The unused FocusOut or Return event calling this function. 

    Returns:
        None
    '''
    rotate_entry.delete(0, tk.END)
    rotate_entry.insert(0, str(rotate_slider.get()))

# tkinter variables
size_var = tk.IntVar()
size_var.set(1000)
size_modifier_x_var = tk.StringVar()
size_modifier_x_var.set("0")
size_modifier_y_var = tk.StringVar()
size_modifier_y_var.set("0")
size_modifier_z_var = tk.StringVar()
size_modifier_z_var.set("0")
zero_y_var = tk.BooleanVar()
zero_y_var.set(True)
align_on_base_var = tk.BooleanVar()
align_on_base_var.set(False)
my_message = tk.StringVar()
my_message.set("Welcome. \nClick a colour button to add a \nreference box to the project.")
name_var = tk.IntVar()
name_var.set(1)
scale_presets = [
    "1", "10", "100", "1000", "2500", "5000",
    "10000", "25000", "50000", "100000", "250000", "500000"
    ]

# menu bar
menubar = tk.Menu(gui)
preset_menu = tk.Menu(menubar, tearoff=0)
preset_menu.add_command(label="Human", command=lambda: apply_preset("human"))
preset_menu.add_command(label="Moai", command=lambda: apply_preset("moai"))
preset_menu.add_command(label="Ford F150", command=lambda: apply_preset("f150"))
preset_menu.add_command(label="Boeing 747", command=lambda: apply_preset("747"))
preset_menu.add_command(label="Godzilla 1954", command=lambda: apply_preset("godzilla"))
preset_menu.add_command(label="Statue Liberty", command=lambda: apply_preset("liberty"))
preset_menu.add_command(label="Eiffel Tower", command=lambda: apply_preset("eiffel"))
preset_menu.add_command(label="1 Mile", command=lambda: apply_preset("mile"))
preset_menu.add_command(label="Mount St. Helen", command=lambda: apply_preset("helen"))
preset_menu.add_command(label="Mount Fuji", command=lambda: apply_preset("fuji"))
preset_menu.add_command(label="Mount Everest", command=lambda: apply_preset("everest"))
preset_menu.add_command(label="Olympus Mons", command=lambda: apply_preset("olympus"))
menubar.add_cascade(label="Presets", menu=preset_menu)

# frame 0 - radio button - size and offset
for i, preset in enumerate(scale_presets):
    formatted_preset = f"{int(preset):,}"
    rb = tk.Radiobutton(frame0, text=formatted_preset, variable=size_var, value=int(preset))
    row = i // 4 + 1
    col = i % 4
    rb.grid(row=row, column=col, padx=2, pady=2, sticky="w")

tk.Label(frame0,text="Size modifier \u00B1: ").grid(row=4, column=0, padx=2, pady=2, sticky="w")
size_modifier_x = tk.Entry(frame0, textvariable=size_modifier_x_var, width=10)
size_modifier_y = tk.Entry(frame0, textvariable=size_modifier_y_var, width=10)
size_modifier_z = tk.Entry(frame0, textvariable=size_modifier_z_var, width=10)

size_modifier_x.grid(row=4, column=1, padx=4, sticky="w")
size_modifier_y.grid(row=4, column=2, padx=4, sticky="w")
size_modifier_z.grid(row=4, column=3, padx=4, sticky="w")

zero_y = tk.Checkbutton(frame0, text="Zero Y axis", variable=zero_y_var)
zero_y.grid(row=6, column=0, padx=4, pady=4, sticky="w")

align_on_base = tk.Checkbutton(frame0, text="Align Y at base", variable=align_on_base_var)
align_on_base.grid(row=6, column=2, columnspan=2, padx=4, pady=4, sticky="w")

reset_size_modifier_b = tk.Button(frame0,
                                  text="Reset modifier",
                                  command=on_reset_modifier_button_click
                                  )
if platform.system() == "Windows":
    reset_size_modifier_b.config(bg="#E7D8E7")
reset_size_modifier_b.grid(row=5, column=0, columnspan=2, padx=4, pady=4, sticky="w")

# frame 1 - rotation slider and reset button
rotate_slider = tk.Scale(frame1,
                         from_=-360,
                         to=360,
                         orient=tk.HORIZONTAL,
                         showvalue=1,
                         length=200,
                         command=update_rotation_entry_from_slider,
                         bg="#CBAE98",
                         troughcolor="#B8DBD0",
                         highlightthickness=0,
                         highlightbackground="#CBAE98"
                         )
rotate_slider.grid(row=0, column=0, sticky='w', columnspan=3, padx=4, pady=4)

rotate_entry = tk.Entry(frame1, width=10)
rotate_entry.grid(row=0, column=3, padx=4, pady=4, sticky="w")
rotate_entry.insert(0, str(rotate_slider.get()))
rotate_entry.bind("<Return>", update_rotation_slider_from_entry)
rotate_entry.bind("<FocusOut>", update_rotation_slider_from_entry)

reset_rot_b = tk.Button(frame1,
                        text="Reset rotation",
                        command=on_reset_rotation_button_click
                        )
if platform.system() == "Windows":
    reset_rot_b.config(bg="#E7D8E7")
reset_rot_b.grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="w")

# frame 2 - colour Buttons
button_images = {}
for index, key in enumerate(colour_dict):
    if platform.system() == "Darwin":
        # Create a solid colour image
        colour = key
        width, height = 60, 18
        button_images[key] = ImageTk.PhotoImage(Image.new("RGB", (width, height), colour))
        # Create a button with the solid colour image
        but = tk.Button(frame2, image=button_images[key], width=width, height=height, command=lambda key=key: on_colour_button_click(key))
    else:
        # Create a button with a coloured background
        but = tk.Button(frame2, bg=key, width=5, command=lambda key=key: on_colour_button_click(key))
    row = index // 6 + 1
    col = index % 6
    but.grid(row=row, column=col, padx=2, pady=2)

name_cb = tk.Checkbutton(frame2, text="Name by size/colour", variable=name_var)
name_cb.grid(row=5, column=0, columnspan=3, sticky="w")

# frame 3 - other buttons
hide_bbox_b = tk.Button(frame3,
                        text=" Hide boxes ",
                        command=lambda: on_show_hide_button_click("off")
                        )
show_bbox_b = tk.Button(frame3,
                        text=" Show boxes ",
                        command=lambda: on_show_hide_button_click("on")
                        )
remove_bbox_b = tk.Button(frame3, text="Remove boxes", command=on_remove)
clear_clip_b = tk.Button(frame3, text="Clear clipboard", command=on_clear_button_click)
hide_bbox_b.grid(row=0, column=0, padx=2, pady=4)
show_bbox_b.grid(row=0, column=1, padx=2, pady=4)
remove_bbox_b.grid(row=0, column=2, padx=2, pady=4)
clear_clip_b.grid(row=1, column=0, columnspan=2, padx=2, pady=4, sticky="w")

# frame 4 - messages as text box
message_tb = tk.Text(frame4, height=5, width=38, bg="#ffede0")
message_tb.insert("1.0", my_message.get())
message_tb.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

gui.config(menu=menubar)
gui.mainloop()
