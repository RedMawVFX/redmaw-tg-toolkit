'''
tg_find_nodes_in_project.pyw - Finds nodes in the Terragen project.  Can add or
remove them from the currently selected nodes in the scene.
'''
import os.path
import platform
import traceback
import tkinter as tk
from tkinter import messagebox
import terragen_rpc as tg

gui = tk.Tk()
gui.geometry("353x478" if platform.system() == "Darwin" else
             "250x460")
gui.title(os.path.basename(__file__))
gui_colours = ["#6f8e90", "#9db2b3", "#DBD0BD", "#D8C3BD", "#C1BDDB", "#DBBDC4"]
gui.configure(bg=gui_colours[0])

frame0 = tk.Frame(gui, relief=tk.FLAT, bg=gui_colours[1])
frame1 = tk.Frame(gui, relief=tk.FLAT, bg=gui_colours[1])
frame2 = tk.LabelFrame(gui, relief=tk.FLAT, text="Quick select in listbox ", bg=gui_colours[1])
frame3 = tk.LabelFrame(
    gui,
    relief=tk.FLAT,
    text="Select / deselect nodes in Terragen ",
    bg=gui_colours[1]
    )
frame0.grid(row=0, column=0, padx=6, pady=6, sticky="WENS")
frame1.grid(row=1, column=0, padx=6, pady=6, sticky="WENS")
frame2.grid(row=2, column=0, padx=6, pady=6, sticky="WENS")
frame3.grid(row=3, column=0, padx=6, pady=6, sticky="WENS")

gui.rowconfigure(0, weight=1)
gui.rowconfigure(1, weight=2)
gui.rowconfigure(2, weight=1)
gui.rowconfigure(3, weight=1)
gui.columnconfigure(0, weight=1)

frame1.grid_rowconfigure(0, weight=1)
frame1.grid_columnconfigure(0, weight=1)

COLOUR_SEARCH_WITH_VALUE = "#E8D7F2" # light purple
COLOUR_SEARCH_WITHOUT_VALUE = ""

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

def update_listbox(event=None):
    '''
    Removes items in the listbox that don't match search pattern.
    Can be called by an event.

    Returns:
        None
    '''
    search_term = search_var.get().lower()
    if len(search_term) > 0:
        item_colour = COLOUR_SEARCH_WITH_VALUE
    else:
        item_colour = COLOUR_SEARCH_WITHOUT_VALUE
    listbox.delete(0, tk.END)
    for i in child_paths:
        if search_term in i.lower():
            listbox.insert(tk.END, i)
            listbox.itemconfig(tk.END, {'bg': item_colour})

def on_add_to_project() -> None:
    '''
    Adds selected items in the listbox to the selected nodes in the project.

    Returns:
        None
    '''
    if child_paths:
        listbox_selection = listbox.curselection()
        if listbox_selection:
            for index in listbox_selection:
                selected_path = listbox.get(index)
                node_id = get_node_id_from_path(selected_path)
                if node_id:
                    select_deselect_in_project(node_id=node_id, mode="add")

def on_remove_from_project() -> None:
    '''
    Removes nodes selected in the listbox from the current selection of nodes
    in the project.

    Returns: 
        None
    '''
    listbox_selection = []
    if child_paths:
        listbox_selection = listbox.curselection()
        if listbox_selection:
            for index in listbox_selection:
                selected_path = listbox.get(index)
                node_id = get_node_id_from_path(selected_path)
                if node_id:
                    selected_nodes_in_project = select_deselect_in_project(
                        node_id=None,
                        mode="current"
                        )
                    if selected_nodes_in_project:
                        currently_selected_node_paths = []
                        for selected_node in selected_nodes_in_project:
                            selected_node_path = get_path(selected_node)
                            currently_selected_node_paths.append(selected_node_path)
                        if selected_path in currently_selected_node_paths:
                            currently_selected_node_paths.remove(selected_path)
                        select_deselect_in_project(node_id=None, mode="clear")
                        node_ids_to_select = []
                        for path in currently_selected_node_paths:
                            new_node_id = get_node_id_from_path(path)
                            node_ids_to_select.append(new_node_id)
                        for selected_id in node_ids_to_select:
                            select_deselect_in_project(selected_id, mode="add")

def select_deselect_in_project(node_id=None, mode=None):
    '''
    This function unifies several rpc method calls under one exception
    handler for better readability.

    Args:
        node_id (obj): Node id
        mode (str): Action to perform: current, add, clear

    Return:
        current_selection (list): Node ids or None
    '''
    try:
        match mode:
            case "current":
                return tg.current_selection()
            case "add":
                tg.select_more(node_id)
                return None
            case "clear":
                tg.select_none()
                return None
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error", str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error", str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error", str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error", traceback.format_exc())

def get_node_id_from_path(path):
    '''
    Gets the node id from the given path.

    Returns
        <obj>: A node id or None. 
    '''
    try:
        return tg.node_by_path(path)
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error", str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error", str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error", str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error", traceback.format_exc())

def listbox_select_all() -> None:
    '''
    Selects all items in the listbox.

    Returns:
        None
    '''
    listbox.selection_set(0,tk.END)

def listbox_select_none() -> None:
    '''
    Deselects all items in the listbox.

    Returns:
        None
    '''
    listbox.selection_clear(0,tk.END)

def listbox_select_invert() -> None:
    '''
    Inverts listbox selection.

    Returns:
        None
    '''
    total_items = listbox.size()
    for i in range(total_items):
        if i not in listbox.curselection():
            listbox.select_set(i)
        else:
            listbox.select_clear(i)

def on_refresh() -> None:
    '''
    Triggers function calls to resample project file for latest nodes.
    Refreshes the contents of the listbox.

    Returns:
        None
    '''
    global child_paths
    child_paths = get_root_level_nodes()
    listbox.delete(0,tk.END)
    for path in child_paths:
        listbox.insert(tk.END, path)
    update_listbox()

def get_paths_of_child_nodes(child_node_ids_filtered):
    '''    
    Gets path of nodes and sorts in alphanumeric order.

    Args:
        child_node_ids_filtered (list): Object ids of root level child nodes.

    Returns:
        paths (list): Node paths in alphanumeric order.
    '''
    paths = []
    if child_node_ids_filtered:
        for child in child_node_ids_filtered:
            child_path = get_path(child)
            if child_path:
                paths.append(child_path)
    if paths:
        paths.sort()
    return paths

def get_path(child_obj):
    '''
    Gets the path of a node.

    Args:
        child_obj (obj): Child id as object (memory address)

    Returns:
        child_path (str): Path of child node, i.e. /Sunlight 01
    '''
    try:
        child_path = child_obj.path()
        return child_path
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error", str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error", str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error", str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error", traceback.format_exc())

def get_root_level_nodes():
    '''
    Gets all root level nodes in the project and calls function to determine paths.

    Returns:
        child_paths (list): Child node paths sorted alphnumerically.    
    '''
    try:
        project = tg.root()
        child_node_ids = project.children()
        group_node_ids = project.children_filtered_by_class("group")
        child_node_ids_filtered = remove_group_nodes(child_node_ids, group_node_ids)
        child_paths_sorted = get_paths_of_child_nodes(child_node_ids_filtered)
        return child_paths_sorted
    except ConnectionError as e:
        popup_warning("Terragen RPC connection error", str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error", str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error", str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error", traceback.format_exc())

def remove_group_nodes(child_node_ids, group_node_ids):
    '''
    Removes group nodes from list of child nodes, because object instances
    are not hashable and can't use set commands.

    Args:
        child_node_ids (list): Object ids of root level child nodes.
        group_node_ids (list): Object ids of group nodes.

    Returns:
        child_node_ids_filtered (list): Object ids of child nodes
    '''
    child_node_ids_filtered = []
    if child_node_ids:
        for child in child_node_ids:
            if child not in group_node_ids:
                child_node_ids_filtered.append(child)
    return child_node_ids_filtered

def on_clear() -> None:
    '''
    Clears search variable and updates the listbox.

    Returns:
        None
    '''
    search_var.set("")
    update_listbox()

# main
child_paths = get_root_level_nodes()

# tkinter variables
search_var = tk.StringVar()

# gui frame 0
tk.Label(frame0, text="Search pattern: ", bg=gui_colours[1]).grid(row=0, column=0, pady=4)
search_e = tk.Entry(frame0, textvariable=search_var, bg=COLOUR_SEARCH_WITH_VALUE)
search_e.grid(row=0, column=1)
search_e.bind("<KeyRelease>", update_listbox)

clear_b = tk.Button(frame0, text="Clear", command=on_clear, width=6)
clear_b.grid(row=1, column=0, padx=4, pady=4, sticky="w")

# gui frame1
listbox = tk.Listbox(frame1, width=36, selectmode=tk.MULTIPLE)
listbox.grid(row=0, column=0, columnspan=3, sticky="nsew")
for item in child_paths:
    listbox.insert(tk.END, item)
scrollbar = tk.Scrollbar(frame1, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.grid(row=0, column=3, sticky="ns", columnspan=4)
listbox.config(yscrollcommand=scrollbar.set)

refresh_b = tk.Button(frame1, text="Refresh", command=on_refresh, width=6)
refresh_b.grid(row=1, column=0, padx=4, pady=6, sticky="w")

listbox_select_all_b = tk.Button(frame2, text="All", command=listbox_select_all, width=6)
listbox_select_all_b.grid(row=0, column=0, padx=4, pady=6, sticky="w")
listbox_select_none_b = tk.Button(frame2, text="None", command=listbox_select_none, width=6)
listbox_select_none_b.grid(row=0, column=1, padx=4, pady=6, sticky="w")
listbox_select_invert_b = tk.Button(frame2, text="Invert", command=listbox_select_invert, width=6)
listbox_select_invert_b.grid(row=0, column=2, padx=4, pady=6, sticky="w")

# gui frame3
all_b = tk.Button(frame3, text="Add to selection", command=on_add_to_project, width=18)
all_b.grid(row=0, column=2, padx=4, pady=4, sticky="w")
none_b = tk.Button(frame3, text="Remove from selection", command=on_remove_from_project, width=18)
none_b.grid(row=1, column=2, padx=4, pady=4, sticky="w")

gui.mainloop()
