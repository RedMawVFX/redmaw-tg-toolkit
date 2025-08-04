import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

CUBEMAP_FACES = [
    ("+X", ["right"]),
    ("-X", ["left"]),
    ("+Y", ["top", "up"]),
    ("-Y", ["bottom", "down"]),
    ("+Z", ["front"]),
    ("-Z", ["back"]),
]

CUBEMAP_LAYOUTS = [
    "Horizontal Cross",
    "Vertical Cross",
    "3x2 Grid",
    "2x3 Grid",
    "Horizontal Strip",
    "Vertical Strip",
]

class CubemapStitcherTk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(os.path.basename(__file__))
        self.geometry("900x650")
        self.folder_path = ""
        self.images = []
        self.face_assignments = {face: None for face, _ in CUBEMAP_FACES}
        self._build_ui()

    def _build_ui(self):
        # Folder selection
        folder_frame = tk.Frame(self)
        folder_frame.pack(fill=tk.X, padx=10, pady=5)
        self.folder_label = tk.Label(folder_frame, text="No folder selected", anchor="w")
        self.folder_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        browse_btn = tk.Button(folder_frame, text="Browse Folder", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT)

        # Layout selection
        layout_frame = tk.Frame(self)
        layout_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(layout_frame, text="Cubemap Layout:").pack(side=tk.LEFT)
        self.layout_var = tk.StringVar(value=CUBEMAP_LAYOUTS[0])
        layout_combo = ttk.Combobox(layout_frame, textvariable=self.layout_var, values=CUBEMAP_LAYOUTS, state="readonly", width=20)
        layout_combo.pack(side=tk.LEFT, padx=5)

        # File list and face assignment
        assign_frame = tk.LabelFrame(self, text="Assign Images to Faces")
        assign_frame.pack(fill=tk.X, padx=10, pady=5)
        file_list_frame = tk.Frame(assign_frame)
        file_list_frame.pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(file_list_frame, text="Files:").pack()
        self.file_listbox = tk.Listbox(file_list_frame, width=60, height=8)
        self.file_listbox.pack()

        faces_frame = tk.Frame(assign_frame)
        faces_frame.pack(side=tk.LEFT, padx=10, pady=5)
        self.face_dropdowns = {}
        for face, aliases in CUBEMAP_FACES:
            row = tk.Frame(faces_frame)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{face} ({'/'.join(aliases)})", width=16, anchor="w").pack(side=tk.LEFT)
            var = tk.StringVar(value="<None>")
            dropdown = ttk.Combobox(row, textvariable=var, values=["<None>"], state="readonly", width=60) #22
            dropdown.pack(side=tk.LEFT)
            self.face_dropdowns[face] = dropdown

        # Output file selection
        output_frame = tk.Frame(self)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(output_frame, text="Output File:").pack(side=tk.LEFT)
        self.output_file_var = tk.StringVar()
        output_entry = tk.Entry(output_frame, textvariable=self.output_file_var, width=50)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        output_browse = tk.Button(output_frame, text="Browse", command=self.browse_output_file)
        output_browse.pack(side=tk.LEFT)

        # Action buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        preview_btn = tk.Button(btn_frame, text="Preview", command=self.preview_cubemap)
        preview_btn.pack(side=tk.LEFT, padx=10)
        save_btn = tk.Button(btn_frame, text="Save Cubemap", command=self.save_cubemap)
        save_btn.pack(side=tk.LEFT, padx=10)

        # Status label
        self.status_var = tk.StringVar()
        status_label = tk.Label(self, textvariable=self.status_var, anchor="w", fg="blue")
        status_label.pack(fill=tk.X, padx=10, pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Image Folder")
        if folder:
            self.folder_path = folder
            self.folder_label.config(text=folder)
            self.load_images()

    def load_images(self):
        self.images = [f for f in os.listdir(self.folder_path) if f.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff"))]
        self.file_listbox.delete(0, tk.END)
        for img in self.images:
            self.file_listbox.insert(tk.END, img)
        for dropdown in self.face_dropdowns.values():
            dropdown["values"] = ["<None>"] + self.images
            dropdown.set("<None>")
        self.status_var.set(f"Found {len(self.images)} images.")

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Select Output File",
            defaultextension=".png",
            filetypes=[
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg;*.jpeg"),
                ("TIFF Files", "*.tif;*.tiff"),
                ("BMP Files", "*.bmp"),
                ("OpenEXR Files", "*.exr"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.output_file_var.set(file_path)

    def get_face_files(self):
        face_files = {}
        for face in self.face_dropdowns:
            fname = self.face_dropdowns[face].get()
            if fname != "<None>":
                face_files[face] = os.path.join(self.folder_path, fname)
            else:
                face_files[face] = None
        return face_files

    def get_images(self, face_files):
        faces = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
        images = []
        for face in faces:
            fpath = face_files.get(face)
            if fpath and os.path.exists(fpath):
                try:
                    img = Image.open(fpath).convert("RGB")
                except Exception:
                    img = None
            else:
                img = None
            images.append(img)
        return images

    def preview_cubemap(self):
        face_files = self.get_face_files()
        images = self.get_images(face_files)
        ref_img = next((im for im in images if im is not None), None)
        if ref_img is None:
            self.status_var.set("No valid images assigned to faces.")
            return
        w, h = ref_img.size
        layout = self.layout_var.get()
        grid_img, _ = self.compose_cubemap(images, layout, w, h)
        if grid_img:
            self.show_image_popup(grid_img)

    def save_cubemap(self):
        face_files = self.get_face_files()
        images = self.get_images(face_files)
        ref_img = next((im for im in images if im is not None), None)
        if ref_img is None:
            self.status_var.set("No valid images assigned to faces.")
            return
        w, h = ref_img.size
        layout = self.layout_var.get()
        grid_img, err = self.compose_cubemap(images, layout, w, h)
        if not grid_img:
            self.status_var.set(err)
            return
        file_path = self.output_file_var.get().strip()
        if not file_path:
            self.status_var.set("Please specify an output file path.")
            return
        try:
            ext = os.path.splitext(file_path)[1].lower()
            save_kwargs = {}
            if ext in [".exr"]:
                # Pillow supports EXR only if OpenEXR plugin is installed
                save_kwargs["format"] = "EXR"
            elif ext in [".tif", ".tiff"]:
                save_kwargs["format"] = "TIFF"
            elif ext in [".bmp"]:
                save_kwargs["format"] = "BMP"
            elif ext in [".jpg", ".jpeg"]:
                save_kwargs["format"] = "JPEG"
            else:
                save_kwargs["format"] = "PNG"
            grid_img.save(file_path, **save_kwargs)
            self.status_var.set(f"Saved: {file_path}")
        except Exception as e:
            self.status_var.set(f"Failed to save: {e}")

    def compose_cubemap(self, images, layout, w, h):
        faces = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
        if layout == "3x2 Grid":
            grid_img = Image.new("RGB", (3 * w, 2 * h), (64, 64, 64))
            positions = [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)]
        elif layout == "2x3 Grid":
            grid_img = Image.new("RGB", (2 * w, 3 * h), (64, 64, 64))
            positions = [(0,0),(1,0),(0,1),(1,1),(0,2),(1,2)]
        elif layout == "Horizontal Strip":
            grid_img = Image.new("RGB", (6 * w, h), (64, 64, 64))
            positions = [(i,0) for i in range(6)]
        elif layout == "Vertical Strip":
            grid_img = Image.new("RGB", (w, 6 * h), (64, 64, 64))
            positions = [(0,i) for i in range(6)]
        elif layout == "Horizontal Cross":
            grid_img = Image.new("RGB", (4 * w, 3 * h), (0, 0, 0))
            positions = {
                "+X": (2,1), "-X": (0,1), "+Y": (1,0), "-Y": (1,2), "+Z": (1,1), "-Z": (3,1)
            }
        elif layout == "Vertical Cross":
            grid_img = Image.new("RGB", (3 * w, 4 * h), (0, 0, 0))
            positions = {
                "+X": (2,1), "-X": (0,1), "+Y": (1,0), "-Y": (1,2), "+Z": (1,1), "-Z": (1,3)
            }
        else:
            return None, f"Layout not implemented: {layout}"

        if layout in ["3x2 Grid", "2x3 Grid", "Horizontal Strip", "Vertical Strip"]:
            for idx, img in enumerate(images):
                if img is not None:
                    img = img.resize((w, h))
                    x = positions[idx][0] * w
                    y = positions[idx][1] * h
                    grid_img.paste(img, (x, y))
        elif layout == "Horizontal Cross":
            for idx, face in enumerate(faces):
                img = images[idx]
                if img is not None:
                    img = img.resize((w, h))
                    x, y = positions[face]
                    grid_img.paste(img, (x * w, y * h))
        elif layout == "Vertical Cross":
            for idx, face in enumerate(faces):
                img = images[idx]
                if img is not None:
                    img = img.resize((w, h))
                    if face == "-Z":
                        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # or img.rotate(180)
                    x, y = positions[face]
                    grid_img.paste(img, (x * w, y * h))
        return grid_img, None

    def show_image_popup(self, pil_img):
        win = tk.Toplevel(self)
        win.title("Cubemap Preview")
        img_w, img_h = pil_img.size
        scale = min(600 / img_w, 400 / img_h, 1.0)
        disp_img = pil_img.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(disp_img)
        label = tk.Label(win, image=tk_img)
        label.image = tk_img
        label.pack(padx=10, pady=10)
        btn = tk.Button(win, text="OK", command=win.destroy)
        btn.pack(pady=5)

if __name__ == "__main__":
    app = CubemapStitcherTk()
    app.mainloop()
