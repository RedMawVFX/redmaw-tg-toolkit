from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import traceback
import os
import terragen_rpc as tg

gui = Tk()
gui.geometry("600x180")
gui.title("tg_replace_image_map_paths.py")

frame0 = LabelFrame(gui,relief=FLAT)
frame1 = LabelFrame(gui,relief=FLAT)
frame0.grid(row=0,column=0,padx=5,pady=5,sticky="WENS")
frame1.grid(row=1,column=0,padx=5,pady=5)

def popup_info(message_title,message_description):
    messagebox.showinfo(title=message_title,message=message_description)

def popup_warning(message_title,message_description):
    messagebox.showwarning(title = message_title,message = message_description)

def on_browse_old():
    old_folder_selected = filedialog.askdirectory()
    if old_folder_selected:
        normalized_path = os.path.normpath(old_folder_selected) # change forward to backward slash
        old_folder_var.set(normalized_path)
        # print("folder selected",old_folder_selected)

def on_browse_new():
    new_folder_selected = filedialog.askdirectory()
    if new_folder_selected:        
        normalized_path = os.path.normpath(new_folder_selected) # change forward to backward slash
        new_folder_var.set(normalized_path)
        # print("folder selected",new_folder_selected)
    
def on_go():
    old_path = old_folder_var.get()
    new_path = new_folder_var.get()
    number_of_changes = 0
    try:
        project = tg.root()
        image_map_shader_ids = project.children_filtered_by_class("image_map_shader")
        for map in image_map_shader_ids:
            map_filename = map.get_param("image_filename")            
            existing_map_path = os.path.dirname(map_filename)            
            if existing_map_path == old_path:
                map_basename = os.path.basename(map_filename)                
                new_filename = os.path.join(new_path,map_basename)                
                map.set_param("image_filename",new_filename)
                number_of_changes +=1
    except ConnectionError as e:
            popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())
    
    popup_info("Terragen RPC complete",str(len(image_map_shader_ids)) + " image map shaders in project. \n" + str(number_of_changes) + " image map shader paths modified.")

# variables
old_folder_var = StringVar()
new_folder_var = StringVar()

# gui elements
Label(frame0,text="Old file path to replace").grid(row=0,column=0,sticky=W)
Label(frame0,text="New file path").grid(row=1,column=0,sticky=W)

old_folder_e = Entry(frame0,textvariable=old_folder_var,width=60)
new_folder_e = Entry(frame0,textvariable=new_folder_var,width=60)
old_folder_e.grid(row=0,column=1)
new_folder_e.grid(row=1,column=1)

old_folder_b = Button(frame0,text="Browse",command=on_browse_old)
new_filepath_b = Button(frame0,text="Browse",command=on_browse_new)
old_folder_b.grid(row=0,column=2,padx=5,pady=5)
new_filepath_b.grid(row=1,column=2,padx=5,pady=5)

go_b = Button(frame1,text="Replace paths that match old file paths",command=on_go,bg="yellow")
go_b.grid(row=2,column=2)

gui.mainloop()