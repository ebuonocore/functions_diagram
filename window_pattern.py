import tkinter as tki
from PIL import Image, ImageTk
from diagram import *
import tools as tl


class Window_pattern():
    def __init__(self, parent_window, diagram):
        self.parent = parent_window
        self.tk = parent_window.tk
        self.diagram = diagram
        self.window = tki.Toplevel(self.tk)
        self.window.resizable(height=True, width=False)
        self.window.bind("<Return>", lambda event: self.cmd_commit())
        self.parent.tk.update_idletasks()
        self.MARGE = 4
        file = 'images/painting_can.png'
        image = Image.open(file)
        self.painting_can_image = ImageTk.PhotoImage(image)
        file = 'images/garbage.png'
        image = Image.open(file)
        self.garbage_image = ImageTk.PhotoImage(image)
        file = 'images/add.png'
        image = Image.open(file)
        self.add_image = ImageTk.PhotoImage(image)
        self.colors = {"DANGER": "pink",
                       "LABEL": "lightgrey", "NEUTRAL": "white"}
        self.frame = tki.Frame(self.window, width=300, height=200)
        self.bt_frame = tki.Frame(
            self.window, relief=tki.RAISED, borderwidth=1, width=300, height=40)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=0)
        self.frame.pack(fill=tki.BOTH, expand=True)
        self.cancel_button = tki.Button(self.bt_frame, text="Cancel",
                                        command=self.cmd_cancel)
        self.cancel_button.pack(side=tki.RIGHT, padx=5, pady=5)
        self.validate_button = tki.Button(self.bt_frame, text="Ok",
                                          command=self.cmd_commit)
        self.validate_button.pack(side=tki.RIGHT, padx=5, pady=5)
        self.bt_frame.pack(fill=tki.BOTH, expand=True)
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
        """ Returns True if value is string castable in a tuple.
        Otherwise, returns False.
        """
        couple = tl.coordinates(value)
        if couple is not None and len(couple) == 2:
            return True
        else:
            return False

    def resize_height(self):
        self.parent.can.update()
        if self.frame.winfo_exists():
            height = self.frame.winfo_height() + 40
            width = self.window.winfo_width()
            self.window.geometry("{}x{}".format(width, height))

    def window_location(self, geometry: str) -> tuple:
        """ Takes the geometry string as a parameter.
            Returns the tuple (locx, locy) corresponding to the location of the window.
            Returns (0, 0) if the the location is not find.
        """
        locations = geometry.split('+')
        if len(locations) == 3:
            if locations[1].isdigit() and locations[2].isdigit():
                return (int(locations[1]), int(locations[2]))
        return (0, 0)

    def window_dimension(self, geometry: str) -> tuple:
        """ Takes the geometry string as a parameter.
            Returns the tuple (width, height) corresponding to the dimension of the window.
            Returns (0, 0) if the the dimension is not find.
        """
        settings = geometry.split('+')
        if len(settings) == 3:
            dimensions = settings[0].split('x')
            if len(dimensions) == 2:
                if dimensions[0].isdigit() and dimensions[1].isdigit():
                    return (int(dimensions[0]), int(dimensions[1]))
        return (0, 0)
