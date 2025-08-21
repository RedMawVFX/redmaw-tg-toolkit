from tkinter import messagebox
import terragen_rpc as tg

PADDING = 60

assume_node_in_group_dict = {
    "cloud_layer_v2": "Atmosphere",
    "cloud_layer_v3": "Atmosphere",
    "easy_cloud": "Atmosphere",
    "sunlight": "Lighting",
    "camera": "Cameras",
    "render": "Renderers",
    "lake": "Water",
    "water_shader": "Water",
    "null": "Objects",
    "bounding_box": "Objects"
}

def message_info(title, message):
    messagebox.showinfo(title, message)

def safe_rpc_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except ConnectionError as e:
        message_info("RPC Message", "Terragen RPC Connection error: " + str(e))
    except TimeoutError as e:
        message_info("RPC Message", "Terragen RPC timeout error: " + str(e))
    except tg.ReplyError as e:
        message_info("RPC Message", "Terragen RPC server reply error: " + str(e))
    except tg.ApiError:
        message_info("RPC Message", "Terragen RPC API error")
        raise

def parse_vector(vec_str):
    """Parses a string like '320 -50 0' into a tuple of floats (x, y, z)."""
    return tuple(map(float, vec_str.split()))

def get_node_network_bounds(nodes_in_context):
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    for node in nodes_in_context:
        pos = parse_vector(safe_rpc_call(node.get_param, "gui_node_pos"))
        x, y = pos[0], pos[1]

        size = parse_vector(safe_rpc_call(node.get_param, "gui_node_size"))
        if size:
            width, height = size[0] * 0.5, size[1] * 0.5
            x1, y1 = x - width, y - width
            x2, y2 = x + width, y + width
        else:
            x1 = x2 = x
            y1 = y2 = y

        min_x = min(min_x, x1)
        min_y = min(min_y, y1)
        max_x = max(max_x, x2)
        max_y = max(max_y, y2)

    return (min_x, min_y, max_x, max_y)

def get_nodes_in_group_except_for(nodes_to_exclude: list, group_name, context=None):
    '''returns a list of child nodes in group_name excluding any in nodes_to_exclude'''
    excluded_names = {n.name() for n in (nodes_to_exclude or [])}
    return [
        child for child in (safe_rpc_call(context.children) or [])
        if safe_rpc_call(child.get_param, "gui_group") == group_name
        and child.name() not in excluded_names
    ]

def get_children_in_context_except_for(nodes_to_exclude: list, context) -> list:
    ''' returns a list of child nodes within the context excluding any nodes
        in the nodes_to_exclude list.
    '''
    children = context.children()
    return [child for child in children if child not in nodes_to_exclude]

def get_node_by_name_from_context(node_name, context):
    '''Returns the first child node whose "name" param matches node_name'''
    return next(
        (child for child in (safe_rpc_call(context.children) or [])
         if safe_rpc_call(child.get_param, "name") == node_name),
        None
    )

def get_node_with_name_from_class(node_name, class_name, context=None): # not used but useful
    '''Returns the first child of the given class with the matching name.'''
    return next(
        (child for child in (context.children_filtered_by_class(class_name) or [])
         if safe_rpc_call(child.get_param, "name") == node_name),
        None
    )

def calc_new_pos(min_x, min_y, max_x, max_y, location="bottom left"):
    match location:
        case "bottom left":
            new_x = min_x
            new_y = min_y - PADDING
        case "top right":
            new_x = max_x + PADDING
            new_y = max_y
        case "top left":
            new_x = min_x - PADDING
            new_y = max_y
        case "bottom right":
            new_x = max_x + PADDING
            new_y = min_y - PADDING

    return f"{new_x} {new_y} 0"

def calc_bottom(other_nodes_in_group):
    '''
    Determines and returns the bottom-most gui node postition in the group
    '''
    bottom_most_pos = None
    min_y = float('inf')

    for node in other_nodes_in_group:
        pos_str = safe_rpc_call(node.get_param, "gui_node_pos")
        parts = pos_str.split()
        if len(parts) < 2:
            continue  # skip invalid

        try:
            y = float(parts[1])  # Y is the second part
        except ValueError:
            continue  # skip bad values

        if y < min_y:
            min_y = y
            bottom_most_pos = pos_str

    return bottom_most_pos

def pad_pos(gui_pos):
    pos = parse_vector(gui_pos)
    x, y = pos[0], pos[1]
    y -= PADDING
    return f"{x} {y} 0"

def repo_group(group):
    gui_node_pos = safe_rpc_call(group.get_param, "gui_node_pos")
    pos = parse_vector(gui_node_pos)
    y = pos[1]
    y = y - (PADDING * 0.5)
    new_gui_node_pos = f"{pos[0]} {y} 0"
    safe_rpc_call(group.set_param, "gui_node_pos", new_gui_node_pos)

def resize_group(group):
    gui_node_size = safe_rpc_call(group.get_param, "gui_node_size")
    if gui_node_size:
        siz = parse_vector(gui_node_size)
        sy = siz[1]
        sy = sy + (PADDING) # was 05
        new_gui_node_size = f"{siz[0]} {sy} 1"
        safe_rpc_call(group.set_param, "gui_node_size", new_gui_node_size)

def assign_group_if_needed(node, class_name):
    '''Assigns a gui_group if one can be assumed from class_name.'''
    group_name = assume_node_in_group_dict.get(class_name)
    if group_name:
        safe_rpc_call(node.set_param, "gui_group", group_name)
    return group_name

def create_group_if_missing(group_name, node, context):
    '''Creates a new group node and positions it based on existing children.'''
    group_node = safe_rpc_call(tg.create_child, context, "group")
    safe_rpc_call(group_node.set_param, "name", group_name)
    # need a list of child nodes in order to determine boundries
    other_children = get_children_in_context_except_for([node, group_node], context)
    min_x, min_y, max_x, max_y = get_node_network_bounds(other_children)
    new_pos = calc_new_pos(min_x, min_y, max_x, max_y, "bottom left")
    safe_rpc_call(group_node.set_param, "gui_node_pos", new_pos)

    return group_node

def position_node_in_group(node, group_node, group_name, context):
    '''Positions the node below other nodes in the same group.'''
    other_nodes_in_group = get_nodes_in_group_except_for([node], group_name, context)

    if not other_nodes_in_group:
        bottom_pos = safe_rpc_call(group_node.get_param, "gui_node_pos")
    else:
        bottom_pos = calc_bottom(other_nodes_in_group)

    padded_pos = pad_pos(bottom_pos)
    safe_rpc_call(node.set_param, "gui_node_pos", padded_pos)

    repo_group(group_node)
    resize_group(group_node)

def position_node_outside_group(node, context):
    '''Positions the node outside of a group, below the node network.'''
    other_children = get_children_in_context_except_for([node], context)
    min_x, min_y, max_x, max_y = get_node_network_bounds(other_children)
    new_pos = calc_new_pos(min_x, min_y, max_x, max_y, "bottom left")
    safe_rpc_call(node.set_param, "gui_node_pos", new_pos)

def auto_position_node(node, class_name):
    '''
    Handler to position the node in the node network.
    The 3 arguments were previously used to create the node.
    
    Args:
        node <obj>: node id
        class_name "str": class of node, i.e. "camera"
        context <obj>: node id of parent object, i.e. root level or internal node network
    '''
    parent_context = safe_rpc_call(node.parent)
    root_context = safe_rpc_call(tg.root)
    context = parent_context or root_context

    gui_group_name = safe_rpc_call(node.get_param, "gui_group") # is node part of a group?
    if not gui_group_name and context == root_context: # only query assumed dict if parent is root
        gui_group_name = assign_group_if_needed(node, class_name) # does class have an assumed group

    if gui_group_name:
        group_node = get_node_by_name_from_context(gui_group_name, context) # assigned group exist?
        if not group_node:
            group_node = create_group_if_missing(gui_group_name, node, context) # create a new group

        position_node_in_group(node, group_node, gui_group_name, context) # at bottom of group
    else:
        position_node_outside_group(node, context) # position node outside node network boundaries

