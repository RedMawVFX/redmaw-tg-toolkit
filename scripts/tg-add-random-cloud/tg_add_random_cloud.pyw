import sys
import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import random
import traceback
import terragen_rpc as tg

# Add the parent directory (scripts) to sys.path in order to import from commons
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from commons.node_network_layout import auto_position_node

# terragen cloud layer presets via add cloud button (21 possibilities from 15 layers)
# 0 = Hi-level Cirrus 2d (v2)
# 1 - Hi-level Cirrocumulus (easy)
# 2 - Mid-level Generic (v3)
# 3 - Mid-level Altocumulus Castellanus Small (easy) (two models)
# 4 - Mid-level Altocumulus Castellanus Large (easy) (two models)
# 5 - Mid-level AltoStratocumulus Small (easy)
# 6 - Mid-level AltoStratocumulus Large (easy)
# 7 - Low-level Generic (v3)
# 8 - Low-level Cumulus Small (easy) (two models)
# 9 - Low-level Cumulus Medium (easy) (two models)
#10 - Low-level Cumulus Large (easy) (two models)
#11 - Low-level Stratocumulus (easy)
#12 - v2 cloud from quick node palette
#13 - v3 cloud from quick node palette
#14 - Easy cloud from quick node palette (two models)

# list of parameter by class
# v2 clouds: class, cloud alt, depth, density , rendering method
# v3 clouds: class, cloud alt, depth, radius, density
# easy clouds: class, type, model, coverage, variation, growth, base alt, depth, radius, density

def get_cloud_params_by_class(x): # returns list of preset cloud layer values from the cloud layer dictionary below
    cloud_from_dict = cloud_layer_dict[x]
    clouds_with_random_altitudes = [0,2,7]
    clouds_with_random_models = [3,4,8,9,10,14]
    if x in clouds_with_random_altitudes:
        if x == 0:
            random_altitude = get_random_value(10000,15000)
            cloud_from_dict[1] = random_altitude
        elif x == 2:
            random_altitude = get_random_value(4000,4500)
            cloud_from_dict[1] = random_altitude
        elif x == 7:
            random_altitude = get_random_value(1800,2300)
            cloud_from_dict[1] = random_altitude
    if x in clouds_with_random_models:
        random_model = get_random_value(0,1)
        cloud_from_dict[2] = random_model
    return cloud_from_dict

def get_random_value(min,max): # returns a string for random value between min and max
    string_of_integer = str(random.randint(min,max))
    return string_of_integer

def get_connected_node(node,path): # returns node id of node assigned to atmosphere shader or none
    if path == "":
        return None
    # check for forward slash
    if path[0] == "/":
        # test to try to find node at root level
        test_path = path
        test_id = tg.node_by_path(test_path)
        if test_id:
            return test_id
    # try to find child
    test_path = node.path() + "/" + path
    test_id = tg.node_by_path(test_path)
    if test_id:
        return test_id
    # try to find sibling
    test_path = node.parent_path() + "/" + path
    test_id = tg.node_by_path(test_path)
    if test_id:
        return test_id
    return None

def add_cloud_to_project(add_cloud): # adds a cloud layer to the project, even if there are no planets.
    atmo_shader_name = ""
    atmo_shader_id = None
    try:
        project = tg.root()
        planets = project.children_filtered_by_class("planet")
        if planets:
            for i in planets:
                atmo_shader_name = i.get_param('atmosphere_shader')
                atmo_shader_id = get_connected_node(i,atmo_shader_name)
                break # only use the first planet in the project at the root level

        if atmo_shader_id:
            new_parent = atmo_shader_id.parent()
        else:
            new_parent = project

        new_cloud_id = tg.create_child(new_parent,add_cloud[0])

        if add_cloud[0] == "cloud_layer_v2": # v2 clouds - class, cloud alt, depth, density, rendering method, input node
            new_cloud_id.set_param("cloud_altitude",add_cloud[1])
            new_cloud_id.set_param("cloud_depth",add_cloud[2])
            new_cloud_id.set_param("cloud_density",add_cloud[3])
            new_cloud_id.set_param("rendering_method",add_cloud[4])
        elif add_cloud[0] == "cloud_layer_v3": # v3 clouds - class, cloud alt, depth, radius, density, input node
            new_cloud_id.set_param("cloud_altitude",add_cloud[1])
            new_cloud_id.set_param("cloud_depth",add_cloud[2])
            new_cloud_id.set_param("radius",add_cloud[3])
            new_cloud_id.set_param("cloud_density",add_cloud[4])
        elif add_cloud[0] == "easy_cloud": # easy clouds - class, type, model, coverage, variation, growth, base alt, depth, radius, density, input node
            new_cloud_id.set_param("input_node",atmo_shader_name)
            new_cloud_id.set_param("local_sphere_radius",add_cloud[8])
            new_cloud_id.set_param("easycloud_type",add_cloud[1])
            new_cloud_id.set_param("easycloud_model",add_cloud[2])
            new_cloud_id.set_param("easycloud_coverage",add_cloud[3])
            new_cloud_id.set_param("easycloud_variation",add_cloud[4])
            new_cloud_id.set_param("easycloud_growth",add_cloud[5])
            new_cloud_id.set_param("cloud_depth",add_cloud[7])
            new_cloud_id.set_param("cloud_density",add_cloud[9])

        new_cloud_id.set_param("input_node",atmo_shader_name) # set cloud's main input node to previous node assigned to planet's atmosphere shader input

        auto_position_node(new_cloud_id, add_cloud[0])

        if planets:
            planets[0].set_param("atmosphere_shader",new_cloud_id.name()) # set planet atmosphere shader to this cloud node

    except ConnectionError as e:
        popup_warning("Terragen RPC connection error",str(e))
    except TimeoutError as e:
        popup_warning("Terragen RPC timeout error",str(e))
    except tg.ReplyError as e:
        popup_warning("Terragen RPC reply error",str(e))
    except tg.ApiError:
        popup_warning("Terragen RPC API error",traceback.format_exc())

def popup_warning(title,message):
    messagebox.showwarning(title=title,message=message)

cloud_layer_dict = {
    0 : ["cloud_layer_v2","10000","10","0.01","0"],
    1 : ["easy_cloud","3","1","1.0","0.5","1","8000","100","150000","0.001"],
    2 : ["cloud_layer_v3","4000","150","50000","0.1"],
    3 : ["easy_cloud","2","1","0.4","0.5","0.5","4000","2000","100000","0.05"],
    4 : ["easy_cloud","2","1","0.4","0.5","0.5","4000","6000","200000","0.05"],
    5 : ["easy_cloud","3","1","0.4","0.5","0.5","4000","500","100000","0.05"],
    6 : ["easy_cloud","3","1","0.4","0.5","0.5","4000","1500","100000","0.05"],
    7 : ["cloud_layer_v3","1800","500","50000","0.05"],
    8 : ["easy_cloud","1","1","0.3","0'0","0.5","1500","1000","50000","0.1"],
    9 : ["easy_cloud","1","1","0.3","0'0","0.5","1500","2500","50000","0.1"],
    10 : ["easy_cloud","1","1","0.3","0'0","0.5","1500","6000","50000","0.1"],
    11 : ["easy_cloud","3","1","0.3","0.0","0.5","1500","1500","50000","0.1"],
    12 : ["cloud_layer_v2","1750","500","0.01","1"],
    13 : ["cloud_layer_v3","1750","500","50000","0.1"],
    14 : ["easy_cloud","1","1","0.5","0.5","0.5","3000","1000","50000","0.1"]
}

# main
random_cloud_type = random.randint(0,14) # randomly pick a type of cloud layer
cloud_layer_params = get_cloud_params_by_class(random_cloud_type) # get the preset list of parameters
add_cloud_to_project(cloud_layer_params) # send string to terragen via rpc and add cloud
