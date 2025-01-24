from tkinter import *
import terragen_rpc as tg

gui = Tk()
gui.title("tg_sunlight01_heading_elevation")
gui.geometry("460x320")

frame1 = LabelFrame(gui,text="Set Sunlight01 heading in degrees ",padx=22,pady=10)
frame2 = LabelFrame(gui,text="Set Sunlight01 elevation in degrees",padx=5,pady=5)
frame3 = LabelFrame(gui,relief=FLAT,bg="#FFF9EC") # Errors and messages

frame1.grid(row=1,column = 0,padx=5)
frame2.grid(row=3,column = 0,padx=5)
frame3.grid(row=4,column = 0,columnspan=4,sticky='nsew')

def rpc_sun_heading(heading):
    try:        
        node = tg.node_by_path('/Sunlight 01')
        if node:
            node.set_param('heading',str(heading))
            rpc_error.set(False)
        else:
            show_operation_message("Sunlight 01 not found.  Add or rename a Sunlight node.")
            rpc_error.set(True)        
    except ConnectionError as e:
        formatted_operation_message = format_message("Terragen RPC connection error: " + str(e))        
        show_operation_message(formatted_operation_message)
        rpc_error.set(True)        
    except TimeoutError as e:
        show_operation_message("Terragen RPC timeout error: " + str(e))
        rpc_error.set(True)
    except tg.ReplyError as e:
        show_operation_message("Terragen RPC server reply error: " + str(e))
        rpc_error.set(True)
    except tg.ApiError:
        show_operation_message("Terragen RPC API error")
        rpc_error.set(True)
        raise

def rpc_sun_elevation(elevation):
    try:        
        node = tg.node_by_path('/Sunlight 01') 
        if node:
            node.set_param('elevation',str(elevation))   
            rpc_error.set(False)
        else:    
            show_operation_message("Sunlight 01 not found.  Add or rename a Sunlight node.")
            rpc_error.set(True)
    except ConnectionError as e:
        rpc_error.set(True)
        formatted_operation_message = format_message("Terragen RPC connection error: " + str(e))       
        show_operation_message(formatted_operation_message)                
    except TimeoutError as e:
        show_operation_message("Terragen RPC timeout error: " + str(e))
        rpc_error.set(True)
    except tg.ReplyError as e:
        show_operation_message("Terragen RPC server reply error: " + str(e))
        rpc_error.set(True)
    except tg.ApiError:
        show_operation_message("Terragen RPC API error")
        rpc_error.set(True)
        raise

def set_sun_heading(heading):    
    rpc_sun_heading(heading)
    if rpc_error.get() == False:
        operation_message.set("Sunlight 01 heading set to "+ str(heading))       

def set_sun_elevation():
    rpc_sun_elevation(sun_elevation.get())
    if rpc_error.get() == False:
        operation_message.set("Sunlight 01 elevation set to " + str(sun_elevation.get()))       

def show_operation_message(text):
    operation_message.set(text)

# Splits a very long error message across two lines of the label widget
def format_message(text):    
    formatted_text = text    
    if len(text) >= 80:
        n = int(len(text) / 2)
        formatted_text = text[:n] + " \n" + text[n:]    
    return(formatted_text)

# Variables
rpc_error = BooleanVar(gui,False)
sun_elevation = IntVar()
operation_message = StringVar()

# Sunlight heading section
button1 = Button(frame1,text="0",command=lambda: set_sun_heading(0)).grid(row=0,column=0,padx=5,pady=5)
button2 = Button(frame1,text="15",command=lambda: set_sun_heading(15)).grid(row=0,column=1,padx=5,pady=5)
button3 = Button(frame1,text="22.5",command=lambda: set_sun_heading(22.5)).grid(row=0,column=2,padx=5,pady=5)
button4 = Button(frame1,text="45",command=lambda: set_sun_heading(45)).grid(row=0,column=3,padx=5,pady=5)
button5 = Button(frame1,text="60",command=lambda: set_sun_heading(60)).grid(row=0,column=4,padx=5,pady=5)
button6 = Button(frame1,text="75",command=lambda: set_sun_heading(75)).grid(row=0,column=5,padx=5,pady=5)
button7 = Button(frame1,text="90",command=lambda: set_sun_heading(90)).grid(row=0,column=6,padx=5,pady=5)
button8 = Button(frame1,text="115",command=lambda: set_sun_heading(115)).grid(row=0,column=7,padx=5,pady=5)
button9 = Button(frame1,text="130",bg="cyan",command=lambda: set_sun_heading(130)).grid(row=0,column=8,padx=5,pady=5)
button10 = Button(frame1,text="145",command=lambda: set_sun_heading(145)).grid(row=0,column=9,padx=5,pady=5)

button11 = Button(frame1,text="160",command=lambda: set_sun_heading(160)).grid(row=1,column=0,padx=5,pady=5)
button12 = Button(frame1,text="180",command=lambda: set_sun_heading(180)).grid(row=1,column=1,padx=5,pady=5)
button13 = Button(frame1,text="195",command=lambda: set_sun_heading(195)).grid(row=1,column=2,padx=5,pady=5)
button14 = Button(frame1,text="205",command=lambda: set_sun_heading(205)).grid(row=1,column=3,padx=5,pady=5)
button15 = Button(frame1,text="240",command=lambda: set_sun_heading(240)).grid(row=1,column=4,padx=5,pady=5)
button16 = Button(frame1,text="270",command=lambda: set_sun_heading(270)).grid(row=1,column=5,padx=5,pady=5)
button17 = Button(frame1,text="300",command=lambda: set_sun_heading(300)).grid(row=1,column=6,padx=5,pady=5)
button18 = Button(frame1,text="315",command=lambda: set_sun_heading(315)).grid(row=1,column=7,padx=5,pady=5)
button19 = Button(frame1,text="330",command=lambda: set_sun_heading(330)).grid(row=1,column=8,padx=5,pady=5)


# Sunlight elevation section
slider1 = Scale(frame2,from_= -90, to = 90, variable=sun_elevation,orient=HORIZONTAL,showvalue=0,length=360).grid(row=0,column=0,padx=10,pady=5)
e1 = Entry(frame2,textvariable=sun_elevation,width=6).grid(row=0,column=1)
button9 = Button(frame2,text="Apply Elevation",bg='yellow',command=set_sun_elevation).grid(row=1,column=0,padx=5,pady=5)

# Message section
label3 = Label(frame3,text="Messages: ",bg="#FFF9EC").grid(row=0,column=0,pady=5,sticky='w')
Label4 = Label(frame3,textvariable=operation_message,bg="#FFF9EC").grid(row=1,column=0,stick='w',)
Label5 = Label(frame3,text=" ",bg="#FFF9EC").grid(row=2,column=0,pady=5,sticky='w') # blank line at end

gui.mainloop()
