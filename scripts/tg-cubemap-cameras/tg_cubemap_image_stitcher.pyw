'''Cubemap Image Stitcher '''

import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from collections import namedtuple
from PIL import Image, ImageTk
import numpy as np
import OpenEXR
import Imath # for EXR support

ImageBundle = namedtuple('Image', ['srgb', 'linear_r', 'linear_g', 'linear_b'])

DEFAULT_FACE_LABEL_ALIASES = {
    'forward': 'forward', 'front': 'forward',
    'back': 'back', 'rear': 'back',
    'left': 'left',
    'right': 'right',
    'top': 'up', 'up': 'up',
    'bottom': 'down', 'down': 'down',
}

# face_label_aliases may be updated by user's config file
# or reset to defaults, or edited in the UI
face_label_aliases = DEFAULT_FACE_LABEL_ALIASES.copy()

GRID_LAYOUTS = {
    '6x1': (6, 1),
    '1x6': (1, 6),
    '3x2': (3, 2),
    '2x3': (2, 3),
    '4x3': (4, 3),
    '3x4': (3, 4)
}

# output presets
CUBEMAP_PRESETS = {
    '6x1': {
        'Left, Forward, Right, Back, Up, Down': {
            2: ('right', 0),
            0: ('left', 0),
            4: ('up', 0),
            5: ('down', 0),
            1: ('forward', 0),
            3: ('back', 0),
        },
        'Unity Cubemap': {
            0: ('right', 0),
            1: ('left', 0),
            2: ('up', 0),
            3: ('down', 0),
            4: ('forward', 0),
            5: ('back', 0),
        },
        'Unreal Engine Cubemap': { 
            0: ('right', 90),
            1: ('left', 270),
            2: ('back', 180),
            3: ('forward', 0),
            4: ('up', 0),
            5: ('down', 180),
        },
    },
    '1x6': {
        'Unity Cubemap': {
            0: ('right', 0),
            1: ('left', 0),
            2: ('up', 0),
            3: ('down', 0),
            4: ('forward', 0),
            5: ('back', 0),
        },
    },
    '3x2': {
        'Unity Cubemap': {
            0: ('right', 0),
            1: ('left', 0),
            2: ('up', 0),
            3: ('down', 0),
            4: ('forward', 0),
            5: ('back', 0),
        },
    },
    '2x3': {
        'Unity Cubemap': {
            0: ('right', 0),
            1: ('left', 0),
            2: ('up', 0),
            3: ('down', 0),
            4: ('forward', 0),
            5: ('back', 0),
        },
    },
    '4x3': {
        'Unity Cubemap': {
            6: ('right', 0),
            4: ('left', 0),
            1: ('up', 0),
            9: ('down', 0),
            5: ('forward', 0),
            7: ('back', 0),
        },
        'Stride3d Cubemap': {
            1: ('right', 90),
            9: ('left', 90),
            4: ('up', 90),
            6: ('down', 90),
            5: ('forward', 90),
            7: ('back', 270),
        },
        'Cafu Cubemap': {
            7: ('right', 0),
            5: ('left', 0),
            2: ('up', 0),
            10: ('down', 0),
            6: ('forward', 0),
            4: ('back', 0),
        },
        'Roblox Skybox': {
            6: ('right', 0),
            4: ('left', 0),
            0: ('up', 0),
            8: ('down', 0),
            7: ('forward', 0),
            5: ('back', 0),
        },
    },
    '3x4': {
        'Unity Cubemap': {
            4: ('right', 0),
            10: ('left', 0),
            1: ('up', 0),
            7: ('down', 0),
            3: ('forward', 0),
            5: ('back', 0),
        },
    }
}


class CubeMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title(os.path.basename(__file__))

        self.detected_faces = {}
        self.selected_face = None
        self.grid_cells = []
        self.grid_assignments = {}
        self.current_layout = '3x2'
        self.cell_frame = None
        self.cell_size = 144
        self.cell_flip_states = {}  # {cell_index: {'h': bool, 'v': bool}}
        self.cell_rotations = {}  # {cell_index: degrees}

        self.aliases_patterns = {
            'forward': tk.StringVar(),
            'back': tk.StringVar(),
            'left': tk.StringVar(),
            'right': tk.StringVar(),
            'up': tk.StringVar(),
            'down': tk.StringVar()
        }

        self.init_aliases_patterns()  # Initialize with default aliases

        # Create a placeholder image to ensure label doesn't collapse
        placeholder = Image.new("RGB", (self.cell_size, self.cell_size), "black")
        self.placeholder_image = ImageTk.PhotoImage(placeholder)

        self.setup_ui()


    def clear_aliases_patterns(self):
        """Clear all aliases patterns."""
        for var in self.aliases_patterns.values():
            var.set("")


    def reset_aliases_patterns(self):
        self.clear_aliases_patterns() # Clear existing patterns
        # Reset to default aliases
        for key, value in DEFAULT_FACE_LABEL_ALIASES.items():
            if value in self.aliases_patterns:
                self.aliases_patterns[value].set(self.aliases_patterns[value].get() + " " + key)


    def init_aliases_patterns(self):
        """Initialize aliases patterns from the config file or the default aliases."""
        base_name = os.path.splitext(os.path.basename(__file__))[0]
        config_path = os.path.join(os.path.dirname(__file__), base_name + '_config.txt')

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    if ':' in line:
                        face, alias = line.split(':', 1)
                        face = face.strip().lower()
                        alias = alias.strip()
                        if face in self.aliases_patterns:
                            self.aliases_patterns[face].set(alias)
        else:
            self.reset_aliases_patterns()


    def save_aliases_to_config(self):
        """Save current aliases to a config file."""
        base_name = os.path.splitext(os.path.basename(__file__))[0]
        config_path = os.path.join(os.path.dirname(__file__), base_name + '_config.txt')

        with open(config_path, 'w') as f:
            for face, var in self.aliases_patterns.items():
                f.write(f"{face}: {var.get().strip()}\n")

        messagebox.showinfo("Save Aliases", f"Aliases saved to:\n{config_path}")


    def setup_ui(self):
        # Main container frames
        input_frame = tk.Frame(self.root, borderwidth=2, relief="groove")
        input_frame.pack(padx=10, pady=5, fill="x")

        output_frame = tk.Frame(self.root, borderwidth=2, relief="groove")
        output_frame.pack(padx=10, pady=5, fill="x")

        # -------------------
        # INPUT FRAME CONTENT
        # -------------------

        # Browse frame
        browse_frame = tk.Frame(input_frame)
        browse_frame.pack(pady=5, fill="x")

        tk.Button(browse_frame, text="Browse for image file",
                command=self.browse_image).pack(side=tk.LEFT, padx=10)

        self.selected_file_label = tk.Label(browse_frame, text="No file selected", fg='gray')
        self.selected_file_label.pack(side=tk.LEFT, padx=10)

        # Thumbnails
        self.face_frame = tk.Frame(input_frame)
        self.face_frame.pack(pady=10)
        self.render_face_thumbnails()  # Initial empty thumbnails

        # Aliases buttons
        aliases_frame = tk.Frame(input_frame)
        aliases_frame.pack(pady=5, fill="x")

        clear_aliases = tk.Button(
            aliases_frame,
            text="Clear Aliases",
            command=self.clear_aliases_patterns
        )
        clear_aliases.pack(side=tk.LEFT, padx=10, pady=5)

        reset_aliases = tk.Button(
            aliases_frame,
            text="Reset Aliases",
            command=self.reset_aliases_patterns
        )
        reset_aliases.pack(side=tk.LEFT, padx=10, pady=5)

        save_aliases = tk.Button(
            aliases_frame,
            text="Save Aliases",
            command=self.save_aliases_to_config
        )
        save_aliases.pack(side=tk.LEFT, padx=10, pady=5)

        load_aliases_from_config = tk.Button(
            aliases_frame,
            text="Load Aliases from Config",
            command=self.init_aliases_patterns
        )
        load_aliases_from_config.pack(side=tk.LEFT, padx=10, pady=5)

        # -------------------
        # OUTPUT FRAME CONTENT
        # -------------------

        # Layout control + Presets Menubutton
        layout_control_frame = tk.Frame(output_frame)
        layout_control_frame.pack(pady=5, fill="x")

        tk.Label(layout_control_frame, text="Grid Layout: ").pack(side=tk.LEFT)
        self.layout_var = tk.StringVar(value=self.current_layout)
        for name in GRID_LAYOUTS:
            tk.Radiobutton(layout_control_frame, text=name, variable=self.layout_var,
                        value=name, command=self.update_grid_layout).pack(side=tk.LEFT)

        # --- Presets Menubutton ---
        preset_mb = tk.Menubutton(layout_control_frame, text="Presets", relief="raised")
        preset_mb.pack(side=tk.LEFT, padx=10)

        preset_menu = tk.Menu(preset_mb, tearoff=0)
        for layout, presets in CUBEMAP_PRESETS.items():
            layout_submenu = tk.Menu(preset_menu, tearoff=0)
            for preset_name in presets:
                layout_submenu.add_command(
                    label=preset_name,
                    command=lambda l=layout, p=preset_name: self.apply_preset(l, p)
                )
            preset_menu.add_cascade(label=layout, menu=layout_submenu)

        preset_mb.config(menu=preset_menu)

        # Grid display
        self.cell_frame = tk.Frame(output_frame)
        self.cell_frame.pack(pady=10)
        self.create_grid()

        # Clear, Preview and Save buttons
        save_frame = tk.Frame(self.root)
        save_frame.pack(pady=10)
        tk.Button(save_frame, text="Clear Assignments", command=self.clear_grid_assignments).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(save_frame, text="Preview Stitched Image", command=self.preview_stitched_image).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(save_frame, text="Save Stitched Image", command=self.save_stitched_image).pack(side=tk.LEFT)


    def browse_image(self):
        '''Handles file selection and places thumbnails in browsing frames of UI.
        Tries to detect all six cubemap faces from the selected filename.
        '''
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.tif *.tiff *.exr")]
        )

        if not file_path:
            return
        self.selected_file_label.config(text=os.path.basename(file_path), fg='black')
        self.detect_faces_from_file(file_path) # Tries to detect six cubemap images from the filename
        self.render_face_thumbnails()
        self.clear_grid_assignments()  # Clear previous assignments when loading new faces


    def detect_faces_from_file(self, file_path):
        '''Tries to detect cubemap faces from the selected file.'''
        folder = os.path.dirname(file_path)
        all_files = os.listdir(folder)
        ext = os.path.splitext(file_path)[1].lower()
        selected_filename = os.path.basename(file_path)
        selected_base, _ = os.path.splitext(selected_filename)

        global face_label_aliases
        face_label_aliases.clear()

        # Check aliases patternss first
        for label, var in self.aliases_patterns.items():
            words = var.get().strip().split()
            for word in words:
                face_label_aliases[word.lower()] = label  # Add each word as an alias for the label

        # Find the pattern in the selected file
        selected_pattern = None
        selected_prefix = None
        selected_suffix = None
        for alias in face_label_aliases:
            idx = selected_base.lower().find(alias)
            if idx != -1:
                selected_pattern = alias
                selected_prefix = selected_base[:idx]
                selected_suffix = selected_base[idx+len(alias):]
                break

        if selected_pattern is None:
            # Fallback: use the whole base name as prefix
            selected_prefix = selected_base
            selected_suffix = ''

        self.detected_faces.clear()
        for f in all_files:
            if not f.lower().endswith(ext):
                continue
            f_base = os.path.splitext(f)[0]
            for alias, label in face_label_aliases.items():
                idx = f_base.lower().find(alias)
                if idx != -1:
                    prefix = f_base[:idx]
                    suffix = f_base[idx+len(alias):]
                    # Only accept if prefix and suffix match selected file
                    if prefix == selected_prefix and suffix == selected_suffix and label not in self.detected_faces:
                        full_path = os.path.join(folder, f)
                        try:
                            img = self.load_image_rgb(full_path)

                            thumb = img.srgb.copy()
                            thumb.thumbnail((self.cell_size, self.cell_size))
                            thumb_tk = ImageTk.PhotoImage(thumb)
                            self.detected_faces[label] = {
                                'filename': f,
                                'filepath': full_path,
                                'image': img,              # <-- full-size image bundle for flipping/stitching
                                'thumbnail': thumb_tk,     # for display in UI
                                'matched_pattern': alias   # store the matched pattern
                            }
                        except Exception as e:
                            print(f"In detect_faces_from_file Failed to load {f}: {e}")
                        break


    def render_face_thumbnails(self):
        # TODO: Separate the creation and update of thumbnails
        for widget in self.face_frame.winfo_children():
            widget.destroy()

        def on_face_click(label):
            self.selected_face = label
            # TODO: Only highlight, don't recreate thumbnails
            self.render_face_thumbnails()  # Re-render to update highlight

        def on_face_right_click(event, label):
            filepath = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.jpg *.jpeg *.png * tiff *.tiff")]
            )
            if not filepath:
                return "break"
            try:
                img = self.load_image_rgb(filepath)
                thumb = img.srgb.copy()
                thumb.thumbnail((self.cell_size, self.cell_size))
                thumb = ImageTk.PhotoImage(thumb)
                # Extract the matched pattern from the filename
                base = os.path.splitext(os.path.basename(filepath))[0]
                matched_pattern = label  # fallback
                for alias in face_label_aliases:
                    if alias in base.lower():
                        matched_pattern = alias
                        break
                self.detected_faces[label] = {
                    'filename': os.path.basename(filepath),
                    'filepath': filepath,
                    'image': img,
                    'thumbnail': thumb,
                    'matched_pattern': label
                }
                self.render_face_thumbnails()
            except Exception as e:
                print(f"Failed to load {filepath}: {e}")
            return "break"

        for i, face in enumerate(['forward', 'back', 'left', 'right', 'up', 'down']):
            # Highlight if selected
            if face == self.selected_face:
                frame = tk.Frame(
                    self.face_frame,
                    relief=tk.SOLID,
                    borderwidth=4,
                    padx=5,
                    pady=5,
                    bg="#3399ff"
                )
            else:
                frame = tk.Frame(self.face_frame, relief=tk.RIDGE, borderwidth=2, padx=5, pady=5)
            frame.grid(row=i//3, column=i%3, padx=5, pady=5)
            # Show matched pattern (if available) instead of alias label
            pattern_label = face.upper()
            if face in self.detected_faces and 'matched_pattern' in self.detected_faces[face]:
                pattern_label = self.detected_faces[face]['matched_pattern'].upper()
            tk.Label(frame, text=pattern_label).pack()
            if face in self.detected_faces:
                thumb = self.detected_faces[face]['thumbnail']
                lbl = tk.Label(frame, image=thumb, cursor="hand2")
                lbl.pack()
                lbl.bind("<Button-1>", lambda e, f=face: on_face_click(f))
                lbl.bind("<ButtonRelease-3>", lambda e, f=face: on_face_right_click(e, f))
                # tk.Label(frame, text=self.detected_faces[face]['filename'], fg='gray').pack()
            else:
                lbl = tk.Label(
                    frame,
                    text="[Empty]",
                    width=12,
                    height=6,
                    bg='black',
                    fg='white',
                    cursor="hand2"
                )
                lbl.pack()
                lbl.bind("<ButtonRelease-3>", lambda e, f=face: on_face_right_click(e, f))

            # Add entry field for aliases patterns
            tk.Label(frame, text="Aliases:").pack()
            tk.Entry(frame, textvariable=self.aliases_patterns[face], width=23).pack()


    def create_grid(self):
        '''Create the output grid based on the current layout.'''
        # TODO: Rename this method to create_output_grid
        for widget in self.cell_frame.winfo_children():
            widget.destroy()

        old_assignments = self.grid_assignments.copy()
        old_flips = self.cell_flip_states.copy()
        old_rotations = self.cell_rotations.copy()

        self.grid_cells.clear()
        self.grid_assignments.clear()
        self.cell_flip_states.clear()

        cols, rows = GRID_LAYOUTS[self.current_layout]

        for r in range(rows):
            for c in range(cols):
                idx = len(self.grid_cells)
                frame = tk.Frame(
                    self.cell_frame,
                    width=self.cell_size,
                    height=self.cell_size,
                    bg='black',
                    bd=2,
                    relief=tk.SUNKEN
                )
                frame.grid(row=r, column=c, padx=2, pady=2)
                frame.grid_propagate(False)

                lbl = tk.Label(frame, bg='black', image=self.placeholder_image)
                lbl.image = self.placeholder_image
                lbl.pack(expand=True, fill='both')
                lbl.bind("<Button-1>", lambda e, i=idx: self.on_grid_cell_click(i))
                lbl.bind("<Button-3>", lambda e, i=idx: self.show_context_menu(e, i))  # Right-click

                self.grid_cells.append(lbl)
                self.grid_assignments[idx] = old_assignments.get(idx, None)
                self.cell_flip_states[idx] = old_flips.get(idx, {'h': False, 'v': False})
                self.cell_rotations[idx] = old_rotations.get(idx, 0)

                self.update_grid_cell(idx)


    def update_grid_layout(self):
        self.current_layout = self.layout_var.get()
        self.create_grid()


    def on_grid_cell_click(self, cell_index):
        current_assignment = self.grid_assignments.get(cell_index)
        # Only assign if cell is empty and a face is selected
        if not current_assignment and self.selected_face and self.selected_face in self.detected_faces:
            thumb = self.detected_faces[self.selected_face]['thumbnail']
            self.grid_assignments[cell_index] = self.selected_face
            self.grid_cells[cell_index].config(image=thumb, bg='black')
            self.grid_cells[cell_index].image = thumb


    def clear_cell_assignment(self, idx):
        self.grid_assignments[idx] = None
        self.update_grid_cell(idx)


    def update_grid_cell(self, idx):
        face_key = self.grid_assignments[idx]
        lbl = self.grid_cells[idx]

        if face_key and face_key in self.detected_faces:
            thumb_image = self.detected_faces[face_key]['image'].srgb.copy()

            flip_state = self.cell_flip_states.get(idx, {'h': False, 'v': False})
            if flip_state['h']:
                thumb_image = thumb_image.transpose(Image.FLIP_LEFT_RIGHT)
            if flip_state['v']:
                thumb_image = thumb_image.transpose(Image.FLIP_TOP_BOTTOM)

            # After flipping logic, before creating thumbnail:
            rotation = self.cell_rotations.get(idx, 0)
            if rotation:
                thumb_image = thumb_image.rotate(rotation, expand=False)

            thumb_image.thumbnail((self.cell_size, self.cell_size))
            tk_thumb = ImageTk.PhotoImage(thumb_image)
            lbl.config(image=tk_thumb, bg='black')
            lbl.image = tk_thumb
        else:
            lbl.config(image=self.placeholder_image, bg='black')
            lbl.image = self.placeholder_image


    def show_context_menu(self, event, idx):
        '''Show context menu for output grid cell actions (flip, rotate, assign face, etc.).'''
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Flip Horizontally", command=lambda: self.flip_cell(idx, 'h'))
        menu.add_command(label="Flip Vertically", command=lambda: self.flip_cell(idx, 'v'))
        menu.add_separator()
        menu.add_command(label="Rotate 90 CCW", command=lambda: self.rotate_cell(idx, 90))
        menu.add_command(label="Rotate 90 CW", command=lambda: self.rotate_cell(idx, -90))
        menu.add_command(
            label="Reset Rotation",
            command=lambda: self.rotate_cell(idx, -self.cell_rotations.get(idx, 0))
        )
        menu.add_separator()
        menu.add_command(
            label="Clear Cell Assignment",
            command=lambda: self.clear_cell_assignment(idx)
        )
        menu.add_separator()

        # Add face label assignments with pattern
        def assign_face_to_cell(face_label):
            if face_label in self.detected_faces:
                self.grid_assignments[idx] = face_label
                self.update_grid_cell(idx)

        for face in ['forward', 'back', 'left', 'right', 'up', 'down']:
            if face in self.detected_faces:
                pattern = self.detected_faces[face].get('matched_pattern', face).upper()
                display_label = f"Assign {pattern}"
                state = tk.NORMAL
            else:
                display_label = f"Assign {face.upper()}"
                state = tk.DISABLED
            menu.add_command(
                label=display_label,
                command=lambda f=face: assign_face_to_cell(f),
                state=state
            )

        menu.tk_popup(event.x_root, event.y_root)


    def rotate_cell(self, idx, angle):
        # Rotate the cell's image by the given angle (+90 or -90)
        current_rotation = self.cell_rotations.get(idx, 0)
        new_rotation = (current_rotation + angle) % 360
        self.cell_rotations[idx] = new_rotation
        self.update_grid_cell(idx)


    def flip_cell(self, idx, axis):
        if idx not in self.cell_flip_states:
            self.cell_flip_states[idx] = {'h': False, 'v': False}

        self.cell_flip_states[idx][axis] = not self.cell_flip_states[idx][axis]
        self.update_grid_cell(idx)


    def clear_grid_assignments(self):
        # Clear only the grid assignments and reset visuals
        for idx in self.grid_assignments:
            self.grid_assignments[idx] = None
            self.update_grid_cell(idx)


    def apply_preset(self, layout_key, preset_name):
        # TODO: Rename this method to apply_output_preset
        if layout_key not in GRID_LAYOUTS:
            print(f"Layout {layout_key} not recognized.")
            return

        preset = CUBEMAP_PRESETS.get(layout_key, {}).get(preset_name, {})
        self.current_layout = layout_key
        self.layout_var.set(layout_key)
        self.create_grid()

        # Clear previous assignments and reset all grid cells
        self.clear_grid_assignments()
        self.cell_rotations.clear()
        self.cell_flip_states.clear()

        for idx, (canonical_face, rotation) in preset.items():
            if canonical_face in self.detected_faces:
                self.grid_assignments[idx] = canonical_face
                self.cell_rotations[idx] = rotation
                # currently do not store flip states in presets
                self.update_grid_cell(idx)
            else:
                print(f"Face '{canonical_face}' not found among detected faces.")


    def stitch_images(self, do_linear):
        """Return an ImageBundle of stitched PIL.Image objects based on current grid assignments.
        May raise an exception if requested image is not available."""
        cols, rows = GRID_LAYOUTS[self.current_layout]
        image_size = None

        # Get size from first assigned image
        for face_key in self.grid_assignments.values():
            if face_key and face_key in self.detected_faces:
                img = self.detected_faces[face_key]['image']
                face_path = self.detected_faces[face_key]['filepath']
                if img is None:
                    print(f"Failed to load image: {face_path}")
                    continue
                image_size = img.srgb.size
                break

        if not image_size:
            return None  # caller handles error display

        cell_width, cell_height = image_size
        out_width, out_height = cols * cell_width, rows * cell_height

        if do_linear:
            stitched_images = [
                Image.new("F", (out_width, out_height), color="black"),
                Image.new("F", (out_width, out_height), color="black"),
                Image.new("F", (out_width, out_height), color="black")
            ]
        else:
            stitched_images = [
                Image.new("RGB", (out_width, out_height), color="black")
            ]

        for idx, face_key in self.grid_assignments.items():
            row = idx // cols
            col = idx % cols
            position = (col * cell_width, row * cell_height)

            if face_key and face_key in self.detected_faces:
                face_path = self.detected_faces[face_key]['filepath']
                image_bundle = self.detected_faces[face_key]['image']
                if image_bundle is None:
                    print(f"Failed to load image: {face_path}")
                    continue

                if do_linear:
                    if image_bundle.linear_r is None or image_bundle.linear_g is None or image_bundle.linear_b is None:
                        print(f"Linear (EXR) images were not loaded for {face_key} at cell {idx}")
                        raise ValueError(
                            f"Linear (EXR) images were not loaded for {face_key} at cell {idx}"
                        )
                    images = [
                        image_bundle.linear_r.copy(),
                        image_bundle.linear_g.copy(),
                        image_bundle.linear_b.copy()
                    ]
                else:
                    if image_bundle.srgb is None:
                        print(f"SRGB image not available for {face_key} at cell {idx}")
                        raise ValueError(f"SRGB image not available for {face_key} at cell {idx}")
                    images = [image_bundle.srgb.copy()]

                for image, stitched_image in zip(images, stitched_images):
                    flip_state = self.cell_flip_states.get(idx, {'h': False, 'v': False})
                    if flip_state['h']:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    if flip_state['v']:
                        image = image.transpose(Image.FLIP_TOP_BOTTOM)

                    # After flipping logic, before pasting into stitched image:
                    rotation = self.cell_rotations.get(idx, 0)
                    if rotation:
                        image = image.rotate(rotation, expand=False)

                    stitched_image.paste(image, position)

        if do_linear:
            return ImageBundle(None, stitched_images[0], stitched_images[1], stitched_images[2])
        else:
            return ImageBundle(stitched_images[0], None, None, None)


    def save_stitched_image(self):
        """Ask for a filename, generate a stitched image, and save it to disk."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("TIFF files", "*.tif *.tiff"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("EXR files", "*.exr"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        do_linear = file_path.lower().endswith(".exr")

        try:
            stitched_image_bundle = self.stitch_images(do_linear=do_linear)
        except Exception as e:
            if do_linear:
                messagebox.showerror("Stitching Failed", f"Could not stitch images to EXR:\n{e}")
            else:
                messagebox.showerror("Stitching Failed", f"Could not stitch images:\n{e}")
            return

        if stitched_image_bundle is None:
            messagebox.showerror("No Images", "No assigned images to save.")
            return

        if do_linear:
            self.save_linears_as_exr(stitched_image_bundle, file_path)
        else:
            stitched_image_bundle.srgb.save(file_path)
            messagebox.showinfo("Success", f"Image saved to:\n{file_path}")


    def preview_stitched_image(self):
        """Show a scrollable, zoomable, and pannable preview of the stitched image."""
        try:
            stitched_image_bundle = self.stitch_images(do_linear=False)
        except Exception as e:
            messagebox.showerror("Stitching Failed", f"Could not stitch images:\n{e}")
            return
        if stitched_image_bundle is None:
            messagebox.showerror("No Images", "No assigned images to preview.")
            return
        stitched_image = stitched_image_bundle.srgb

        preview_window = tk.Toplevel(self.root)
        preview_window.title("Stitched Image Preview")
        preview_window.geometry("800x600")  # starting size

        # --- Scrollable Canvas ---
        canvas = tk.Canvas(preview_window, bg="gray", highlightthickness=0)
        h_scroll = tk.Scrollbar(preview_window, orient=tk.HORIZONTAL, command=canvas.xview)
        v_scroll = tk.Scrollbar(preview_window, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame to hold image inside canvas
        image_frame = tk.Frame(canvas, bg="gray")
        canvas_window = canvas.create_window((0, 0), window=image_frame, anchor="nw")

        img_label = tk.Label(image_frame, bg="gray")
        img_label.pack()

        # Track current scale
        current_scale = [25]  # mutable so inner funcs can change it

        def update_preview(scale_percent, center_x=None, center_y=None):
            """Update preview image, optionally keeping zoom centered at given canvas coords."""
            scale_percent = max(1, min(100, float(scale_percent)))  # clamp to 1–100

            # If no center given, use window center
            if center_x is None or center_y is None:
                center_x = canvas.canvasx(canvas.winfo_width() / 2)
                center_y = canvas.canvasy(canvas.winfo_height() / 2)

            # Convert to relative position before zoom
            scroll_region = canvas.bbox("all")
            if scroll_region:
                x_ratio = (center_x - scroll_region[0]) / (scroll_region[2] - scroll_region[0])
                y_ratio = (center_y - scroll_region[1]) / (scroll_region[3] - scroll_region[1])
            else:
                x_ratio, y_ratio = 0.5, 0.5

            # Resize image
            new_width = int(stitched_image.width * (scale_percent / 100))
            new_height = int(stitched_image.height * (scale_percent / 100))
            resized_img = stitched_image.resize((new_width, new_height), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(resized_img)
            img_label.configure(image=img_tk)
            img_label.image = img_tk  # Keep reference

            # Update scroll region
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

            # Restore scroll position so zoom center stays fixed
            scroll_region = canvas.bbox("all")
            if scroll_region:
                canvas.xview_moveto(x_ratio)
                canvas.yview_moveto(y_ratio)

            current_scale[0] = scale_percent
            scale_slider.set(scale_percent)  # keep slider in sync

        # Slider for zoom
        scale_slider = tk.Scale(
            preview_window,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            label="Preview Size (%)",
            command=lambda val: update_preview(val)
        )
        scale_slider.set(current_scale[0])
        scale_slider.pack(fill="x")

        # --- Mouse wheel scroll & zoom ---
        def _on_mousewheel(event):
            # Ctrl+Wheel for zoom, normal wheel for scroll
            if (event.state & 0x4):  # 0x4 = Control key
                delta = 5 if event.delta > 0 else -5
                update_preview(current_scale[0] + delta,
                            center_x=canvas.canvasx(event.x),
                            center_y=canvas.canvasy(event.y))
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_shift_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

        # --- Drag-to-pan with middle or right mouse ---
        def start_pan(event):
            canvas.scan_mark(event.x, event.y)

        def do_pan(event):
            canvas.scan_dragto(event.x, event.y, gain=1)

        canvas.bind("<ButtonPress-2>", start_pan)   # middle mouse button
        canvas.bind("<B2-Motion>", do_pan)
        canvas.bind("<ButtonPress-3>", start_pan)   # right mouse as fallback
        canvas.bind("<B3-Motion>", do_pan)

        # --- Double-click to reset zoom ---
        def reset_zoom(event=None):
            update_preview(100)  # reset to full size
            # Center image in canvas
            scroll_region = canvas.bbox("all")
            if scroll_region:
                canvas.xview_moveto(0.5 - (canvas.winfo_width() / 2) / (scroll_region[2] - scroll_region[0]))
                canvas.yview_moveto(0.5 - (canvas.winfo_height() / 2) / (scroll_region[3] - scroll_region[1]))

        img_label.bind("<Double-Button-1>", reset_zoom)

        # Initial preview
        update_preview(current_scale[0])


    def load_exr(self, file_path):
        '''Returns a named tuple ImageBundle with (srgb, linear_r, linear_g, linear_b) images'''
        try:
            exr_file = OpenEXR.InputFile(file_path)
            dw = exr_file.header()['dataWindow']
            width = dw.max.x - dw.min.x + 1
            height = dw.max.y - dw.min.y + 1

            pt = Imath.PixelType(Imath.PixelType.FLOAT)
            channels = exr_file.header()['channels'].keys()

            if not all(c in channels for c in ('R', 'G', 'B')):
                return None

            r = np.frombuffer(exr_file.channel('R', pt), dtype=np.float32).reshape((height, width))
            g = np.frombuffer(exr_file.channel('G', pt), dtype=np.float32).reshape((height, width))
            b = np.frombuffer(exr_file.channel('B', pt), dtype=np.float32).reshape((height, width))

            img_linear = np.stack([r, g, b], axis=2)
            img = img_linear.copy()
            img = np.clip(img, 0, 1)
            img = np.power(img, 1.0 / 2.2)  # Apply gamma correction, was gamma variable
            img = (img * 255).astype(np.uint8)

            return ImageBundle(
                Image.fromarray(img),
                Image.fromarray(r),
                Image.fromarray(g),
                Image.fromarray(b)
            )
        except Exception as e:
            print(f"in load_exr Failed to load EXR: {e}")
            return None


    def save_srgb_as_exr(self, pil_image, file_path):
        try:
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")

            # Convert to float32 linear (no gamma)
            arr = np.asarray(pil_image).astype(np.float32) / 255.0

            R = arr[:, :, 0].astype(np.float32).tobytes()
            G = arr[:, :, 1].astype(np.float32).tobytes()
            B = arr[:, :, 2].astype(np.float32).tobytes()

            height, width = arr.shape[:2]
            header = OpenEXR.Header(width, height)
            half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
            header['channels'] = {'R': half_chan, 'G': half_chan, 'B': half_chan}

            exr = OpenEXR.OutputFile(file_path, header)
            exr.writePixels({'R': R, 'G': G, 'B': B})
            exr.close()
            messagebox.showinfo("Success", f"EXR image saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("EXR Save Failed", f"Could not save EXR:\n{e}")


    def save_linears_as_exr(self, image_bundle, file_path):
        try:
            R = np.asarray(image_bundle.linear_r).astype(np.float32)
            G = np.asarray(image_bundle.linear_g).astype(np.float32)
            B = np.asarray(image_bundle.linear_b).astype(np.float32)

            width, height = image_bundle.linear_r.width, image_bundle.linear_r.height
            header = OpenEXR.Header(width, height)
            half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
            header['channels'] = {'R': half_chan, 'G': half_chan, 'B': half_chan}

            exr = OpenEXR.OutputFile(file_path, header)
            exr.writePixels({'R': R, 'G': G, 'B': B})
            exr.close()
            messagebox.showinfo("Success", f"EXR image saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("EXR Save Failed", f"Could not save EXR:\n{e}")


    def load_image_rgb(self, file_path):
        """
        Unified image loader for EXR and standard formats.
        Returns a named tuple ImageBundle with (srgb, linear_r, linear_g, linear_b) images
        or None if loading fails.
        """
        # TODO: Show message if file fails to load, not just print message
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".exr":
            return self.load_exr(file_path) # returns named tuple (srgb, linear exr)
        else:
            try:
                return ImageBundle(Image.open(file_path).convert("RGB"), None, None, None)
            except Exception as e:
                print(f"Failed to load image {file_path}: {e}")
                return None


if __name__ == "__main__":
    root = tk.Tk()
    app = CubeMapApp(root)
    root.mainloop()
