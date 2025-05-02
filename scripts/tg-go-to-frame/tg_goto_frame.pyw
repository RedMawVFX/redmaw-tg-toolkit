'''
tg_go_to_frame.py - Sets the current frame in the Terragen project.

When first executed the Entry widget value is set to the current frame
in the project.  

Certain keyboard bindings can be used as shortcuts to modify the value
of the Entry widget.
    Up arrow - step to next frame
    Down arrow - step to previous frame
    Escape - resets Entry widget to initial value
    MouseWheel up - steps to next frames (must press Enter key to accept)
    MouseWheel down -steps to previous frames (must press Enter key to accept)
'''

import os.path
import traceback
import tkinter as tk
from tkinter import messagebox
import terragen_rpc as tg

gui = tk.Tk()
gui.title(os.path.basename(__file__))
gui.geometry("280x75")

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

def is_valid_integer(value):
    """
    Check if the string value is a valid integer.

    Args:
        value (str): Current value of the Entry widget

    Returns:
        (bool)
    """
    global ERROR_SHOWN
    try:
        int(value)
        return True
    except ValueError:
        if not ERROR_SHOWN:
            popup_warning("Invalid input", "Please enter a valid integer.")
            ERROR_SHOWN = True
        return False

def on_go_to(_) -> None:
    '''
    Advances the current frame according to the value in the Entry widget.

    Args:
        (_): Unused keyrelease event

    Returns:
        None
    '''
    global ERROR_SHOWN
    if not defer_eval.get():
        current_frame = current_frame_var.get()
        if is_valid_integer(current_frame):
            ERROR_SHOWN = False
            try:
                project = tg.root()
                project.set_param("current_frame", int(current_frame_var.get()))
            except ConnectionError as e:
                popup_warning(os.path.basename(__file__), "Terragen RPC connection error" + str(e))
                return None
            except TimeoutError as e:
                popup_warning(os.path.basename(__file__), "Terragen RPC timeout error" + str(e))
                return None
            except tg.ReplyError as e:
                popup_warning(os.path.basename(__file__), "Terragen RPC reply error" + str(e))
                return None
            except tg.ApiError:
                popup_warning(
                    os.path.basename(__file__),
                    "Terragen RPC API error" + str(traceback.format_exc())
                    )
                return None

def on_enter(event) -> None:
    '''
    Advances the current frame according to the value in the Entry widget only
    when the defer checkbutton is enabled and Enter is pressed.

    Args:
        (event): enter key pressed

    Returns:
        None
    '''
    global ERROR_SHOWN
    if defer_eval.get():
        current_frame = current_frame_var.get()
        if is_valid_integer(current_frame):
            ERROR_SHOWN = False
            try:
                project = tg.root()
                project.set_param("current_frame", int(current_frame_var.get()))
            except ConnectionError as e:
                popup_warning(os.path.basename(__file__), "Terragen RPC connection error" + str(e))
                return None
            except TimeoutError as e:
                popup_warning(os.path.basename(__file__), "Terragen RPC timeout error" + str(e))
                return None
            except tg.ReplyError as e:
                popup_warning(os.path.basename(__file__), "Terragen RPC reply error" + str(e))
                return None
            except tg.ApiError:
                popup_warning(
                    os.path.basename(__file__),
                    "Terragen RPC API error" + str(traceback.format_exc())
                    )
                return None 

def decrease_value(_) -> None:
    '''
    Decreases the current frame value by one.

    Args:
        (_): Unused down arrow event

    Returns:
        None
    '''
    current_frame = current_frame_var.get()
    if is_valid_integer(current_frame):
        current_frame_var.set(int(current_frame) - 1)

def increase_value(_) -> None:
    '''
    Increases the current frame value by one.

    Args:
        (_): Unused up arrow event

    Returns:
        None
    '''
    current_frame = current_frame_var.get()
    if is_valid_integer(current_frame):
        current_frame_var.set(int(current_frame) + 1)

def on_mouse_wheel(event) -> None:
    '''
    Increases or decreases the current frame value.

    Args:
        (event): Mousewheel up or down scrolling

    Returns:
        None
    '''
    current_value = current_frame_var.get()
    if is_valid_integer(current_value):
        if event.delta > 0:
            current_frame_var.set(str(int(current_value) + 1))
        elif event.delta < 0:
            current_frame_var.set(str(int(current_value) - 1))
    else:
        print("Invalid input")

def on_escape(_) -> None:
    '''
    Resets the Entry widget value to its original value at the time the
    script was first run.

    Args:
        (_): Unused escape key event

    Returns:
        None
    '''
    current_frame_var.set(current_frame_at_startup.get())

def on_startup() -> None:
    '''
    Gets initial values from the current Terragen projects and sets the
    global tkinter variables.

    Returns:
        None
    '''
    try:
        project = tg.root()
        current_frame_at_startup.set(project.get_param("current_frame"))
        current_frame_var.set(current_frame_at_startup.get())
        start_frame_var.set(project.get_param("start_frame"))
        end_frame_var.set(project.get_param("end_frame"))
    except ConnectionError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC connection error" + str(e))
        return None
    except TimeoutError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC timeout error" + str(e))
        return None
    except tg.ReplyError as e:
        popup_warning(os.path.basename(__file__), "Terragen RPC reply error" + str(e))
        return None
    except tg.ApiError:
        popup_warning(
            os.path.basename(__file__),
            "Terragen RPC API error" + str(traceback.format_exc())
            )
        return None

def set_focus_and_select() -> None:
    '''
    Sets focus to the entry widget and select the entire text

    Returns:
        None
    '''
    frame.focus_set()
    frame.select_range(0, tk.END)

# tkinker variables
current_frame_at_startup = tk.StringVar()
current_frame_var = tk.StringVar()
current_frame_var.set("1")
start_frame_var = tk.StringVar()
end_frame_var = tk.StringVar()
ERROR_SHOWN = False
defer_eval = tk.BooleanVar()
defer_eval.set(True)

# main
on_startup()

# gui
tk.Label(gui, text="Go to frame: ").grid(row=0, column=0, padx=4, pady=10, sticky="w")

frame = tk.Entry(gui, textvariable=current_frame_var, width=10)
frame.grid(row=0, column=1, padx=4, pady=10, sticky="w")
frame.bind("<MouseWheel>", on_mouse_wheel)
frame.bind("<Up>", increase_value)
frame.bind("<Down>", decrease_value)
frame.bind("<KeyRelease>", on_go_to)
frame.bind("<Return>", on_enter)
frame.bind("<Escape>", on_escape)

defer = tk.Checkbutton(gui, text="Defer evaluation (Press Enter)", variable=defer_eval)
defer.grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="w")

set_focus_and_select()

gui.mainloop()
