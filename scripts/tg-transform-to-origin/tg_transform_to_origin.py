from tkinter import *
import terragen_rpc as tg

# Window
gui = Tk()
gui.title("tg_transform_to_origin")
gui.geometry("800x300")

gui.columnconfigure(0,weight=1)
gui.rowconfigure(0,weight=1)
gui.rowconfigure(1,weight=1)

# Frames
frame1 = LabelFrame(gui,text="Instructions",relief=FLAT,bg="#A6CAE4")
frame1.grid(row=0,column=0,sticky='wens')
frame2 = LabelFrame(gui,relief=FLAT,bg="#B2B4B8")
frame2.grid(row=1,column=0,sticky='wens')

def main():
    selected_nodes = are_nodes_selected()
    if len(selected_nodes)>0:
        raw_clipboard_contents = get_clipboard_contents()
        if len(raw_clipboard_contents) > 0:
            verified_contents = verify_clipboard_contents(raw_clipboard_contents) # returns xyz values as a list             
            if len(verified_contents) > 0:
                offset_coordinates = []
                invert_x = str(float(verified_contents[0])* -1)
                invert_z = str(float(verified_contents[2])* -1)
                offset_coordinates = (invert_x + ' 0.0 ' + invert_z)
                add_transform_input_shader(selected_nodes[0],offset_coordinates)
        
def are_nodes_selected():
    try:
        node=[]
        node = tg.current_selection()
        if node == []:
            message.set("Please select a node in the Node Network view for the Transform Input shader to follow.")
    except ConnectionError as e:
        rpc_error.set(True)
        formatted_message = format_message("Terragen RPC connection error: " + str(e))       
        message.set(formatted_message)                
    except TimeoutError as e:
        message.set("Terragen RPC timeout error: " + str(e))
        rpc_error.set(True)
    except tg.ReplyError as e:        
        message.set("Terragen RPC server reply error: " + str(e))
        rpc_error.set(True)
    except tg.ApiError:
        message.set("Terragen RPC API error.")        
        rpc_error.set(True)
        raise
    return(node)    

def get_clipboard_contents(): # returns raw clipbord if any    
    clipboard_contents = gui.clipboard_get()
    return(clipboard_contents)

def verify_clipboard_contents(x):
    coordinates = []
    if x[0:4] != "xyz:":
        message.set("Invalid coordinates in the clipboard.  See step 1 above.")
    else:
        trimmed_clipboard_data = x[5:]
        coordinates = trimmed_clipboard_data.split(",")
    return (coordinates)    

def add_transform_input_shader(first_selected_node,offset_coordinates):
    try:
        project = tg.root()
        new_transform = tg.create_child(project,'transform_input_shader')
        transform_main_input = first_selected_node.name()
        new_transform.set_param('input_node', transform_main_input)
        new_transform.set_param('translate','1')
        new_transform.set_param('translate_by',offset_coordinates)
        message.set("Added Transform Input shader to " + transform_main_input + " with offset coordinates " + offset_coordinates)
        rpc_error.set(False)
    except ConnectionError as e:
        rpc_error.set(True)
        formatted_message = format_message("Terragen RPC connection error: " + str(e))       
        message.set(formatted_message)                
    except TimeoutError as e:
        message.set("Terragen RPC timeout error: " + str(e))
        rpc_error.set(True)
    except tg.ReplyError as e:        
        message.set("Terragen RPC server reply error: " + str(e))
        rpc_error.set(True)
    except tg.ApiError:
        message.set("Terragen RPC API error.")        
        rpc_error.set(True)
        raise

# Splits a very long error message across two lines of the label widget
def format_message(text):
    formatted_text = text    
    if len(text) >= 80:
        n = int(len(text) / 2)
        formatted_text = text[:n] + " \n" + text[n:]    
    return(formatted_text)

# variables
rpc_error = BooleanVar(gui,False)
message = StringVar()

# Transform input with offset coordinates
label1 = Label(frame1,text="1. In the 3D Preview, right-click above a location and select Copy Coordinates.",bg="#A6CAE4",padx=5).grid(row=0,column=0,sticky='w')
label2 = Label(frame1, text="2. In the Node Network, select a node to be used as the Main input for a new Transform Input shader.",bg="#A6CAE4",padx=5).grid(row=1,column=0,sticky='w')
label3 = Label(frame1, text="3. Click the Apply Offset button below.",bg="#A6CAE4",padx=5).grid(row=2,column=0,sticky='w')
button11 = Button(frame1,text="Apply Offset",bg='#D3C19E',command=main,padx=5).grid(row=3,column=0,padx=20,pady=5,sticky='w')
label4 = Label(frame1, text="4. In the Node Network, connect the output of the Transform Input shader to the Main input of a downstream node like the Compute Terrain.",bg="#A6CAE4",padx=5).grid(row=4,column=0,sticky='w')

# Message section
label5 = Label(frame2,text="Messages: ",bg="#B2B4B8").grid(row=0,column=0,padx=5,sticky='w')
Label6 = Label(frame2,textvariable=message,bg="#B2B4B8").grid(row=1,column=0,padx=5)
Label7 = Label(frame2,text=" ",bg="#B2B4B8").grid(row=2,column=0) # blank line at end

gui.mainloop()
