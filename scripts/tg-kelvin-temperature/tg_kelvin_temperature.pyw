from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import traceback
import terragen_rpc as tg

gui = Tk()
gui.title("tg_kelvin_temperature")
gui.geometry("525x250")
gui.config(bg="#89B2B9") # dark green colour

gui.rowconfigure(0,weight=2)
gui.rowconfigure(1,weight=1)
gui.columnconfigure(0,weight=1)
gui.columnconfigure(1,weight=2)

frame0 = LabelFrame(gui,relief=FLAT,bg="#B8DBD0")
frame1 = LabelFrame(gui,relief=FLAT,bg="#CBAE98")
frame2 = LabelFrame(gui,relief=FLAT,bg="#B8DBD0")
frame3 = LabelFrame(gui,relief=FLAT,bg="#CBAE98")
frame0.grid(row=0,column=0,sticky="WENS",padx=3)
frame1.grid(row=0,column=1,sticky="WENS",padx=3)
frame2.grid(row=1,column=0,sticky="WENS",padx=3)
frame3.grid(row=1,column=1,sticky="WENS",padx=3)

def load_image(image_path):
    if os.path.exists(image_path):
        return Image.open(image_path)
    else:
        return None

image_path = "images/tg_kelvin_colours.gif"
image_open = load_image(image_path)
if image_open:
    image1 = ImageTk.PhotoImage(image_open)

# The rest of the code will go here

def get_sunlight_nodes_in_project():
    try:
        project = tg.root()
        return get_sunlight_nodes_in_node(project)
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
        return([])
    except TimeoutError as e:        
        popup_warning("Terragen RPC timeout error",str(e))
        return([])
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
        return([])
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())
        return([])

def get_sunlight_nodes_in_node(in_node):
    # returns a list of sunlight node paths. Lists could be empty if no sunlight nodes exist.
    try:
        node_paths = []
        all_children = in_node.children()
        sunlight_children = in_node.children_filtered_by_class("sunlight")
        for child in sunlight_children:
            node_paths.append(child.path())
        if recursive_search.get():
            for child in all_children:
                deeper_paths = get_sunlight_nodes_in_node(child)
                node_paths.extend(deeper_paths)
        return node_paths
    
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
        return([])
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
        return([])
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
        return([])
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())
        return([])

def refresh():    
    global sunlight_paths
    sunlight_paths = get_sunlight_nodes_in_project()
    sunlight_combobox.set('') # clears the selected value, ensures nothing is displayed
    sunlight_combobox["values"] = sunlight_paths
    if len(sunlight_paths) > 0:
        sunlight_combobox.current(0)

def apply_kelvin():
    kelvin_as_srgb = kelvin_table[kelvin.get()] # returns tuple from dictionary
    kelvin_as_decimal = srgb_to_decimal(kelvin_as_srgb) # decimal as a list
    set_sunlight_node_in_project(kelvin_as_decimal)

def srgb_to_decimal(sRGB):
    srgb_list = []
    for i in range(len(sRGB)):
        srgb_list.append(pow(sRGB[i]/255,2.2))
    srgb_list_to_tuple = tuple(srgb_list)
    return srgb_list_to_tuple

def set_sunlight_node_in_project(kelvin_decimal):
    index = sunlight_combobox.current()
    if index < 0:
        popup_warning("TclError","No Sunlight nodes in project. \nAdd Sunlight node and refresh list. \n")
        return
    try:
        node = tg.node_by_path(sunlight_paths[index])
        if node:
            node.set_param('colour',kelvin_decimal)
        else:
            popup_warning("Terragen Warning","Selected Sunlight node no longer in project. \nRefresh list. \n")
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())

def popup_warning(message_title,message_description):
    messagebox.showwarning(title = message_title,message = message_description)

# dictionary
kelvin_table = {
    1000: (255, 56, 0),
    1100: (255, 71, 0),
    1200: (255, 83, 0),
    1300: (255, 93, 0),
    1400: (255, 101, 0),
    1500: (255, 109, 0),
    1600: (255, 115, 0),
    1700: (255, 121, 0),
    1800: (255, 126, 0),
    1900: (255, 131, 0),
    2000: (255, 138, 18),
    2100: (255, 142, 33),
    2200: (255, 147, 44),
    2300: (255, 152, 54),
    2400: (255, 157, 63),
    2500: (255, 161, 72),
    2600: (255, 165, 79),
    2700: (255, 169, 87),
    2800: (255, 173, 94),
    2900: (255, 177, 101),
    3000: (255, 180, 107),
    3100: (255, 184, 114),
    3200: (255, 187, 120),
    3300: (255, 190, 126),
    3400: (255, 193, 132),
    3500: (255, 196, 137),
    3600: (255, 199, 143),
    3700: (255, 201, 148),
    3800: (255, 204, 153),
    3900: (255, 206, 159),
    4000: (255, 209, 163),
    4100: (255, 211, 168),
    4200: (255, 213, 173),
    4300: (255, 215, 177),
    4400: (255, 217, 182),
    4500: (255, 219, 186),
    4600: (255, 221, 190),
    4700: (255, 223, 194),
    4800: (255, 225, 198),
    4900: (255, 227, 202),
    5000: (255, 228, 206),
    5100: (255, 230, 210),
    5200: (255, 232, 213),
    5300: (255, 233, 217),
    5400: (255, 235, 220),
    5500: (255, 236, 224),
    5600: (255, 238, 227),
    5700: (255, 239, 230),
    5800: (255, 240, 233),
    5900: (255, 242, 236),
    6000: (255, 243, 239),
    6100: (255, 244, 242),
    6200: (255, 245, 245),
    6300: (255, 246, 247),
    6400: (255, 248, 251),
    6500: (255, 249, 253),
    6600: (254, 249, 255),
    6700: (252, 247, 255),
    6800: (249, 246, 255),
    6900: (247, 245, 255),
    7000: (245, 243, 255),
    7100: (243, 242, 255),
    7200: (240, 241, 255),
    7300: (239, 240, 255),
    7400: (237, 239, 255),
    7500: (235, 238, 255),
    7600: (233, 237, 255),
    7700: (231, 236, 255),
    7800: (230, 235, 255),
    7900: (228, 234, 255),
    8000: (227, 233, 255),
    8100: (225, 232, 255),
    8200: (224, 231, 255),
    8300: (222, 230, 255),
    8400: (221, 230, 255),
    8500: (220, 229, 255),
    8600: (218, 229, 255),
    8700: (217, 227, 255),
    8800: (216, 227, 255),
    8900: (215, 226, 255),
    9000: (214, 225, 255),
    9100: (212, 225, 255),
    9200: (211, 224, 255),
    9300: (210, 223, 255),
    9400: (209, 223, 255),
    9500: (208, 222, 255),
    9600: (207, 221, 255),
    9700: (207, 221, 255),
    9800: (206, 220, 255),
    9900: (205, 220, 255),
    10000: (207, 218, 255),
    10100: (207, 218, 255),
    10200: (206, 217, 255),
    10300: (205, 217, 255),
    10400: (204, 216, 255),
    10500: (204, 216, 255),
    10600: (203, 215, 255),
    10700: (202, 215, 255),
    10800: (202, 214, 255),
    10900: (201, 214, 255),
    11000: (200, 213, 255),
    11100: (200, 213, 255),
    11200: (199, 212, 255),
    11300: (198, 212, 255),
    11400: (198, 212, 255),
    11500: (197, 211, 255),
    11600: (197, 211, 255),
    11700: (197, 210, 255),
    11800: (196, 210, 255),
    11900: (195, 210, 255),
    12000: (195, 209, 255)}

# variables
recursive_search = BooleanVar()
selected_sunlight = StringVar()
kelvin = IntVar()

# main - get sunlight nodes in the project
sunlight_paths = get_sunlight_nodes_in_project()

# checkbox
recursive_checkbox = Checkbutton(frame0,text="Recursive search?",variable=recursive_search,bg="#B8DBD0",padx=10,pady=10)
recursive_checkbox.grid(row=0,column=0,sticky='w')

# text labels
text01 = Label(frame0,text='Select Sunlight node.',relief = FLAT,bg="#B8DBD0",padx=10,pady=10)
text02 = Label(frame2,text="Click button to refresh list.",relief=FLAT,bg="#B8DBD0",padx=10,pady=10)
text03 = Label(frame1,text="Select Kelvin temperature.",bg="#CBAE98",relief=FLAT,padx=10,pady=10)
text04 = Label(frame3,text="Click button to apply Kelvin temperature to selected sunlight.",relief=FLAT,bg="#CBAE98",padx=10,pady=10)
text01.grid(row=2,column=0,sticky='w')
text02.grid(row=0,column=0,sticky="w")
text03.grid(row=0,column=0,sticky="w")
text04.grid(row=0,column=0,sticky="w")

# bitmap image or text
if image_open:
    kelvin_image = Label(frame1,image=image1,background="#CBAE98")
    kelvin_image.grid(row=1,column=0,padx=10)
else:
    kelvin_image = Label(frame1,text="<-- 1000k warm colours, cool colours 12,000k -->",background="#CBAE98")
    kelvin_image.grid(row=1,column=0,padx=10)

# slider
kelvin_slider = Scale(frame1,from_ = 1000, to = 12000, variable =kelvin,orient=HORIZONTAL,showvalue =1,resolution=100,length=300,bg="#CBAE98",troughcolor="#B8DBD0",highlightthickness=0,highlightbackground="#CBAE98")
kelvin_slider.grid(row=6,column=0,sticky='w',padx=10)

# combobox
sunlight_combobox = ttk.Combobox(frame0,textvariable=selected_sunlight,state="readonly")
sunlight_combobox["values"] = sunlight_paths
if len(sunlight_paths) > 0:
    sunlight_combobox.current(0)
sunlight_combobox.grid(row=3,column=0,padx=10)

# buttons
refresh_button = Button(frame2,text="Refresh",command=refresh)
refresh_button.grid(row=2,column=0)
apply_button = Button(frame3,text="Apply Kelvin",bg='gold',command=apply_kelvin)
apply_button.grid(row=1,column=0)

# empty space
empty_row1 = Label(frame0,text=" ",bg="#B8D8D0")
empty_row2 = Label(frame1,text=" ",bg="#CBAE98")
empty_row1.grid(row=1)
empty_row2.grid(row=2)

# Keep the following line at the very end of the program
gui.mainloop()
