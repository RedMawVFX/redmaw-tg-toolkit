import os.path
import platform
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile
from tkinter.filedialog import askopenfile
import re
import terragen_rpc as tg

def display_bookmarks():
    formatted_for_popup = format_bookmarks()
    popup_info("Current bookmark values",formatted_for_popup)

def format_bookmarks():
    formatted_text = ""
    for items in bookmarks:
        formatted_text  = formatted_text + str(items) + ' \n'
    return formatted_text

def reset_bookmarks():
    global bookmarks
    bookmarks = [(default_position,default_rotation,default_focal)] * 10
    my_messages.set("Bookmarks reset to default values.")

def reset_bookmarks_zero():
    global bookmarks
    zero = '0 0 0'
    bookmarks = [(zero,zero,default_focal)] * 10
    my_messages.set("Bookmarks rest to 0,0,0")

def popup_help_file_menu():
    text = "Open bookmarks: Replaces all existing bookmarks with values loaded from file. \nSave bookmarks: Saves all current bookmark values to a file."
    popup_info("Help for File menu", text)

def popup_help_utility_menu():
    text = "Display bookmarks: Displays the current values assigned to all the bookmarks. \nRest bookmarks: Resets all bookmarks to default render camera values. \nReset bookmarks to zero: Resets all bookmark postion and rotation values to zero."
    popup_info("Help for Utility menu",text)

gui = Tk()
gui.title(os.path.basename(__file__))
gui.geometry("692x500" if platform.system() == "Darwin" else
             "475x500")

gui.columnconfigure(0,weight=2)
gui.columnconfigure(1,weight=1)
gui.columnconfigure(2,weight=1)
gui.columnconfigure(3,weight=1)
gui.columnconfigure(4,weight=1)
gui.columnconfigure(5,weight=1)

gui.rowconfigure(0,weight=0)
gui.rowconfigure(1,weight=1)
gui.rowconfigure(2,weight=1)
gui.rowconfigure(3,weight=4)

frame1 = LabelFrame(gui,text="Select camera to copy bookmark from")
frame2 = LabelFrame(gui,text="Select camera to apply bookmark to")
frame3 = LabelFrame(gui,text="Messages:",bg="#FFF9EC",relief=FLAT)

frame1.grid(row=1, column=0,sticky="WENS",padx=10,pady=10)
frame2.grid(row=2, column=0,sticky="WENS",padx=10,pady=10)
frame3.grid(row=3,column=0,sticky="WENS",padx=10,pady=10)

error_table = {
1: "Terragen RPC connection error",
2: "Terragen RPC timeout error",
3: "Terragen RPC server reply error",
4: "Terragen RPC API error",
5: "Terragen RPC attribute error"
}

def get_cameras():
    try:
        project = tg.root()
        node_ids = tg.children_filtered_by_class(project,'camera')
        return node_ids
    except ConnectionError as e:
        popup_message(1,str(e))
    except TimeoutError as e:
        popup_message(2,str(e))
    except tg.ReplyError as e:
        popup_message(3,str(e))
    except tg.ApiError:
        popup_message(4,str(e))

def update_combobox_cameras():
    r = get_cameras()
    create_camera_dictionary(r)
    acquire_camera_cb["values"] = list(camera_dictionary.values())
    acquire_camera_cb.current(0)
    apply_camera_cb["values"] = list(camera_dictionary.values())
    apply_camera_cb.current(0)

def popup_info(message_title,message_description):
    messagebox.showinfo(title=message_title,message=message_description)

def popup_message(message_type,message_description):
    messagebox.showwarning(title=error_table[message_type], message = message_description)

def popup_add_camera(message_type,message_description):
    user_choice = messagebox.askyesno(title = message_type,message=message_description)
    if user_choice:
        add_camera()

def add_camera():
    try:
        project = tg.root()
        tg.create_child(project,'camera')
    except ConnectionError as e:
        popup_message(1,str(e))
    except TimeoutError as e:
        popup_message(2,str(e))
    except tg.ReplyError as e:
        popup_message(3,str(e))
    except tg.ApiError:
        popup_message(4,str(e))

def create_camera_dictionary(ids):
    camera_dictionary.clear()
    for nodes in ids:
        try:
            camera_dictionary[str(nodes)]= tg.name(nodes)
        except ConnectionError as e:
            popup_message(1,str(e))
        except TimeoutError as e:
            popup_message(2,str(e))
        except tg.ReplyError as e:
            popup_message(3,str(e))
        except tg.ApiError:
            popup_message(4,str(e))

def set_bookmark_rb():
    x = bookmark_rb.get()

def acquire_bookmark():
    camera_params_as_list = []
    rb_selection = bookmark_rb.get()
    camera_selection = acquire_from_camera.get()
    selected_camera_position, selected_camera_rotation, selected_camera_focal = get_camera_params(camera_selection)
    camera_params_as_string = str(selected_camera_position),str(selected_camera_rotation),str(selected_camera_focal)
    bookmarks[rb_selection-1] = camera_params_as_string
    build_message("acquire",rb_selection,camera_selection)

def build_message(x,rb,cam):
    if x == "acquire":
        y = str(cam) + " copied to bookmark " + str(rb) + " "
        my_messages.set(y)
    elif x == "apply":
        y = "Bookmark " + str(rb+1) + " applied to " +str (cam) + " "
        my_messages.set(y)
    elif x == "loaded":
        y = "Bookmarks loaded from disk "
        my_messages.set(y)
    elif x == "saved":
        y = "Bookmarks saved to disk "
        my_messages.set(y)

def get_camera_params(x):
    try:
        node = tg.node_by_path(x)
        pos = node.get_param('position')
        rot = node.get_param('rotation')
        foc = node.get_param('focal_length_in_mm')
        return pos,rot,foc
    except ConnectionError as e:
        popup_message(1,str(e))
    except TimeoutError as e:
        popup_message(2,str(e))
    except tg.ReplyError as e:
        popup_message(3,str(e))
    except tg.ApiError:
        popup_message(4,str(e))

def set_camera_params(cam,book):
    preset = bookmarks[book]
    try:
        node = tg.node_by_path(cam)
        node.set_param('position',preset[0])
        node.set_param('rotation',preset[1])
        node.set_param('focal_length_in_mm',preset[2])
    except ConnectionError as e:
        popup_message(1,str(e))
    except TimeoutError as e:
        popup_message(2,str(e))
    except tg.ReplyError as e:
        popup_message(3,str(e))
    except tg.ApiError:
        popup_message(4,str(e))

def apply_bookmark():
    rb_selection = bookmark_rb.get()
    camera_selection = apply_to_camera.get()
    set_camera_params(camera_selection,rb_selection-1)
    build_message("apply",rb_selection-1,camera_selection)

def save_bookmarks_to_disk():
    my_filetypes = [("Text document","*.txt"),("All files","*.*")]
    file = asksaveasfile(filetypes= my_filetypes, defaultextension=my_filetypes)
    x = str(bookmarks)
    file.write(x)
    file.close()
    build_message("saved"," "," ")

def load_bookmarks_from_disk():
    global bookmarks
    presets_from_disk = read_from_file()
    formatted_presets = format_presets_from_disk(presets_from_disk)
    bookmarks = formatted_presets

def format_presets_from_disk(presets):
    converted_string = str(presets)
    pattern = r"\(.*?\)"
    matches = re.findall(pattern,converted_string)
    extracted_elements = [eval(match) for match in matches]
    return extracted_elements

def read_from_file():
    my_filetypes = [("Text document","*.txt"),("All files","*.*")]
    file = askopenfile(mode='r',filetypes= my_filetypes)
    content = file.read()
    file.close()
    return content

def copy_bookmark(x):
    bookmark_rb.set(x)
    camera_selection = acquire_from_camera.get()
    selected_camera_position, selected_camera_rotation, selected_camera_focal = get_camera_params(camera_selection)
    camera_params_as_string = str(selected_camera_position),str(selected_camera_rotation),str(selected_camera_focal)
    bookmarks[x-1] = camera_params_as_string
    build_message("acquire",x,camera_selection)

def paste_bookmark(x):
    camera_selection = apply_to_camera.get()
    set_camera_params(camera_selection,x-1)
    build_message("apply",x-1,camera_selection)

def set_button_colour(button,colour):
    if platform.system() == "Windows":
        button.config(bg=colour)

# variables
camera_dictionary = {}
acquire_from_camera = StringVar()
apply_to_camera = StringVar()
bookmark_rb = IntVar()
bookmark_rb.set(1)
default_position = '0 10 -30'
default_rotation = '-7 0 0'
default_focal = '31.1769'
bookmarks = [(default_position,default_rotation,default_focal)] * 10
my_messages =StringVar()
my_messages.set("Welcome.  ")

# menu bar
menubar = Menu(gui)
filemenu = Menu(menubar,tearoff=0)
filemenu.add_command(label="Open bookmarks...",command=load_bookmarks_from_disk)
filemenu.add_command(label="Save bookmarks...",command = save_bookmarks_to_disk)
menubar.add_cascade(label="File",menu=filemenu)

utilitymenu = Menu(menubar,tearoff=0)
utilitymenu.add_command(label = "Display bookmarks", command=display_bookmarks)
utilitymenu.add_separator()
utilitymenu.add_command(label="Reset bookmarks",command=reset_bookmarks)
utilitymenu.add_command(label="Reset bookmarks to zero",command=reset_bookmarks_zero)
menubar.add_cascade(label="Utility",menu=utilitymenu)

helpmenu = Menu(menubar,tearoff=0)
helpmenu.add_command(label="For file menu",command=popup_help_file_menu)
helpmenu.add_command(label="For utility menu",command=popup_help_utility_menu)
menubar.add_cascade(label="Help",menu=helpmenu)

# main
camera_ids = get_cameras()
if not camera_ids:
    popup_add_camera("Add Camera","Add Camera node to project?")
    camera_ids = get_cameras()
    if not camera_ids:
        quit()

# build camera dictionary
create_camera_dictionary(camera_ids)

# labels and combobox
acquire_camera_cb = ttk.Combobox(
    frame1,
    textvariable=acquire_from_camera,
    postcommand=update_combobox_cameras
    )
acquire_camera_cb["values"] = list(camera_dictionary.values())
acquire_camera_cb.current(0)
acquire_camera_cb.grid(row=0,column=0,sticky='e',padx=5,pady=5)

apply_camera_cb = ttk.Combobox(
    frame2,
    textvariable=apply_to_camera,
    postcommand=update_combobox_cameras
    )
apply_camera_cb["values"] = list(camera_dictionary.values())
apply_camera_cb.current(0)
apply_camera_cb.grid(row=0,column=0,sticky='e',padx=5,pady=5)

null = Label(frame1, text=" ")
null.grid(row=3, columnspan=2)
null_02 = Label(frame2, text=" ")
null_02.grid(row=3, columnspan=2)

info_message = Label(
    frame3,
    textvariable=my_messages,
    fg='red',
    bg="#FFF9EC",
    padx=4
    )
info_message.grid(row=0, columnspan=2, sticky='wens')

# buttons
copy_1 = Button(frame1,text="Copy  1", command=lambda: copy_bookmark(1))
set_button_colour(copy_1, "#BED5F4")
copy_1.grid(row=3, column=1, padx=2, pady=4)
copy_2 = Button(frame1, text="Copy  2", command=lambda: copy_bookmark(2))
set_button_colour(copy_2,"#BED5F4")
copy_2.grid(row=3,column=2,padx=2,pady=4)
copy_3 = Button(frame1, text="Copy  3", command=lambda: copy_bookmark(3))
set_button_colour(copy_3,"#BED5F4")
copy_3.grid(row=3, column=3, padx=2, pady=4)
copy_4 = Button(frame1, text="Copy  4", command=lambda: copy_bookmark(4))
set_button_colour(copy_4,"#BED5F4")
copy_4.grid(row=3, column=4, padx=2, pady=4)
copy_5 = Button(frame1, text="Copy  5", command=lambda: copy_bookmark(5))
set_button_colour(copy_5,"#BED5F4")
copy_5.grid(row=3, column=5, padx=2, pady=4)

copy_6 = Button(frame1, text="Copy  6", command=lambda: copy_bookmark(6))
set_button_colour(copy_6,"#BED5F4")
copy_6.grid(row=4,column=1,padx=2,pady=4)
copy_7 = Button(frame1, text="Copy  7", command=lambda: copy_bookmark(7))
set_button_colour(copy_7,"#BED5F4")
copy_7.grid(row=4, column=2, padx=2, pady=4)
copy_8 = Button(frame1, text="Copy  8", command=lambda: copy_bookmark(8))
set_button_colour(copy_8,"#BED5F4")
copy_8.grid(row=4, column=3, padx=2, pady=4)
copy_9 = Button(frame1, text="Copy  9", command=lambda: copy_bookmark(9))
set_button_colour(copy_9,"#BED5F4")
copy_9.grid(row=4, column=4, padx=2, pady=4)
copy_10 = Button(frame1, text="Copy 10", command=lambda: copy_bookmark(10))
set_button_colour(copy_10,"#BED5F4")
copy_10.grid(row=4, column=5, padx=2, pady=2)

apply_1 = Button(frame2, text="Apply  1", command=lambda: paste_bookmark(1))
set_button_colour(apply_1,"#BEF4C2")
apply_1.grid(row=3, column=1, padx=2, pady=4)
apply_2 = Button(frame2, text="Apply  2", command=lambda: paste_bookmark(2))
set_button_colour(apply_2, "#BEF4C2")
apply_2.grid(row=3, column=2, padx=2, pady=4)
apply_3 = Button(frame2, text="Apply  3", command=lambda: paste_bookmark(3))
set_button_colour(apply_3,"#BEF4C2")
apply_3.grid(row=3, column=3, padx=2, pady=4)
apply_4 = Button(frame2, text="Apply  4", command=lambda: paste_bookmark(4))
set_button_colour(apply_4,"#BEF4C2")
apply_4.grid(row=3, column=4, padx=2, pady=4)
apply_5 = Button(frame2, text="Apply  5", command=lambda: paste_bookmark(5))
set_button_colour(apply_5,"#BEF4C2")
apply_5.grid(row=3, column=5, padx=2, pady=4)

apply_6 = Button(frame2, text="Apply  6", command=lambda: paste_bookmark(6))
set_button_colour(apply_6,"#BEF4C2")
apply_6.grid(row=4, column=1, padx=2, pady=4)
apply_7 = Button(frame2, text="Apply  7", command=lambda: paste_bookmark(7))
set_button_colour(apply_7,"#BEF4C2")
apply_7.grid(row=4, column=2, padx=2, pady=4)
apply_8 = Button(frame2, text="Apply  8", command=lambda: paste_bookmark(8))
set_button_colour(apply_8,"#BEF4C2")
apply_8.grid(row=4, column=3, padx=2, pady=4)
apply_9 = Button(frame2, text="Apply  9", command=lambda: paste_bookmark(9))
set_button_colour(apply_9,"#BEF4C2")
apply_9.grid(row=4, column=4, padx=2, pady=4)
apply_10 = Button(frame2, text="Apply 10", command=lambda: paste_bookmark(10))
set_button_colour(apply_10,"#BEF4C2")
apply_10.grid(row=4, column=5, padx=2, pady=2)

gui.config(menu=menubar)
gui.mainloop()
