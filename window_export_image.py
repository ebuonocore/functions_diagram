from canvasvg import saveall
from os import remove
from PIL import Image, ImageTk
from tkinter import filedialog as fd
import tkinter as tki
from diagram import *
import tools as tl
from window_pattern import *


class Window_export_image(Window_pattern):
    def __init__(self, parent_window, diagram, destination=None):
        super().__init__(parent_window, diagram)
        self.window.title('Export diagram to SVG')
        rootx = self.parent.can.winfo_rootx()
        rooty = self.parent.can.winfo_rooty()
        win_width, win_height = self.window_dimension(
            self.parent.tk.geometry())
        self.window.geometry(
            "300x140+{}+{}".format(rootx+win_width-300-self.MARGE, rooty+self.MARGE))
        self.diagram = diagram
        self.SVG_labels = dict()
        self.draw_grid()

    def draw_grid(self):
        """ Draw the grid to put the buttons and the labels in the Window.
        """
        # SVG cell : Marge
        self.create_entry(self.SVG_labels, "Marge",
                          row=1, default_value="0")
        self.SVG_labels["Marge"].bind("<FocusOut>", self.check_marge)
        # SVG cell : opacity
        self.create_entry(self.SVG_labels, "Background opacity",
                          row=2, default_value="1")
        opacity_label = tki.Label(
            self.window, text="  0(transparency) to 1(opacity)", anchor="w")
        opacity_label.pack(side=tki.LEFT)

    def create_entry(self, dico_labels, name, **kwargs):
        """ Create the label and cell, places them in the grid, and adds them to the dictionary.
        """
        row = 0
        cell_type = "Label"
        default_value = 0
        for k, v in kwargs.items():
            if k == 'row':
                row = v
            elif k == 'cell_type':
                cell_type = v
            elif k == 'default_value':
                default_value = v
            else:
                raise Exception("The parameter " + k + " doesn't exist.")
        label = tki.Label(self.frame, text=name, anchor="w")
        label.grid(row=row, column=1, sticky=tki.W)
        if cell_type == "Label":
            if type(default_value) == int:
                value = tki.IntVar()
            else:
                value = tki.StringVar()
            value.set(default_value)
            cell = tki.Entry(self.frame, textvariable=value)
        elif cell_type == "Box":
            value = tki.IntVar()
            value.set(default_value)
            cell = tki.Checkbutton(
                self.frame, variable=value, onvalue=1, offvalue=0)
        else:
            cell = None
        if cell is not None:
            cell.grid(row=row, column=2)
            dico_labels[name] = cell

    def cmd_cancel(self):
        self.window.destroy()

    def cmd_commit(self):
        """ Launche the rendering function according to the choice made between the PNG or SVG format.
        """
        if not self.diagram.is_empty():
            selected_file = fd.asksaveasfile(
                title='Save SVG file', defaultextension=".svg")
            if selected_file is not None:
                self.export_SVG(selected_file)
        self.window.destroy()

    def export_SVG(self, selected_file):
        """ Export the diagram in the SVG format.
        """
        marge_str = self.SVG_labels["Marge"].get()
        marge = tl.cast_to_int(marge_str)
        if marge is None or marge > 1000:
            marge = 0
        background_color_str = self.parent.preferences["main background color_color"]
        background_color = tl.cast_to_color(background_color_str)
        if background_color is None:
            background_color = 'white'
        opacity_str = self.SVG_labels["Background opacity"].get()
        opacity = tl.cast_to_float(opacity_str, "unit")
        file_name = selected_file.name
        saveall(file_name, self.parent.can)
        if background_color is not None:
            with open(file_name) as f:
                file_text = f.read()
            if "viewBox=" in file_text and "width=\"" in file_text:
                origin = file_text.index("width=\"") + len("width=\"")
                start = file_text.index("viewBox=") + len("viewBox=")
                end = file_text[start:].index(">") + start
                parameters_str = file_text[start:end].replace("\"", "")
                parameters = parameters_str.split(" ")
                good_format = True
                for i in range(4):
                    value = tl.cast_to_float(parameters[i])
                    if value is not None:
                        if i <= 1:
                            parameters[i] = str(value - marge)
                        else:
                            parameters[i] = str(value + 2*marge)
                    else:
                        good_format = False
                if good_format and len(parameters) == 4:
                    x, y, w, h = parameters
                    line = w+"\" height=\""+h+"\" viewBox=\""
                    line += x+" "+y+" "+w+" "+h+"\">"
                    line += "<rect x=\""+x+"\" y=\""+y+"\" width=\"" + \
                        w+"\" height=\""+h+"\" style=\"fill:"+background_color+";"
                    if opacity is not None:
                        line += "fill-opacity:" + str(opacity)
                    line += "\" />"
                    new_file_text = file_text[:origin] + \
                        line + file_text[end+1:]
                    with open(file_name, 'w') as f:
                        f.write(new_file_text)

    def check_marge(self, event):
        if "Marge" in self.SVG_labels.keys():
            entry = self.SVG_labels["Marge"]
            value = entry.get()
            if value.isdigit() or value == "":
                entry.config(bg='white')
                return True
            else:
                entry.config(bg=self.colors["DANGER"])
                return False
