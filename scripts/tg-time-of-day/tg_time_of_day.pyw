from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import platform
import sunpos as sp
from datetime import datetime
import terragen_rpc as tg
import traceback

gui = Tk()
gui.title("tg_time_of_day.py")
gui.geometry("732x661" if platform.system() == "Darwin" else
             "560x600")
gui.config(bg="#89B2B9") # dark green colour

gui.rowconfigure(0,weight=1)
gui.rowconfigure(1,weight=1)
gui.rowconfigure(2,weight=1)
gui.rowconfigure(3,weight=1)
gui.columnconfigure(0,weight=1)
gui.columnconfigure(1,weight=2)

frame0 = LabelFrame(gui,text="Select sunlight node",relief=FLAT, padx=8,pady=4,bg="#B8DBD0")
frame1 = LabelFrame(gui,text="Enter time and location: ",relief=FLAT,padx=20,pady=10,bg="#B8DBD0")
frame2 = LabelFrame(gui,text="Last values plotted were: ",relief=FLAT,padx=10,pady=10,bg="#CBAE98")
frame3 = LabelFrame(gui,text="Location presets: ",relief=FLAT,padx=10,pady=10,bg="#B8DBD0")
frame4 = LabelFrame(gui,text="Adjust camera exposure",relief=FLAT,padx=8,pady=4,bg="#CDCB9A") # "#CD9AB1")
frame0.grid(row=0,column=0,padx=4,pady=4,sticky="WENS")
frame1.grid(row=1,column=0,padx=4,pady=4,rowspan=2,sticky='WENS')    
frame2.grid(row=3,column=0,padx=4,pady=4,columnspan=2,sticky='WENS')
frame3.grid(row=1,column=1,padx=4,pady=4,rowspan=2,sticky='WENS')
frame4.grid(row=0,column=1,padx=4,pady=4,sticky='WENS') # camera exposure frame

def show_error(text):
    error_message.set(text)

def popup_message(message_type,message_description):
    messagebox.showwarning(title=message_type, message = message_description)

def get_sunlight_nodes(): # return a list of sunlight paths in the project. could be empty.
    node_paths = []
    try:
        project = tg.root()
        node_ids = project.children_filtered_by_class("sunlight")
        for nodes in node_ids:            
            node_paths.append(nodes.path())
        return node_paths
    except ConnectionError as e:
        popup_message("Terragen RPC connection error: ",str(e))
        return node_paths
    except TimeoutError as e:
        popup_message("Terragen RPC timeout error: ", str(e))
        return node_paths
    except tg.ReplyError as e:
        popup_message("Terragen RPC server reply error: ", str(e))
        return node_paths
    except tg.ApiError:
        popup_message("Terragen RPC API error",traceback.format_exc())
        return node_paths
        raise

def toggle_terragen_sun(name):
    try:        
        node = tg.node_by_path(name) #returns None if sunlight no longer in project        
        try:
            x = node.get_param_as_int('enable')
        except AttributeError as err:
            show_error("Sunlight not in project. Refresh list.")
        else:
            if x == 1:
                node.set_param('enable',0)
            else:
                node.set_param('enable',1)
    except ConnectionError as e:
        popup_message("Terragen RPC connection error: ", str(e))
    except TimeoutError as e:
        popup_message("Terragen RPC timeout error: " , str(e))
    except tg.ReplyError as e:
        popup_message("Terragen RPC server reply error: " , str(e))
    except tg.ApiError:
        popup_message("Terragen RPC API error",traceback.format_exc())
        raise

def setTerragenSunHeadingAndElevation(name,values):
    try:
        node = tg.node_by_path(name) # set to None if selected sunlight is no longer in project
        try:
            node.set_param('heading',values[0])
            node.set_param('elevation',values[1])
        except AttributeError as err:
            show_error("Sunlight not in project. Refresh list.")
    except ConnectionError as e:
        popup_message("Terragen RPC connection error: " , str(e))
    except TimeoutError as e:
        popup_message("Terragen RPC timeout error: " , str(e))
    except tg.ReplyError as e:
        popup_message("Terragen RPC server reply error: " , str(e))
    except tg.ApiError:
        popup_message("Terragen RPC API error",traceback.format_exc())
        raise

# variables
system_time = datetime.now()
year = IntVar(gui,value = system_time.year)
month = IntVar(gui,value = system_time.month)
day = IntVar(gui,value = system_time.day)
hour = IntVar(gui,value = system_time.hour)
minute = IntVar(gui,value = system_time.minute)
second = IntVar(gui,value = system_time.second)
timezone = IntVar(gui,value = 8) # not updated by system_time yet
latitude = DoubleVar(gui,value = 34.052235)
longitude = DoubleVar(gui,value = -104.741667)
display_last_sunlight = StringVar()
display_when=StringVar()
display_location=StringVar()
azimuth = StringVar()
elevation = StringVar()
selected_sunlight = StringVar()
rID = StringVar()
# rNames = StringVar()
error_message = StringVar()
selected_location = StringVar()
preset_location = []
preset_latitude = []
preset_longitude = []
preset_timezone = []
display_latitude = StringVar()
display_longitude = StringVar()
display_timezone = StringVar()
sun_on_off = IntVar() # used?
selected_camera = StringVar() #camera in project
camera_ids = StringVar()
camera_names = StringVar()
exposure = IntVar()

def when_where():                
    when = [year.get(), month.get(), day.get(), hour.get(), minute.get(), second.get(),timezone.get()]
    location = [latitude.get(),longitude.get()]
    display_when.set(when)
    display_location.set(location)    
    results = sp.sunpos(when,location,True)    
    azimuth.set(results[0])
    elevation.set(results[1])
    setTerragenSunHeadingAndElevation(selected_sunlight.get(),results)    
    display_last_sunlight.set(selected_sunlight.get())

def get_presets():
    file = open('presets_latlong2.csv',"r")
    content = file.readlines()
    for line in content:
        x,y,z,a = line.strip().split(',')
        preset_location.append(x)
        preset_latitude.append(z) # lat lon switched in v2 of CSV
        preset_longitude.append(y)
        preset_timezone.append(a)
    file.close()

def set_latitude_longitude():
    v = presets_combobox.current()
    display_latitude.set(preset_latitude[v])
    display_longitude.set(preset_longitude[v])
    display_timezone.set(preset_timezone[v])
    latitude.set(preset_latitude[v])
    longitude.set(preset_longitude[v])
    timezone.set(preset_timezone[v])

def checkbox_sun():
    toggle_terragen_sun(selected_sunlight.get())

def update_sun_combobox_list():
    global sunlight_paths
    sunlight_paths = get_sunlight_nodes()
    suns_combobox.set(" ") # clears selected value ensuring nothing is displayed
    suns_combobox["values"] = sunlight_paths
    if len(sunlight_paths) > 0:
        suns_combobox.current(0)

def get_camera_nodes(): # return a list of camera node paths
    camera_paths = []
    camera_node_ids = []
    try:
        project = tg.root()
        camera_node_ids = project.children_filtered_by_class("camera")
        for nodes in camera_node_ids:            
            camera_paths.append(nodes.path())
        return camera_paths
    except ConnectionError as e:
        popup_message("Terragen RPC connection error: " , str(e))
        return camera_paths
    except TimeoutError as e:
        popup_message("Terragen RPC timeout error: " , str(e))
        return camera_paths
    except tg.ReplyError as e:
        popup_message("Terragen RPC server reply error: " , str(e))
        return camera_paths
    except tg.ApiError:
        popup_message("Terragen RPC API error",traceback.format_exc())
        return camera_paths
        raise

def update_camera_list():
    global camera_paths
    camera_paths = get_camera_nodes()
    cameras_combobox.set(" ") # clears list
    cameras_combobox['values'] = camera_paths
    if len(camera_paths) > 0:
        cameras_combobox.current(0)
    else:
        show_error("Camera nodes not found. ")

def apply_exposure():
    set_camera_exposure(selected_camera.get(),exposure.get())


def set_camera_exposure(selected_camera_path,exposure_value):
    try:
        node = tg.node_by_path(selected_camera_path) # set to None if selected sunlight is no longer in project
        try:
            node.set_param('light_exposure',exposure_value)
            # node.set_param('elevation',values[1])
        except AttributeError as err:
            show_error("Sunlight not in project. Refresh list.")
    except ConnectionError as e:
        popup_message("Terragen RPC connection error: " , str(e))
    except TimeoutError as e:
        popup_message("Terragen RPC timeout error: " , str(e))
    except tg.ReplyError as e:
        popup_message("Terragen RPC server reply error: " , str(e))
    except tg.ApiError:
        popup_message("Terragen RPC API error",traceback.format_exc())
        raise

# Main
sunlight_paths = get_sunlight_nodes()    # returns list of sunlight nodes
get_presets()
camera_paths = get_camera_nodes()

# Frame0 elements
suns_combobox = ttk.Combobox(frame0,textvariable=selected_sunlight)
suns_combobox["values"] = sunlight_paths
if len(sunlight_paths) > 0:
    suns_combobox.current(0)
else:
    show_error("No sunlight nodes in project or Terragen not running.")
suns_combobox.grid(row=0,column=0)

toggle_sun_button = Button(frame0,text="Sun on/off",bg='pink',command=checkbox_sun)
toggle_sun_button.grid(row=1,column=1,sticky="w",padx=4,pady=4)
refresh_sun_button = Button(frame0,text="Refresh list",command=update_sun_combobox_list)
refresh_sun_button.grid(row=0,column=1,sticky="w",padx=4)

# Frame1 and 2 elements
year_label = Label(frame1,text = 'Year',bg="#B8DBD0")
month_label = Label(frame1,text = 'Month',bg="#B8DBD0")
day_label = Label(frame1,text = 'Day',bg="#B8DBD0")
hour_label = Label(frame1,text = 'Hour',bg="#B8DBD0")
minute_label = Label(frame1,text = 'Minute',bg="#B8DBD0")
second_label = Label(frame1,text = 'Second',bg="#B8DBD0")
timezone_label = Label(frame1,text = 'Timezone',bg="#B8DBD0")
latitude_label = Label(frame1,text='Latitude (N)',bg="#B8DBD0")
longitude_label = Label(frame1,text='Longitude (W)',bg="#B8DBD0")
# null_label = Label(frame1,text=" ")

year_label.grid(row=0,column=0, sticky='w')
month_label.grid(row=1, column=0,sticky='w')
day_label.grid(row=2, column=0,sticky='w')
hour_label.grid(row=3, column=0,sticky='w')
minute_label.grid(row=4, column=0,sticky='w')
second_label.grid(row=5, column=0,sticky='w')
timezone_label.grid(row=6, column=0,sticky='w')
latitude_label.grid(row=7,column=0,sticky='w')
longitude_label.grid(row=8,column=0,sticky='w')
# null_label.grid(row=9,columnspan=2)

last_sun_label = Label(frame2,text='Node: ',bg="#CBAE98")
last_sun2_label = Label(frame2,textvariable=display_last_sunlight,bg="#CBAE98")
when_label = Label(frame2,text='Date & time: ',bg="#CBAE98")
when2_label = Label(frame2,textvariable=display_when,bg="#CBAE98")
location_label = Label(frame2,text='Location: ',bg="#CBAE98")
location2_label = Label(frame2,textvariable=display_location,bg="#CBAE98")
azimuth_label = Label(frame2,text='Azimuth:',bg="#CBAE98")
azimuth2_label = Label (frame2,textvariable=azimuth,bg="#CBAE98")
elevation_label = Label(frame2,text='Elevation:',bg="#CBAE98")
elevation2_label = Label(frame2,textvariable=elevation,bg="#CBAE98")
error_message_label = Label(frame2,textvariable=error_message,fg='red',bg="#CBAE98")

last_sun_label.grid(row=12,column=0,sticky='w')
last_sun2_label.grid(row=12,column=1,sticky='w')
when_label.grid(row=13, column=0,sticky='w')
when2_label.grid(row=13, column=1,sticky='w')
location_label.grid(row=14,column=0,sticky='w')
location2_label.grid(row=14,column=1,sticky='w')
azimuth_label.grid(row=15,column=0,sticky='w')
azimuth2_label.grid(row=15,column=1,sticky='w')
elevation_label.grid(row=16,column=0,sticky='w')
elevation2_label.grid(row=16,column=1,sticky='w')
error_message_label.grid(row=17,columnspan=2,sticky='w')

# Sliders
year_slider = Scale(frame1,from_= 1900, to = 2099,variable=year,orient=HORIZONTAL,showvalue=0)
month_slider = Scale(frame1,from_= 1, to = 12,variable=month,orient=HORIZONTAL,showvalue=0)
day_slider = Scale(frame1,from_= 1, to = 31,variable=day,orient=HORIZONTAL,showvalue=0)
hour_slider = Scale(frame1,from_= 0, to = 23,variable=hour,orient=HORIZONTAL,showvalue=0)
minute_slider = Scale(frame1,from_= 0,to = 59,variable=minute,orient=HORIZONTAL,showvalue=0)
second_slider = Scale(frame1,from_= 0, to = 59,variable=second,orient=HORIZONTAL,showvalue=0)
timezone_slider = Scale(frame1,from_= -13, to = 13,variable=timezone,orient=HORIZONTAL,showvalue=0)

year_slider.grid(row=0,column=1)
month_slider.grid(row=1,column=1)
day_slider.grid(row=2,column=1)
hour_slider.grid(row=3,column=1)
minute_slider.grid(row=4,column=1)
second_slider.grid(row=5,column=1)
timezone_slider.grid(row=6,column=1)

# Entry
year_entry = Entry(frame1, textvariable = year,width=6)
month_entry = Entry(frame1, textvariable = month,width=6)
day_entry = Entry(frame1, textvariable = day,width=6)
hour_entry = Entry(frame1, textvariable = hour,width=6)
minute_entry = Entry(frame1, textvariable = minute,width=6)
second_entry = Entry(frame1, textvariable = second,width=6)
timezone_entry = Entry(frame1, textvariable = timezone,width=6)
latitude_entry = Entry(frame1, textvariable = latitude,width=16)
longitude_entry = Entry(frame1, textvariable = longitude,width=16)

year_entry.grid(row=0,column=3,sticky="w")
month_entry.grid(row=1,column=3)
day_entry.grid(row=2,column=3)
hour_entry.grid(row=3,column=3)
minute_entry.grid(row=4,column=3)
second_entry.grid(row=5,column=3)
timezone_entry.grid(row=6, column = 3)
latitude_entry.grid(row=7, column =1)
longitude_entry.grid (row=8,column =1)    

# APPLY Button
apply_button = Button(frame1,text='Apply to Sun',bg='yellow',command=when_where)
apply_button.grid(row=10,column=1,sticky="w",columnspan=2,padx=2,pady=8)

# Frame 3 elements
presets_combobox = ttk.Combobox(frame3,textvariable=selected_location)
presets_combobox["values"]=preset_location
presets_combobox.current(16)
presets_combobox.grid(row=0,column=1,sticky='w')

preset_location_label = Label(frame3,text="Location: ",bg="#B8DBD0")
preset_latitude_label = Label(frame3,text="Latitude:",bg="#B8DBD0")
preset_longitude_label = Label(frame3,text="Longitude:",bg="#B8DBD0")
preset_timezone_label = Label(frame3,text="Timezone:",bg="#B8DBD0")
preset_display_latitude_label = Label(frame3,textvariable=display_latitude,bg="#B8DBD0")
preset_display_longitude_label = Label(frame3,textvariable=display_longitude,bg="#B8DBD0")
preset_display_timezone_label = Label (frame3, textvariable=display_timezone,bg="#B8DBD0")
apply_preset_button = Button(frame3,text="Apply Preset",command=set_latitude_longitude)

preset_location_label.grid(row=0,column=0,sticky='w')
preset_latitude_label.grid(row=1,column=0,sticky='w')
preset_longitude_label.grid(row=2,column=0,sticky='w')
preset_timezone_label.grid(row=3,column=0,sticky='w')
preset_display_latitude_label.grid(row=1,column=1,sticky='w')
preset_display_longitude_label.grid(row=2,column=1,sticky='w')
preset_display_timezone_label.grid(row=3,column=1,sticky='w')
apply_preset_button.grid(row=5,column=1,pady=5,sticky='w')

# Frame 4 elements
cameras_combobox = ttk.Combobox(frame4,textvariable=selected_camera) #,postcommand=update_camera_list)
cameras_combobox["values"]=camera_paths
if len(camera_paths) > 0:
    cameras_combobox.current(0)
else:
    show_error("No camera nodes in project or Terragen not running.")
cameras_combobox.grid(row=0,column=0)

# cameras_label = Label(frame4,text="Cameras: ")
exposure_label = Label (frame4,text="Exposure: ",bg="#CDCB9A")
exposure_slider_label = Scale(frame4,from_= 0, to = 10,variable=exposure,orient=HORIZONTAL,showvalue=1,bg="#CDCB9A")
# exposure_entry = Entry(frame4,textvariable = exposure, width =6)
apply_exposure_button = Button(frame4,text="Apply exposure",bg='#A5A8EC',command=apply_exposure) # was pink
refresh_camera_button = Button(frame4,text="Refresh list",command=update_camera_list )

# cameras_label.grid(row=0,column=0,sticky='w')
exposure_label.grid(row=1,column=0,sticky='se')
exposure_slider_label.grid(row=1,column=1,sticky='w')
# exposure_entry.grid(row=1,column=2,sticky="sw")
apply_exposure_button.grid(row=3,column=1,padx=4,pady=2,sticky="w")
refresh_camera_button.grid(row=0,column=1,padx=4,sticky="w")

gui.mainloop()
