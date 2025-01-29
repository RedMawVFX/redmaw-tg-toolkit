'''
tg_dashbord.py - This script makes organizing and running your Python scripts for Terragen 
just one button click away.  The script will automatically generate a User Interface with
 button widgets and tabs according to the contents of its config file. The config file is
 TOML formatted.
'''
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform
import toml
try:
    import terragen_rpc as tg
except (ImportError, ModuleNotFoundError):
    messagebox.showwarning(
        "Terragen RPC Missing",
        "Terragen RPC module is missing. Please see README file for installation instructions."
        )
    sys.exit(1)

def execute_script(script_path):
    """Execute the script given by the full path, from its local directory."""
    original_directory = os.getcwd()  # Save the current working directory

    if not os.path.exists(script_path):
        # Show a warning message if the script does not exist
        messagebox.showwarning("Script Missing", f"The script '{script_path}' is missing.")
        return

    script_directory = os.path.dirname(script_path)  # Get the directory of the script
    os.chdir(script_directory)  # Change the current working directory to the script's directory

    try:
        # Determine the platform to choose the correct executable
        if platform.system() == 'Windows':
            # Use pythonw.exe on Windows to prevent terminal window from opening
            command = ['pyw', script_path]
        else:
            # On macOS and Linux, just use python3
            command = ['python3', script_path]

        # Run the script
        subprocess.run(command, check=True)
    finally:
        # Restore the original working directory after the script execution
        os.chdir(original_directory)

def handle_shortcut(event, shortcuts_dict):
    """Handle the keypress event and trigger script execution."""
    key_combination = event.keysym.lower()

    # Check for modifier keys (Shift, Control, Alt)
    modifiers = []
    if event.state & 0x0001:  # Shift
        modifiers.append('Shift')
    if event.state & 0x0004:  # Control
        modifiers.append('Control')

    # Check for Alt key modifier by keysym
    if event.keysym in ['Alt_L', 'Alt_R']:  # Left or Right Alt key
        modifiers.append('Alt')

    # Combine the modifiers with the key (e.g., Shift-b or Control-b)
    full_shortcut = '+'.join(modifiers + [key_combination]) if modifiers else key_combination

    # Format the detected shortcut to match the dictionary format
    if len(full_shortcut) == 1:  # Single letter shortcut (e.g., 'k')
        full_shortcut = f"<{full_shortcut}>"
    else:
        full_shortcut = full_shortcut.replace("+", "-")  # Convert '+' to '-'

    # Check if the combined shortcut is in the dictionary and trigger the corresponding script
    if full_shortcut in shortcuts_dict:
        execute_script(shortcuts_dict[full_shortcut])
    else:
        print(f"Shortcut '{full_shortcut}' not found in dictionary.")

def create_buttons_for_category(tab, category_name, scripts_with_shortcuts, shortcuts_dict, base_dir):
    """Create buttons for each script in a given category, and bind keyboard shortcuts."""
    row, col = 0, 0  # To place 2 buttons per row

    for script in scripts_with_shortcuts:
        script_path, label, shortcut = script

        # Resolve relative path to absolute path and normalize path
        full_script_path = os.path.join(base_dir, script_path) if not os.path.isabs(script_path) else script_path
        full_script_path = os.path.normpath(full_script_path)  # Normalize path for OS-specific separators

        # Use the filename if no label is provided
        button_label = label if label else os.path.basename(script_path)

        # Create a button for each script
        button = tk.Button(tab, text=button_label, width=30, command=lambda path=full_script_path: execute_script(path))
        button.grid(row=row, column=col, padx=5, pady=2, sticky="ew")

        # Add the shortcut to the dictionary to be checked during key press
        if shortcut:
            shortcuts_dict[shortcut] = full_script_path

        # Update row and col to display 2 buttons per row
        col += 1
        if col == 2:
            col = 0
            row += 1

def create_tabs_from_config(config_file):
    """Create tabs and buttons dynamically based on the TOML config file."""
    # Get the base directory (directory where the script is located)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Load the TOML config file
    config = toml.load(config_file)

    # Iterate through the categories and create tabs and buttons
    color_index = 1  # To track which color to apply to each tab

    shortcuts_dict = {}  # Dictionary to store shortcut -> script mapping

    for category in config['category']:
        category_name = category['name']
        category_name_for_tabs = f"{category_name} "
        scripts = category['scripts']

        scripts_with_shortcuts = []
        for script in scripts:
            path = script['path']
            label = script.get('label', None)
            shortcut = script.get('shortcut', None)
            scripts_with_shortcuts.append((path, label, shortcut))

        # Create a new tab for this category using tk.Frame instead of ttk.Frame
        tab = tk.Frame(notebook, padx=5, pady=5)
        notebook.add(tab, text=category_name_for_tabs)

        # Set the background color of the tab's content area
        tab.config(bg=colors[color_index])

        # Create buttons for scripts in the tab
        create_buttons_for_category(tab, category_name, scripts_with_shortcuts, shortcuts_dict, base_dir)

        # Increment the color index and reset if it exceeds the available colors
        color_index += 1
        if color_index >= len(colors):
            color_index = 0

    return shortcuts_dict  # Return the dictionary of shortcuts

def show_shortcuts_info(config_file):
    """Display a window with the list of script names and their shortcuts."""
    config = toml.load(config_file)

    shortcut_info = "Shortcuts:\n\n"
    for category in config['category']:
        scripts = category['scripts']
        for script in scripts:
            label = script.get('label', None)
            shortcut = script.get('shortcut', None)

            # Only include scripts with shortcuts
            if shortcut:
                script_name = label if label else os.path.basename(script['path'])
                shortcut_info += f"{script_name}: {shortcut}\n"

    # Show the info in a messagebox
    messagebox.showinfo("Shortcuts", shortcut_info)

# windows and tab colours
colors = ["#F1DDB4", "#B8DBD0", "#B8B8DB", "#DCB8DB", "#DBB8B8", "#DBD1B8", "#DBB8C5"]

# Create the main window
root = tk.Tk()
root.title(os.path.basename(__file__))
root.config(background=colors[0])

# Create the Menu Bar
menubar = tk.Menu(root)

# Create Help menu
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Shortcuts", command=lambda: show_shortcuts_info(config_file))
menubar.add_cascade(label="Help", menu=help_menu)

# Configure the menu
root.config(menu=menubar)

# Create a Notebook (tabs container)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=5, pady=5)

# Path to your TOML config file
config_file = 'tg_dashboard_config.toml'  # Update this with your actual path

# Create tabs and buttons based on the TOML config file and get the shortcut dictionary
shortcuts_dict = create_tabs_from_config(config_file)

# Bind the key press events for Shift and Control on the root window (regular keys)
root.bind_all('<KeyPress>', lambda event: handle_shortcut(event, shortcuts_dict))

# Specifically handle Alt key separately (via <Alt> keypress binding)
root.bind_all('<Alt-KeyPress>', lambda event: handle_shortcut(event, shortcuts_dict))

# Start the Tkinter application
root.mainloop()
