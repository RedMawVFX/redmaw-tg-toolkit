import os.path
import platform
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import traceback
import terragen_rpc as tg

gui = Tk()
gui.geometry("944x640" if platform.system() == "Darwin" else
             "650x640")
gui.title(os.path.basename(__file__))
gui.config(bg="#89B2B9")

gui.rowconfigure(0,weight=1)
gui.rowconfigure(1,weight=1)
gui.rowconfigure(2,weight=1)
gui.rowconfigure(3,weight=1)

frame1 = Frame(gui,padx=10,pady=10,bg="#B8DBD0") # listbox
frame1.grid(row=0,column=0,padx=4,pady=4,sticky="WENS")
frame2 = Frame(gui,padx=10,pady=10,bg="#CBAE98") # buttons
frame2.grid(row=2,column=0,padx=4,pady=4,sticky="WENS")
frame3 = Frame(gui,padx=10,pady=10,bg="#B8DBD0") # counter label
frame3.grid(row=1,column=0,padx=4,pady=2,sticky="WENS")

def analyze_project():
    update_progress_status("Analyzing project. This may take a moment.")
    gui.update()
    analyze()
    update_progress_status('Number of nodes in project ending with "_1" is')

def analyze():
    listbox_delete_all()
    global all_names_in_project, names_to_rename, ids_to_rename, paths_to_rename
    try:
        project = tg.root()
        all_names_in_project, names_to_rename, ids_to_rename, paths_to_rename = get_nodes_in_node(project) # may not need globals this way
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())
        
    if len(paths_to_rename) == 0:
        popup_info("tg_rename_1_1_1_ndoes.py", "No nodes found in project ending in '_1'.")    
    listbox_populate(paths_to_rename)

def update_progress_status(update_msg):
    progress_status.set(update_msg)

def get_nodes_in_node(in_node):
    names_in_project_list = []
    names_to_rename_list = []
    paths_to_rename_list = []
    ids_to_rename_list = []
    try:
        ids_of_children = in_node.children()
        if ids_of_children:
            for child_id in ids_of_children:
                child_name = child_id.name()
                child_path = child_id.path()
                names_in_project_list.append(child_name)
                if child_name[-2:] == "_1":
                    names_to_rename_list.append(child_name)
                    paths_to_rename_list.append(child_path)
                    ids_to_rename_list.append(child_id)
                deeper_all_names, deeper_child_names, deeper_child_ids, deeper_child_paths = get_nodes_in_node(child_id)
                names_in_project_list.extend(deeper_all_names)
                names_to_rename_list.extend(deeper_child_names)
                paths_to_rename_list.extend(deeper_child_paths)
                ids_to_rename_list.extend(deeper_child_ids)
        num_nodes_to_rename.set(len(names_to_rename_list))
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())

    return names_in_project_list,names_to_rename_list,ids_to_rename_list,paths_to_rename_list

def listbox_populate(paths_to_rename):
    for item in paths_to_rename:
        listbox_of_nodes.insert(END,item)

def listbox_select_all():
    for i in range(listbox_of_nodes.size()):
        listbox_of_nodes.selection_set(i)

def listbox_select_none():
    listbox_of_nodes.selection_clear(0,END)

def listbox_delete_all():
    listbox_of_nodes.delete(0,END)

def rename_selected_nodes():
    selected_indices = listbox_of_nodes.curselection() # returns tuple of integers of selection indices
    global new_names_to_compare, names_to_rename    
    global paths_to_rename    
    new_names_to_update = []
    selected_node_ids_to_rename = []
    selected_indices_actually_update = [] # need this to update the listbox properly
    selected_node_new_paths = []
    if selected_indices:
        for i in selected_indices:
            current_node_id = ids_to_rename[i]
            truncate_name = names_to_rename[i]
            if truncate_name[-2:] == "_1": # check pattern because update function can rename listbox items and they can be selected again
                while (truncate_name[-2:] == "_1"):
                        truncate_name = truncate_name[:-2]
                if truncate_name[-2:].isdigit():
                    new_node_name = names_with_numeric_suffix(truncate_name,all_names_in_project,new_names_to_compare)
                    new_names_to_compare.append(new_node_name)
                    new_names_to_update.append(new_node_name)
                    selected_node_ids_to_rename.append(current_node_id)
                    selected_indices_actually_update.append(i)
                else:
                    new_node_name = names_with_alphabetic_suffix(truncate_name,all_names_in_project,new_names_to_compare)
                    new_names_to_compare.append(new_node_name)
                    new_names_to_update.append(new_node_name)
                    selected_node_ids_to_rename.append(current_node_id)
                    selected_indices_actually_update.append(i)

        selected_node_new_paths = update_project(selected_node_ids_to_rename,new_names_to_update)
        if len(selected_node_new_paths) == 0:
            # if nothing returned from update function it means either an rpc exception possibly occured and TG is not running or the nodes were already renamed
            # if tg not running clear the listbox and return everything to the default state
            try:
                x = tg.root()
            except ConnectionError:
                listbox_delete_all()
                return_globals_to_default_state()

    else:
        popup_info("tg_rename_1_1_1_nodes.py","Please select nodes first.")

    # update the list box to display new node name.  In this way, the indexes are preserved even if the value displayed changes.
    if selected_indices_actually_update and selected_node_new_paths:
        for index, item in enumerate(selected_indices_actually_update):
            listbox_of_nodes.delete(item)
            listbox_of_nodes.insert(item,selected_node_new_paths[index])
            names_to_rename[item] = new_names_to_update[index] # updates the original list, otherwise it picks up the old 
            paths_to_rename[item] = selected_node_new_paths[index]

def names_with_numeric_suffix(truncate_name,all_nodes,new_names_to_compare):
    does_name_already_exist = 1 # assume exists
    starting_number = int(truncate_name[-2:])
    increment_by = 0
    while does_name_already_exist >= 0:
        increment_by = increment_by + 1
        next_number = starting_number + increment_by
        suggested_name = truncate_name[:-2] + str(next_number).zfill(2)
        name_exist = does_name_exist_in_project(suggested_name,all_nodes,new_names_to_compare)
        if name_exist == 0: # means suggested name is not in use
            does_name_already_exist = -1
    return(suggested_name)

def names_with_alphabetic_suffix(truncate_name,all_nodes,new_names_to_compare):
    does_name_already_exist = 1 # assume exists
    increment_by = 0
    while does_name_already_exist >= 0:
        increment_by = increment_by + 1
        suggested_name = truncate_name + " " + str(increment_by).zfill(2)
        name_exist = does_name_exist_in_project(suggested_name,all_nodes,new_names_to_compare)
        if name_exist == 0:
            does_name_already_exist = -1
    return (suggested_name)

def does_name_exist_in_project(name,all_nodes,new_names_to_compare): # this function checks to see if the suggested name already exists in the list of all names and list of new names
    exist = 1 # assume exists
    for i in all_nodes:
        if name  == i:
            return(exist)
    if len(new_names_to_compare) > 0: # first time through, won't be anything in the list
        for i in new_names_to_compare:
            if name == i:
                return(exist)
    exist = 0 # name doesn't exist yet
    return (exist)

def popup_info(title_text,message_text):
    messagebox.showinfo(title=title_text,message=message_text)

def popup_warning(message_type,message_description):
    messagebox.showwarning(title=message_type, message = message_description)

def update_project(selected_node_ids_to_rename,new_names_to_update): # updates the node's name and returns a list of new auto-generated node paths
    auto_update_path = []
    try:
        for counter, item in enumerate(selected_node_ids_to_rename):
            item.set_param('name',new_names_to_update[counter])
            auto_update_path.append(item.path())
        return auto_update_path            
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
        return auto_update_path
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
        return auto_update_path
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
        return auto_update_path
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())
        return auto_update_path
    
def return_globals_to_default_state():
    global all_names_in_project, names_to_rename, paths_to_rename, ids_to_rename, new_names_to_compare    
    all_names_in_project = []
    names_to_rename = []
    paths_to_rename = []
    ids_to_rename = []
    new_names_to_compare = []
    num_nodes_to_rename.set(0)
    update_progress_status('Click the "Analyze project" button to start.  It may take a moment to process the entire project.')    

# global variables
num_nodes_to_rename = IntVar()
all_names_in_project = []
names_to_rename = []
paths_to_rename = []
ids_to_rename = []
new_names_to_compare = []
progress_status = StringVar()
update_progress_status('Click the "Analyze project" button to start.  It may take a moment to process the entire project.')

# gui components
listbox_of_nodes = Listbox(frame1,width=100,height=30,selectmode=MULTIPLE)
listbox_of_nodes.grid(row=0,column=0,sticky="WENS")

listbox_scrollbar = Scrollbar(frame1,orient="vertical")
listbox_scrollbar.config(command=listbox_of_nodes.yview)
listbox_scrollbar.grid(row=0,column=1,sticky="NS")

listbox_of_nodes.config(yscrollcommand=listbox_scrollbar.set)

# labels
progress_label = Label(frame3,textvariable=progress_status,bg="#B8DBD0")
progress_label.grid(row=1,column=0,columnspan=3,sticky="w")

total_nodes_to_rename_label = Label(frame3,textvariable=num_nodes_to_rename,bg="#B8DBD0")
total_nodes_to_rename_label.grid(row=1,column=3)

# buttons
analyze_button = Button(frame2,text="Analyze project / Refresh list",command=analyze_project)
analyze_button.grid(row=1,column=0,padx=4,pady=4)

select_all_button = Button(frame2, text="Select all",command=listbox_select_all)
select_all_button.grid(row=1,column=1,padx=20,pady=4)

select_none_button = Button(frame2,text="Select none",command=listbox_select_none)
select_none_button.grid(row=1,column=2,padx=5,pady=4)

rename_button = Button(frame2, text="Rename nodes", command=rename_selected_nodes)
if platform.system() == "Windows":
    rename_button.config(bg='gold')
rename_button.grid(row=1, column=4, padx=20, pady=4)

gui.mainloop()