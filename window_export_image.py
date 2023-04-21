import tkinter as tki
from PIL import Image, ImageTk
from diagram import *
import tools as tl
from tkinter import filedialog as fd
from canvasvg import saveall
from os import remove
from window_settings import *


class Window_export_image(Window_settings):
    def __init__(self, parent_window, diagram, destination=None):
        super().__init__(parent_window, diagram)
        self.window.title('Export diagram to SVG')
        self.window.geometry("300x230")
        self.diagram = diagram
        self.SVG_labels = dict()
        self.draw_grid()

    def draw_grid(self):
        """ Draws the grid to put the buttons and the labels in the Window.
        """
        # SVG cell : Marge
        self.create_entry(self.SVG_labels, "Marge",
                          row=4, default_value="0")
        self.SVG_labels["Marge"].bind("<FocusOut>", self.check_marge)
        # SVG cell : Background color
        self.create_entry(self.SVG_labels, "Background",
                          row=5, default_value="(255, 255, 255)")
        self.SVG_labels["Background"].bind("<FocusOut>", self.check_background)
        # SVG cell : opacity
        self.create_entry(self.SVG_labels, "Opacity",
                          row=6, default_value="1")
        # SVG cell : Spacer
        self.create_entry(self.SVG_labels, "", row=7, cell_type="Spacer")
        self.resize_height()

    def create_entry(self, dico_labels, name, **kwargs):
        """ Creates the label and cell, places them in the grid, and adds them to the dictionary.
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
        label = tki.Label(self.frame, text=name)
        label.grid(row=row, column=1, sticky=tki.E)
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
        """ Launches the rendering function according to the choice made between the PNG or SVG format.
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
        background_color_str = self.SVG_labels["Background"].get()
        background_color = tl.cast_to_color(background_color_str)
        opacity_str = self.SVG_labels["Opacity"].get()
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

    def check_background(self, event):
        if "Background" in self.SVG_labels.keys():
            entry = self.SVG_labels["Background"]
            value = entry.get()
            if tl.cast_to_color(value) is not None:
                entry.config(bg='white')
                return True
        entry.config(bg=self.colors["DANGER"])
        return False
