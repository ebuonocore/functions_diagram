import tkinter as tki
from PIL import Image, ImageTk
from diagram import *
import tools as tl
from tkinter import colorchooser


class Window_configuration():
    def __init__(self, parent_window):
        self.parent = parent_window
        self.tk = parent_window.tk
        self.window = tki.Toplevel(self.tk)
        self.window.title('Configuration')
        self.window.resizable(height=True, width=True)
        self.window.bind("<Return>", lambda event: self.cmd_commit())
        self.parent.tk.update_idletasks()
        self.MARGE = 4
        self.colors = {"DANGER": "pink",
                       "LABEL": "lightgrey", "NEUTRAL": "white"}
        file = 'images/painting_can.png'
        image = Image.open(file)
        self.painting_can_image = ImageTk.PhotoImage(image)
        rootx = self.parent.can.winfo_rootx()
        rooty = self.parent.can.winfo_rooty()
        can_height = self.parent.can.winfo_height()
        win_width, win_height = self.window_dimension(
            self.parent.tk.geometry())
        height = min(400, can_height-2*self.MARGE-40)
        self.window.geometry(
            "400x{}+{}+{}".format(height, rootx+win_width-400-self.MARGE, rooty+self.MARGE))
        self.preferences = tl.load_preferences()
        self.frame = tl.ScrollableFrame(self.window)
        self.pref_cells = dict()
        self.lines = self.build_frame()
        self.frame.pack(fill=tki.BOTH, expand=True)
        self.bt_frame = tki.Frame(
            self.window, relief=tki.RAISED, borderwidth=1, width=300, height=40)
        self.cancel_button = tki.Button(self.bt_frame, text="Cancel",
                                        command=self.cmd_cancel)
        self.cancel_button.pack(side=tki.RIGHT, padx=5, pady=5)
        self.default_button = tki.Button(self.bt_frame, text="Default",
                                         command=self.cmd_default)
        self.default_button.pack(side=tki.RIGHT, padx=5, pady=5)
        self.validate_button = tki.Button(self.bt_frame, text="Ok",
                                          command=self.cmd_commit)
        self.validate_button.pack(side=tki.RIGHT, padx=5, pady=5)
        self.bt_frame.pack(fill=tki.BOTH, expand=False)

    def build_frame(self):
        lines = tki.Canvas(self.frame.scrollable_frame)
        for pref_key, pref_value in self.preferences.items():
            line = tki.Frame(lines)
            label_var = tki.StringVar()
            label_var.set(pref_key)
            label_field = tki.Label(line, textvariable=label_var, width=23)
            label_field.config(bg=self.colors["LABEL"])
            label_field.pack(side=tki.LEFT)
            value = tki.StringVar()
            value.set(pref_value)
            self.pref_cells[pref_key] = tki.Entry(
                line, textvariable=value, width=20)
            self.pref_cells[pref_key].bind(
                "<FocusOut>", self.update_preferences)
            self.pref_cells[pref_key].pack(side=tki.LEFT)
            if "color" in pref_key:
                bt = tki.Button(line, image=self.painting_can_image,
                                command=lambda: self.colorchooser(pref_key))
                bt.pack(side=tki.LEFT)
            line.pack(side=tki.TOP)
        lines.pack()
        return lines

    def cmd_commit(self):
        self.update_preferences(None)
        tl.write_preferences(self.preferences)
        self.parent.draw()
        self.window.destroy()

    def cmd_default(self):
        self.preferences = tl.load_preferences('default')
        self.parent.preferences = self.preferences
        self.parent.draw()
        self.lines.destroy()
        self.build_frame()

    def cmd_cancel(self):
        self.window.destroy()

    def update_preferences(self, event):
        for pref_key, entry_cell in self.pref_cells.items():
            pref_value = entry_cell.get()
            self.preferences[pref_key] = pref_value
        self.parent.preferences = self.preferences
        self.parent.draw()

    def colorchooser(self, pref_key):
        color = colorchooser.askcolor()[1]
        entry = self.pref_cells[pref_key]
        entry.delete(0, tki.END)
        entry.insert(0, color)

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
