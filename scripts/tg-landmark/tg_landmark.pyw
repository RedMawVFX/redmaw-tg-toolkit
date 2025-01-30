'''
Adds a landmark object to the project, either at the origin of the project
or the coordinates in the clipboard.
'''
import os.path
import platform
import tkinter as tk
import terragen_rpc as tg

gui = tk.Tk()
gui.title(os.path.basename(__file__))
gui.geometry("500x250")

# Frame setup
frame1 = tk.LabelFrame(gui, text="Add landmark at origin", padx=5, pady=5)
frame2 = tk.LabelFrame(gui, text="Add landmark at coordinates", padx=5, pady=5)
frame3 = tk.LabelFrame(gui, relief=tk.FLAT, bg="#FFF9EC")

gui.grid_columnconfigure(0, weight=1)
gui.grid_columnconfigure(1, weight=1)
gui.grid_rowconfigure(0, weight=1)
gui.grid_rowconfigure(1, weight=2)

frame1.grid(row=0, column = 0, sticky='nsew')
frame2.grid(row=0, column = 1, sticky='nsew')
frame3.grid(row=1, column = 0, columnspan=2, sticky='nsew')

def add_landmark() -> None:
    '''
    Builds a list of parameter values for landmark object
    and calls function to add landmark object to project.

    Args:
        x (int): Index of radio button selected for scale

    Returns:
        None
    '''
    choice = rb_origin.get()
    scale = [2, 20, 200, 2000]
    landmark_values = [] #name, scale, postion, colour
    landmark_values.append("Landmark " + str(scale[choice-1]) + "m")
    landmark_values.append(scale[choice-1])
    landmark_values.append((0, 0, 0))
    landmark_values.append((0, 1, 0))
    rpc_landmark(landmark_values)
    if rpc_error.get() is False:
        message.set(landmark_values[0] + " added at origin")

def add_landmark_at() -> None:
    '''
    Adds a landmark object at the coordinates in the clipboard.

    Args:
        x (int): Index of radio button selected for scale

    Returns:
        None
    '''
    choice = rb_coordinates.get()
    clipboard_text = gui.clipboard_get()
    if clipboard_text[0:4] == "xyz:":
        trimmed_text = clipboard_text[5:] # trim off xyz: from front of string
        split_text = trimmed_text.split(",")
        position = str(split_text[0] + " " + split_text[1] + " " + split_text[2])
        scale = [2, 20, 200, 2000]
        landmark_values = [] #name, scale, postion, colour
        landmark_values.append("Landmark " + str(scale[choice-1]) + "m")
        landmark_values.append(scale[choice-1])
        landmark_values.append(position)
        landmark_values.append((0, 0, 1))
        rpc_landmark(landmark_values)
        if rpc_error.get() is False:
            message.set(landmark_values[0]+" added at coordinates "+landmark_values[2])
    else:
        message.set("Invalid coordinates in clipboard.")

def rpc_landmark(landmark_values) -> None:
    '''
    Adds Landmark object to project and sets parameter values.

    Args:
        landmark_values []: List of values

    Returns:
        None
    '''
    try:
        project = tg.root()
        new_landmark = tg.create_child(project,'landmark')
        new_landmark.set_param('name', landmark_values[0])
        new_landmark.set_param('position',landmark_values[2])
        new_landmark.set_param('scale',landmark_values[1])
        new_landmark.set_param('colour',landmark_values[3])
        rpc_error.set(False)
    except ConnectionError as e:
        formatted_message = format_message("Terragen RPC connection error: " + str(e))
        message.set(formatted_message)
        rpc_error.set(True)
    except TimeoutError as e:
        message.set("Terragen RPC timeout error: " + str(e))
        rpc_error.set(True)
    except tg.ReplyError as e:
        message.set("Terragen RPC server reply error: " + str(e))
        rpc_error.set(True)
    except tg.ApiError:
        message.set("Terragen RPC API error")
        rpc_error.set(True)
        raise

def format_message(text):
    '''
    Splits a very long error message across two lines of the label widget

    Args:
        text (str): Text to be formatted

    Returns:
        formatted_text (str): Text formatted to fit in window
    '''
    formatted_text = text
    if len(text) >= 80:
        n = int(len(text) / 2)
        formatted_text = text[:n] + " \n" + text[n:]
    return formatted_text

# variables
error_message = tk.StringVar()
info_message = tk.StringVar()
rpc_error = tk.BooleanVar()
rpc_error.set(False)
rb_origin = tk.IntVar()
rb_origin.set(1)
rb_coordinates = tk.IntVar()
rb_coordinates.set(1)
message = tk.StringVar()

# frame1
r1 = tk.Radiobutton(frame1, text = '2m', variable=rb_origin, value=1)
r1.grid(row=1,column=0)
r2 = tk.Radiobutton(frame1, text = '20m', variable=rb_origin, value=2)
r2.grid(row=1,column=1)
r3 = tk.Radiobutton(frame1, text = '200m', variable=rb_origin, value=3)
r3.grid(row=1,column=2)
r4 = tk.Radiobutton(frame1, text = '2km', variable=rb_origin, value=4)
r4.grid(row=1,column=3)

label1 = tk.Label(frame1, text=" ")
label1.grid(row=2,columnspan=4)

button1 = tk.Button(frame1, text="Add landmark", command=add_landmark)
if platform.system() == "Windows":
    button1.config(bg="green")
    button1.config(fg="white")
button1.grid(row=3, columnspan=4)

# frame2
r5 = tk.Radiobutton(frame2, text = '2m', variable=rb_coordinates, value=1)
r5.grid(row=1, column=0)
r6 = tk.Radiobutton(frame2, text = '20m', variable=rb_coordinates, value=2)
r6.grid(row=1, column=1)
r7 = tk.Radiobutton(frame2, text = '200m', variable=rb_coordinates, value=3)
r7.grid(row=1, column=2)
r8 = tk.Radiobutton(frame2, text = '2km', variable=rb_coordinates, value=4)
r8.grid(row=1, column=3)

label2 = tk.Label(frame2, text="Copy coordinates to clipboard first!",fg="blue")
label2.grid(row=2,columnspan=4)

button2 = tk.Button(frame2, text="Add landmark", command=add_landmark_at)
if platform.system() == "Windows":
    button2.config(bg="blue")
    button2.config(fg="white")
button2.grid(row=3, columnspan=4)

# frame3
label3 = tk.Label(frame3, text="Messages: ", bg="#FFF9EC")
label3.grid(row=0, column=0, pady=5, sticky='w')
label4 = tk.Label(frame3, textvariable=message, bg="#FFF9EC")
label4.grid(row=1, column=0, stick='w',)

gui.mainloop()
