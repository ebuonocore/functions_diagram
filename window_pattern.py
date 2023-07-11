from PIL import Image, ImageTk
import tkinter as tki
from diagram import *
import tools as tl


class Window_pattern:
    def __init__(self, parent_window, diagram):
        self.parent = parent_window
        self.tk = parent_window.tk
        self.diagram = diagram
        self.window = tki.Toplevel(self.tk)
        self.window.resizable(height=True, width=False)
        self.window.bind("<Return>", lambda event: self.cmd_commit())
        self.parent.tk.update_idletasks()
        self.MARGE = 4
        self.painting_can_image = self.load_image("painting_can")
        self.garbage_image = self.load_image("garbage")
        self.add_image = self.load_image("add")
        self.colors = {"DANGER": "pink", "LABEL": "lightgrey", "NEUTRAL": "white"}
        self.frame = tki.Frame(self.window, width=300, height=200)
        self.bt_frame = tki.Frame(
            self.window, relief=tki.RAISED, borderwidth=1, width=300, height=40
        )
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=0)
        self.frame.pack(fill=tki.BOTH, expand=False)
        self.cancel_button = tki.Button(
            self.bt_frame, text="Cancel", command=self.cmd_cancel
        )
        self.cancel_button.pack(side=tki.RIGHT, padx=5, pady=5)
        self.validate_button = tki.Button(
            self.bt_frame, text="Ok", command=self.cmd_commit
        )
        self.validate_button.pack(side=tki.RIGHT, padx=5, pady=5)
        self.bt_frame.pack(side=tki.BOTTOM, fill=tki.BOTH, expand=False)
        # self.bt_frame.pack_propagate(False)

        self.window.protocol("WM_DELETE_WINDOW", self.cmd_cancel)

    def cmd_cancel(self):
        self.window.destroy()

    def cmd_commit(self):
        self.window.destroy()

    def close_window(self):
        self.parent.memory.add(self.parent.diagram.export_to_text())
        self.parent.edition_in_progress = False
        self.tk.after(10, self.window.destroy())

    def update_parent_window(self):
        self.parent.auto_resize_blocks()
        self.parent.position_functions_nodes()
        self.parent.draw()

    def is_like_tuple(self, value):
        """Return True if value is string castable in a tuple.
        Otherwise, return False.
        """
        couple = tl.coordinates(value)
        if couple is not None and len(couple) == 2:
            return True
        else:
            return False

    def resize_height(self):
        self.parent.can.update()
        try:
            if self.frame.winfo_exists():
                height = self.frame.winfo_height() + 40
                width = self.window.winfo_width()
                self.window.geometry("{}x{}".format(width, height))
        except:
            pass

    def window_location(self, geometry: str) -> tuple:
        """Take the geometry string as a parameter.
        Return the tuple (locx, locy) corresponding to the location of the window.
        Return (0, 0) if the the location is not find.
        """
        locations = geometry.split("+")
        if len(locations) == 3:
            if locations[1].isdigit() and locations[2].isdigit():
                return (int(locations[1]), int(locations[2]))
        return (0, 0)

    def window_dimension(self, geometry: str) -> tuple:
        """Take the geometry string as a parameter.
        Return the tuple (width, height) corresponding to the dimension of the window.
        Return (0, 0) if the the dimension is not find.
        """
        settings = geometry.split("+")
        if len(settings) == 3:
            dimensions = settings[0].split("x")
            if len(dimensions) == 2:
                if dimensions[0].isdigit() and dimensions[1].isdigit():
                    return (int(dimensions[0]), int(dimensions[1]))
        return (0, 0)

    def load_image(self, file_name: str) -> ImageTk.PhotoImage:
        """Load the image from the file."""
        file = "images/" + file_name + ".png"
        image = Image.open(file)
        return ImageTk.PhotoImage(image)
