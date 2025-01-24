from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile
from tkinter.filedialog import askopenfile
import re
import traceback
from PIL import ImageTk, Image
import terragen_rpc as tg

gui = Tk()
gui.title("tg_crop_region_presets")
gui.geometry("360x440")
gui.config(bg="#89B2B9")

frame0 = LabelFrame(gui,relief=FLAT,bg="#B8DBD0")
bottom_frame = LabelFrame(gui,bg="#FDEDEC")
frame0.grid(row=0,column=0,sticky="WENS",padx=5,pady=5)
bottom_frame.grid(row=2,column=0,sticky="WENS",padx=5,pady=2)

notebook = ttk.Notebook(bottom_frame)
notebook.grid(row=0,column=0)

tab1 = Frame(notebook,padx=10,bg="#947A66")
tab2 = Frame(notebook,padx=10,bg="#947A66")
tab3 = Frame(notebook,padx=10,bg="#947A66")
tab4 = Frame(notebook,padx=10,bg="#947A66")
tab5 = Frame(notebook,padx=10,bg="#947A66")
tab6 = Frame(notebook,padx=10,bg="#947A66")
notebook.add(tab1, text="Halves")
notebook.add(tab2, text="Thirds")
notebook.add(tab3, text="Quarters")
notebook.add(tab4, text="Ninths")
notebook.add(tab5, text="Sixtenths")
notebook.add(tab6, text="Custom")

def popup_info(message_title,message_description):
    messagebox.showinfo(title=message_title,message=message_description)

def popup_warning(message_title,message_description):
    messagebox.showwarning(title = message_title,message = message_description)

def get_renderers(): # returns list of renderer paths
    node_ids = []
    node_paths = []
    try:
        project = tg.root()
        node_ids = tg.children_filtered_by_class(project,'render')
        for nodes in node_ids:
            node_paths.append(tg.path(nodes))
        return(node_paths)
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())

def update_combobox_renderers():
    try:
        current_renderer_paths = get_renderers()
        selected_renderer_cb.set('') # clears the selected value, ensures nothing is displayed
        selected_renderer_cb["values"] = current_renderer_paths
        if len(current_renderer_paths) > 0:
            selected_renderer_cb.current(0) 
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())

def copy_crop_params(x): # gets current tg crop values as list, converts it to tuple, stores it in dict, redraws custom button
    screen_percents = [0.0 ,1.0 , 0.0, 1.0] # TG defaults
    renderer = tg.node_by_path(selected_render_node.get())
    screen_percents[0] = renderer.get_param_as_float("crop_left")
    screen_percents[1] = renderer.get_param_as_float("crop_right")
    screen_percents[2] = renderer.get_param_as_float("crop_bottom")
    screen_percents[3] = renderer.get_param_as_float("crop_top")
    screen_percents_tuple = tuple(screen_percents)
    crop_presets[x] = screen_percents_tuple # update the custom dictionary values 40 - 43 
    refresh_canvas(x,screen_percents_tuple) # redraw the custom button with crop region

def crop(x):
    percents = crop_presets[x]
    set_crop_region(percents)

def set_crop_region(y):
    try:
        renderer = tg.node_by_path(selected_render_node.get())
        if renderer:
            renderer.set_param("crop_left",y[0])
            renderer.set_param("crop_right",y[1])
            renderer.set_param("crop_bottom",y[2])
            renderer.set_param("crop_top",y[3])
        else:
            popup_warning("Terragen Warning","Selected renderer is no longer in project. \nRefresh list. \n")
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())

def crop_enable():
    try:
        renderer = tg.node_by_path(selected_render_node.get())
        if enable_on_off.get():        
            renderer.set_param("do_crop_region",1)
        else:
            renderer.set_param("do_crop_region",0)
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())

def save_custom_crops_to_disk():
    x = str(get_custom_crops_from_dict()) # forcing a string to file
    my_filetypes = [("Text document","*.txt"),("All files","*.*")]
    file = asksaveasfile(filetypes= my_filetypes, defaultextension=my_filetypes)        
    file.write(x)
    file.close()

def load_custom_crops_from_disk(): # loads saved presets from disk or set of default values
    custom_presets_from_disk = read_from_file()
    formatted_custom_presets = format_custom_presets_from_disk(custom_presets_from_disk)
    update_custom_crops_dict(formatted_custom_presets)    
    draw_on_canvas = [40,41,42,43] # upate the custom canvases
    for key in draw_on_canvas:
        crops = crop_presets[key]
        refresh_canvas(key,crops)

def format_custom_presets_from_disk(presets):
    converted_string = str(presets)
    pattern = r"\(.*?\)"
    matches = re.findall(pattern,converted_string)
    extracted_elements = [eval(match) for match in matches]    
    return extracted_elements

def get_custom_crops_from_dict():
    custom_crop_keys = [40, 41, 42, 43]
    custom_crop_presets = []
    for key in custom_crop_keys:
        custom_crop_presets.append(crop_presets[key])
    return (custom_crop_presets)

def display_dict_values():    
    text = "Custom 1: " + str(crop_presets[40]) +"\nCustom 2: " + str(crop_presets[41]) + "\nCustom 3:" + str(crop_presets[42]) +"\nCustom 4:" + str(crop_presets[43])
    popup_info("Custom crop presets",text)

def read_from_file():  # returns string of four presets from disk or a set of defaults
    content = "[(0.05, 0.6, 0.4, 0.7), (0.6, 0.97, 0.2, 0.78), (0.4, 0.6, 0.08, 0.36), (0.05, 0.28, 0.1, 0.95)]"
    my_filetypes = [("Text document","*.txt"),("All files","*.*")]
    file = askopenfile(mode='r',filetypes= my_filetypes)
    if file:
        content = file.read()
        file.close()
    return content

def update_custom_crops_dict(y):  
    crop_presets[40] = y[0]
    crop_presets[41] = y[1]
    crop_presets[42] = y[2]
    crop_presets[43] = y[3]    

def popup_add_renderer(message_type,message_description):
    user_choice = messagebox.askyesno(title = message_type,message=message_description)
    if user_choice:
        add_renderer()

def add_renderer():
    try:
        project = tg.root()
        tg.create_child(project,'render')
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())

def popup_help_file_menu():
    text = "Open custom crop presets: Replaces the 4 user-defined crop settings with values loaded from a file. \nSave custom crop presets: Saves the 4 user-defined custom crop preset values to a file."
    popup_info("Help for File menu", text)

def popup_help_presets_menu():
    text = "Select a drop-down option to set the crop region.  This an alterntive method to using the buttons and tabs below."
    popup_info("Help for Utility menu",text)

def popup_help_custom_menu():
    text = "Apply preset 1 - 4: Select an option to set the crop region to one of four user-defined presets.  \nCopy to custom 1 - 4: Saves the current crop region for the selected Renderer to the selected buffer in memory. \nDisplay custom presets: Displays the numerical values for the four custom crop regions."
    popup_info("Help for Custom menu",text)

def popup_help_utility_menu():
    text = "Add renderer: Simply adds a renderer to the project. \nRefresh list: Updates the drop-down list of renderers in the project."
    popup_info("Help for Utility menu",text)

def refresh_canvas(custom_preset_index,screen_percents_tuple): # passed custom preset number and tg unmodified crop region values in a tuple    
    # TG uses 0 for bottom and 1 for top, while tkinter is opposite. Invert y values with 1 - y value.
    canvas_width = 64
    canvas_height = 36    
    x1 = int(screen_percents_tuple[0] * canvas_width)
    x2 = int(screen_percents_tuple[1] * canvas_width)
    y1 = int((1 - screen_percents_tuple[2]) * canvas_height)
    y2 = int((1 - screen_percents_tuple[3]) * canvas_height)    

    if custom_preset_index == 40:
        canvas40.delete("all")
        canvas40.create_rectangle(x1,y1,x2,y2,fill="magenta")
    elif custom_preset_index == 41:
        canvas41.delete("all")
        canvas41.create_rectangle(x1,y1,x2,y2,fill="magenta")
    elif custom_preset_index == 42:
        canvas42.delete("all")
        canvas42.create_rectangle(x1,y1,x2,y2,fill="magenta")
    elif custom_preset_index == 43:
        canvas43.delete("all")
        canvas43.create_rectangle(x1,y1,x2,y2,fill="magenta")

# presets for crop regions halves, thirds, quarters, ninths, sixteenths, the last four are the custom presets
crop_presets = {
    0: (0.0, 1.0, 0.0, 1.0),
    1: (0.0, 0.5, 0.0, 1.0),
    2: (0.5, 1.0, 0.0, 1.0),
    3: (0.0, 1.0, 0.5, 1.0),
    4: (0.0, 1.0, 0.0, 0.5),
    5: (0.0, 1.0, 0.666667, 1.0),
    6: (0.0, 1.0, 0.333333, 0.666667),
    7: (0.0, 1.0, 0.0, 0.333333),
    8: (0.0, 0.333333, 0.0, 1.0),
    9: (0.333333, 0.666667, 0.0, 1.0),
    10: (0.666667, 1.0, 0.0, 1.0),
    11: (0.0, 0.5, 0.5, 1.0),    
    12: (0.5, 1.0, 0.5, 1.0),
    13: (0.0, 0.5, 0.0, 0.5),
    14: (0.5, 1.0, 0.0, 0.5),
    15: (0.0, 0.333333, 0.666667, 1.0),
    16: (0.333333, 0.666667, 0.666667, 1.0),
    17: (0.666667, 1.0, 0.666667, 1.0),
    18: (0.0, 0.333333, 0.333333, 0.666667),
    19: (0.333333, 0.666667, 0.333333, 0.666667),
    20: (0.666667, 1.0, 0.333333, 0.666667),
    21: (0.0, 0.333333, 0.0, 0.333333),
    22: (0.333333, 0.666667, 0.0, 0.333333),
    23: (0.666667, 1.0, 0.0, 0.333333),
    24: (0.0, 0.25, 0.75, 1.0),
    25: (0.25, 0.5, 0.75, 1.0),
    26: (0.5, 0.75, 0.75, 1.0),
    27: (0.75, 1.0, 0.75, 1.0),
    28: (0.0, 0.25, 0.5, 0.75),
    29: (0.25, 0.5, 0.5, 0.75),
    30: (0.5, 0.75, 0.5, 0.75),
    31: (0.75, 1.0, 0.5, 0.75),
    32: (0.0, 0.25, 0.25, 0.5),
    33: (0.25, 0.5, 0.25, 0.5),
    34: (0.5, 0.75, 0.25, 0.5),
    35: (0.75, 1.0, 0.25, 0.5),
    36: (0.0, 0.25, 0.0, 0.25),
    37: (0.25, 0.5, 0.0, 0.25),
    38: (0.5, 0.75, 0.0, 0.25),
    39: (0.75, 1.0, 0.0, 0.25),
    40: (0.05, 0.6, 0.4, 0.7),
    41: (0.6, 0.97, 0.2, 0.78),
    42: (0.4, 0.6, 0.08, 0.36),
    43: (0.05, 0.28, 0.1, 0.95)
}

# use a dictionary to store the image names
image_paths = {
    "thumbnail_0": "images/crop_0.bmp",
    "thumbnail_1": "images/crop_1.bmp",
    "thumbnail_2": "images/crop_2.bmp",
    "thumbnail_3": "images/crop_3.bmp",
    "thumbnail_4": "images/crop_4.bmp",
    "thumbnail_5": "images/crop_5.bmp",
    "thumbnail_6": "images/crop_6.bmp",
    "thumbnail_7": "images/crop_7.bmp",
    "thumbnail_8": "images/crop_8.bmp",
    "thumbnail_9": "images/crop_9.bmp",
    "thumbnail_10": "images/crop_10.bmp",
    "thumbnail_11": "images/crop_11.bmp",
    "thumbnail_12": "images/crop_12.bmp",
    "thumbnail_13": "images/crop_13.bmp",
    "thumbnail_14": "images/crop_14.bmp",
    "thumbnail_15": "images/crop_15.bmp",
    "thumbnail_16": "images/crop_16.bmp",
    "thumbnail_17": "images/crop_17.bmp",
    "thumbnail_18": "images/crop_18.bmp",
    "thumbnail_19": "images/crop_19.bmp",
    "thumbnail_20": "images/crop_20.bmp",
    "thumbnail_21": "images/crop_21.bmp",
    "thumbnail_22": "images/crop_22.bmp",
    "thumbnail_23": "images/crop_23.bmp",
    "thumbnail_24": "images/crop_24.bmp",
    "thumbnail_25": "images/crop_25.bmp",
    "thumbnail_26": "images/crop_26.bmp",
    "thumbnail_27": "images/crop_27.bmp",
    "thumbnail_28": "images/crop_28.bmp",
    "thumbnail_29": "images/crop_29.bmp",
    "thumbnail_30": "images/crop_30.bmp",
    "thumbnail_31": "images/crop_31.bmp",
    "thumbnail_32": "images/crop_32.bmp",
    "thumbnail_33": "images/crop_33.bmp",
    "thumbnail_34": "images/crop_34.bmp",
    "thumbnail_35": "images/crop_35.bmp",
    "thumbnail_36": "images/crop_36.bmp",
    "thumbnail_37": "images/crop_37.bmp",
    "thumbnail_38": "images/crop_38.bmp",
    "thumbnail_39": "images/crop_39.bmp",
    "thumbnail_40": "images/crop_40.bmp",
    "thumbnail_41": "images/crop_41.bmp",
    "thumbnail_42": "images/crop_42.bmp",
    "thumbnail_43": "images/crop_43.bmp",
}

# tkinter variables
enable_on_off = IntVar()
custom_preset1 = StringVar()
custom_preset2 = StringVar()
custom_preset3 = StringVar()
custom_preset4 = StringVar()
custom_preset1.set("0.05, 0.6, 0.4, 0.7")
custom_preset2.set("0.6, 0.97, 0.2, 0.78")
custom_preset3.set("0.4, 0.6, 0.08, 0.36")
custom_preset4.set("0.05, 0.28, 0.1, 0.95")
selected_render_node= StringVar()
custom_preset1_x1 = DoubleVar()
custom_preset1_x2 = DoubleVar()
custom_preset1_y1 = DoubleVar()
custom_preset1_y2 = DoubleVar()
custom_preset2_x1 = DoubleVar()
custom_preset2_x2 = DoubleVar()
custom_preset2_y1 = DoubleVar()
custom_preset2_y2 = DoubleVar()
custom_preset3_x1 = DoubleVar()
custom_preset3_x2 = DoubleVar()
custom_preset3_y1 = DoubleVar()
custom_preset3_y2 = DoubleVar()
custom_preset4_x1 = DoubleVar()
custom_preset4_x2 = DoubleVar()
custom_preset4_y1 = DoubleVar()
custom_preset4_y2 = DoubleVar()

# menu bar
menubar = Menu(gui)
filemenu = Menu(menubar,tearoff=0)
filemenu.add_command(label="Open custom crop presets...",command=load_custom_crops_from_disk)
filemenu.add_command(label="Save custom crop presets...",command = save_custom_crops_to_disk)
menubar.add_cascade(label="File",menu=filemenu)

presetmenu = Menu(menubar,tearoff=0)
presets_half = Menu(presetmenu,tearoff=0)
menubar.add_cascade(label="Presets",menu=presetmenu)
presetmenu.add_cascade(label="Half",menu=presets_half)
presets_half.add_command(label="Horz T",command=lambda: crop(3))
presets_half.add_command(label="Horz B",command=lambda: crop(4))
presets_half.add_command(label="Vert L",command=lambda: crop(1))
presets_half.add_command(label="Vert R",command=lambda: crop(2))

presets_third = Menu(presetmenu,tearoff=0)
presetmenu.add_cascade(label="Thirds",menu=presets_third)
presets_third.add_command(label="Horz T",command=lambda: crop(5))
presets_third.add_command(label="Horz M",command=lambda: crop(6))
presets_third.add_command(label="Horz B",command=lambda: crop(7))
presets_third.add_command(label="Vert L",command=lambda: crop(8))
presets_third.add_command(label="Vert M",command=lambda: crop(9))
presets_third.add_command(label="Vert R",command=lambda: crop(10))

presets_quarter = Menu(presetmenu,tearoff=0)
presetmenu.add_cascade(label="Quarter",menu=presets_quarter)
presets_quarter.add_command(label="Top L",command=lambda: crop(11))
presets_quarter.add_command(label="Top R",command=lambda: crop(12))
presets_quarter.add_command(label="Bot L",command=lambda: crop(13))
presets_quarter.add_command(label="Bot R",command=lambda: crop(14))

presets_ninth = Menu(presetmenu,tearoff=0)
presetmenu.add_cascade(label="Ninths",menu=presets_ninth)
presets_ninth.add_command(label="Top L",command=lambda: crop(15))
presets_ninth.add_command(label="Top M",command=lambda: crop(16))
presets_ninth.add_command(label="Top R",command=lambda: crop(17))
presets_ninth.add_command(label="Mid L",command=lambda: crop(18))
presets_ninth.add_command(label="Mid M",command=lambda: crop(19))
presets_ninth.add_command(label="Mid B",command=lambda: crop(20))
presets_ninth.add_command(label="Bot L",command=lambda: crop(21))
presets_ninth.add_command(label="Bot M",command=lambda: crop(22))
presets_ninth.add_command(label="Bot R",command=lambda: crop(23))

presets_sixtenth = Menu(presetmenu,tearoff=0)
presetmenu.add_cascade(label="Sixtenth",menu=presets_sixtenth)
presets_sixtenth.add_command(label="Row1 A",command=lambda: crop(24))
presets_sixtenth.add_command(label="Row1 B",command=lambda: crop(25))
presets_sixtenth.add_command(label="Row1 C",command=lambda: crop(26))
presets_sixtenth.add_command(label="Row1 D",command=lambda: crop(27))
presets_sixtenth.add_command(label="Row2 A",command=lambda: crop(28))
presets_sixtenth.add_command(label="Row2 B",command=lambda: crop(29))
presets_sixtenth.add_command(label="Row2 C",command=lambda: crop(30))
presets_sixtenth.add_command(label="Row2 D",command=lambda: crop(31))
presets_sixtenth.add_command(label="Row3 A",command=lambda: crop(32))
presets_sixtenth.add_command(label="Row3 B",command=lambda: crop(33))
presets_sixtenth.add_command(label="Row3 C",command=lambda: crop(34))
presets_sixtenth.add_command(label="Row3 D",command=lambda: crop(35))
presets_sixtenth.add_command(label="Row4 A",command=lambda: crop(36))
presets_sixtenth.add_command(label="Row4 B",command=lambda: crop(37))
presets_sixtenth.add_command(label="Row4 C",command=lambda: crop(38))
presets_sixtenth.add_command(label="Row4 D",command=lambda: crop(39))

custommenu = Menu(menubar,tearoff=0)
custommenu.add_command(label = "Apply preset 1",command=lambda: crop(40))
custommenu.add_command(label = "Apply preset 2",command=lambda: crop(41))
custommenu.add_command(label = "Apply preset 3",command=lambda: crop(42))
custommenu.add_command(label = "Apply preset 4",command=lambda: crop(43))
custommenu.add_separator()
custommenu.add_command(label = "Copy to custom 1",command=lambda:copy_crop_params(40))
custommenu.add_command(label = "Copy to custom 2",command=lambda:copy_crop_params(41))
custommenu.add_command(label = "Copy to custom 3",command=lambda:copy_crop_params(42))
custommenu.add_command(label = "Copy to custom 4",command=lambda:copy_crop_params(43))
custommenu.add_separator()
custommenu.add_command(label = "Display custom presets", command=display_dict_values)
menubar.add_cascade(label="Custom",menu=custommenu)

utilitymenu = Menu(menubar,tearoff=0)
utilitymenu.add_command(label = "Add renderer",command=add_renderer)
utilitymenu.add_command(label="Refresh list",command=update_combobox_renderers)
menubar.add_cascade(label="Utility",menu=utilitymenu)

helpmenu = Menu(menubar,tearoff=0)
helpmenu.add_command(label="For file menu",command=popup_help_file_menu)
helpmenu.add_command(label="For preset menu",command=popup_help_presets_menu)
helpmenu.add_command(label="For custom menu",command=popup_help_custom_menu)
helpmenu.add_command(label="For utility menu",command=popup_help_utility_menu)
menubar.add_cascade(label="Help",menu=helpmenu)

# main
renderer_paths = get_renderers() # get the paths for all render nodes in the project
if not renderer_paths:
    popup_add_renderer("Add Renderer","Add render node to project?")
    renderer_paths = get_renderers()
    if not renderer_paths:
        quit()

# get thumbnail images
images = {} # init image dict
for name, path in image_paths.items():
    img = Image.open(path)
    images[name] = ImageTk.PhotoImage(img)

# checkbox and combobox
enable = Checkbutton(frame0,text="Enable crop region",bg="#B8DBD0",variable=enable_on_off,onvalue=1,offvalue=0,command=crop_enable).grid(row=0,column=1)

selected_renderer_cb = ttk.Combobox(frame0,textvariable=selected_render_node,state="readonly")
selected_renderer_cb["values"] = renderer_paths
if len(renderer_paths) > 0:
    selected_renderer_cb.current(0)
selected_renderer_cb.grid(row=0,column=0)

# upper buttons
b0 = Button(frame0,text="Reset",image=images["thumbnail_0"],compound=TOP,command=lambda: crop(0))
b0.grid(row=0,column=2,padx=2,pady=4)
refresh_button = Button(frame0,text="Refresh list",command=update_combobox_renderers)
refresh_button.grid(row=1,column=2,pady=4)
# halve buttons
b1 = Button(tab1,text="Vert L",image=images["thumbnail_1"],compound=TOP,command=lambda: crop(1))
b1.grid(row=0,column=2,padx=4,pady=10)
b2 = Button(tab1,text="Vert R",image=images["thumbnail_2"],compound=TOP,command=lambda: crop(2))
b2.grid(row=0,column=3,padx=4,pady=10)
b3 = Button(tab1,text="Horz T",image=images["thumbnail_3"],compound=TOP,command=lambda: crop(3))
b3.grid(row=0,column=0,padx=4,pady=10)
b4 = Button(tab1,text="Horz B",image=images["thumbnail_4"],compound=TOP,command=lambda: crop(4))
b4.grid(row=0,column=1,padx=4,pady=10)
# third buttons
b5 = Button(tab2,text="Horz T",image=images["thumbnail_5"],compound=TOP,command=lambda: crop(5))
b5.grid(row=0,column=0,padx=4,pady=10)
b6 = Button(tab2,text="Horz M",image=images["thumbnail_6"],compound=TOP,command=lambda: crop(6))
b6.grid(row=0,column=1,padx=4,pady=10)
b7 = Button(tab2,text="Horz B",image=images["thumbnail_7"],compound=TOP,command=lambda: crop(7))
b7.grid(row=0,column=2,padx=4,pady=10)
b8 = Button(tab2,text="Vert L",image=images["thumbnail_8"],compound=TOP,command=lambda: crop(8))
b8.grid(row=1,column=0,padx=4,pady=2)
b9 = Button(tab2,text="Vert M",image=images["thumbnail_9"],compound=TOP,command=lambda: crop(9))
b9.grid(row=1,column=1,padx=4,pady=2)
b10 = Button(tab2,text="Vert R",image=images["thumbnail_10"],compound=TOP,command=lambda: crop(10))
b10.grid(row=1,column=2,padx=4,pady=2)
# quarter buttons
b11 = Button(tab3,text="Top L ",image=images["thumbnail_11"],compound=TOP,command=lambda: crop(11))
b11.grid(row=0,column=0,padx=4,pady=10)
b12 = Button(tab3,text="Top R ",image=images["thumbnail_12"],compound=TOP,command=lambda: crop(12))
b12.grid(row=0,column=1,padx=4,pady=10)
b13 = Button(tab3,text="Bot L ",image=images["thumbnail_13"],compound=TOP,command=lambda: crop(13))
b13.grid(row=0,column=2,padx=4,pady=10)
b14 = Button(tab3,text="Bot R ",image=images["thumbnail_14"],compound=TOP,command=lambda: crop(14))
b14.grid(row=0,column=3,padx=4,pady=10)
# ninth buttons
b15 = Button(tab4,text="Top L",image=images["thumbnail_15"],compound=TOP,command=lambda: crop(15))
b15.grid(row=0,column=0,padx=4,pady=10)
b16 = Button(tab4,text="Top M",image=images["thumbnail_16"],compound=TOP,command=lambda: crop(16))
b16.grid(row=0,column=1,padx=4,pady=10)
b17 = Button(tab4,text="Top R",image=images["thumbnail_17"],compound=TOP,command=lambda: crop(17))
b17.grid(row=0,column=2,padx=4,pady=10)
b18 = Button(tab4,text="Mid L",image=images["thumbnail_18"],compound=TOP,command=lambda: crop(18))
b18.grid(row=1,column=0,padx=4,pady=2)
b19 = Button(tab4,text="Mid M",image=images["thumbnail_19"],compound=TOP,command=lambda: crop(19))
b19.grid(row=1,column=1,padx=4,pady=2)
b20 = Button(tab4,text="Mid R",image=images["thumbnail_20"],compound=TOP,command=lambda: crop(20))
b20.grid(row=1,column=2,padx=4,pady=2)
b21 = Button(tab4,text="Bot L",image=images["thumbnail_21"],compound=TOP,command=lambda: crop(21))
b21.grid(row=2,column=0,padx=4,pady=10)
b22 = Button(tab4,text="Bot M",image=images["thumbnail_22"],compound=TOP,command=lambda: crop(22))
b22.grid(row=2,column=1,padx=4,pady=10)
b23 = Button(tab4,text="Bot R",image=images["thumbnail_23"],compound=TOP,command=lambda: crop(23))
b23.grid(row=2,column=2,padx=4,pady=10)
# sixteenth buttons
b24 = Button(tab5,text="Row1 A",image=images["thumbnail_24"],compound=TOP,command=lambda: crop(24))
b24.grid(row=0,column=0,padx=4,pady=4)
b25 = Button(tab5,text="Row1 B",image=images["thumbnail_25"],compound=TOP,command=lambda: crop(25))
b25.grid(row=0,column=1,padx=4,pady=4)
b26 = Button(tab5,text="Row1 C",image=images["thumbnail_26"],compound=TOP,command=lambda: crop(26))
b26.grid(row=0,column=2,padx=4,pady=4)
b27 = Button(tab5,text="Row1 D",image=images["thumbnail_27"],compound=TOP,command=lambda: crop(27))
b27.grid(row=0,column=3,padx=4,pady=4)
b28 = Button(tab5,text="Row2 A",image=images["thumbnail_28"],compound=TOP,command=lambda: crop(28))
b28.grid(row=1,column=0,padx=4,pady=4)
b29 = Button(tab5,text="Row2 B",image=images["thumbnail_29"],compound=TOP,command=lambda: crop(29))
b29.grid(row=1,column=1,padx=4,pady=4)
b30 = Button(tab5,text="Row2 C",image=images["thumbnail_30"],compound=TOP,command=lambda: crop(30))
b30.grid(row=1,column=2,padx=4,pady=4)
b31 = Button(tab5,text="Row2 D",image=images["thumbnail_31"],compound=TOP,command=lambda: crop(31))
b31.grid(row=1,column=3,padx=4,pady=4)
b32 = Button(tab5,text="Row3 A",image=images["thumbnail_32"],compound=TOP,command=lambda: crop(32))
b32.grid(row=2,column=0,padx=4,pady=4)
b33 = Button(tab5,text="Row3 B",image=images["thumbnail_33"],compound=TOP,command=lambda: crop(33))
b33.grid(row=2,column=1,padx=4,pady=4)
b34 = Button(tab5,text="Row3 C",image=images["thumbnail_34"],compound=TOP,command=lambda: crop(34))
b34.grid(row=2,column=2,padx=4,pady=4)
b35 = Button(tab5,text="Row3 D",image=images["thumbnail_35"],compound=TOP,command=lambda: crop(35))
b35.grid(row=2,column=3,padx=4,pady=4)
b36 = Button(tab5,text="Row4 A",image=images["thumbnail_36"],compound=TOP,command=lambda: crop(36))
b36.grid(row=3,column=0,padx=4,pady=4)
b37 = Button(tab5,text="Row4 B",image=images["thumbnail_37"],compound=TOP,command=lambda: crop(37))
b37.grid(row=3,column=1,padx=4,pady=4)
b38 = Button(tab5,text="Row4 C",image=images["thumbnail_38"],compound=TOP,command=lambda: crop(38))
b38.grid(row=3,column=2,padx=4,pady=4)
b39 = Button(tab5,text="Row4 D",image=images["thumbnail_39"],compound=TOP,command=lambda: crop(39))
b39.grid(row=3,column=3,padx=4,pady=4)

# custom tab - buttons and labels
custom_label3 = Label(tab6,text="Click to APPLY preset to Terragen crop region.",bg="#947A66",fg="#FFFFFF")
custom_label3.grid(row=0,column=0,columnspan=4,padx=2,pady=6,sticky="w")

custom_label2 = Label(tab6,text="Click to COPY Terragen crop region to preset.",bg="#947A66",fg="#FFFFFF")
custom_label2.grid(row=6,column=0,columnspan=4,padx=2,sticky="w")

# empty rows
custom_label5 = Label(tab6,text=" ",bg="#947A66")
custom_label5.grid(row=5,column=0)

b40 = Button(tab6,text="Apply 1",command=lambda: crop(40))
b40.grid(row=4,column=0,padx=4,pady=6)
b41 = Button(tab6,text="Apply 2",command=lambda: crop(41))
b41.grid(row=4,column=1,padx=4,pady=6)
b42 = Button(tab6,text="Apply 3",command=lambda: crop(42))
b42.grid(row=4,column=2,padx=4,pady=6)
b43 = Button(tab6,text="Apply 4",command=lambda: crop(43))
b43.grid(row=4,column=3,padx=4,pady=6)

# copy custom crop buttons
copy1 = Button(tab6,text="Copy 1",bg='#DAF0DE',command=lambda: copy_crop_params(40))
copy2 = Button(tab6,text="Copy 2",bg='#DAF0DE',command=lambda: copy_crop_params(41))
copy3 = Button(tab6,text="Copy 3",bg='#DAF0DE',command=lambda: copy_crop_params(42))
copy4 = Button(tab6,text="Copy 4",bg='#DAF0DE',command=lambda: copy_crop_params(43))
copy1.grid(row=7,column=0,padx=4,pady=4)
copy2.grid(row=7,column=1,padx=4,pady=4)
copy3.grid(row=7,column=2,padx=4,pady=4)
copy4.grid(row=7,column=3,padx=4,pady=4)

# canvas to draw custom crop regions on 
canvas40 = Canvas(tab6,width=64,height=36,bg='black')
canvas40.grid(row=1,column=0,padx=4)
canvas41 = Canvas(tab6,width=64,height=36,bg='black')
canvas41.grid(row=1,column=1,padx=4)
canvas42 = Canvas(tab6,width=64,height=36,bg='black')
canvas42.grid(row=1,column=2,padx=4)
canvas43 = Canvas(tab6,width=64,height=36,bg='black')
canvas43.grid(row=1,column=3,padx=4)

# draw custom crop proxies - creates magenta rectangle on canvas
draw_on_canvas = [40,41,42,43]
for key in draw_on_canvas: # call refresh_canvas for each button 40-43
    crops = crop_presets[key]    
    refresh_canvas(key,crops)

gui.config(menu=menubar)
gui.mainloop()