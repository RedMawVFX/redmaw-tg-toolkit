''' 
Toggles the crop region between on and off for all renderers in project.
'''
import traceback
from tkinter import messagebox
import terragen_rpc as tg

def popup_warning(message_title, message_description):
    messagebox.showwarning(message_title, message_description)

try:
    project = tg.root()
    renderers = project.children_filtered_by_class("render")
    if not renderers:
        messagebox.showwarning("Terragen Warning", "No renderers in project.")

    for render in renderers:
        prop = render.get_param("do_crop_region")
        prop = "0" if prop == "1" else "1"
        render.set_param("do_crop_region",prop)

except ConnectionError as e:
    popup_warning("Terragen RPC connection error",str(e))
except TimeoutError as e:
    popup_warning("Terragen RPC timeout error",str(e))
except tg.ReplyError as e:
    popup_warning("Terragen RPC reply error",str(e))
except tg.ApiError:
    popup_warning("Terragen RPC API error",traceback.format_exc())
