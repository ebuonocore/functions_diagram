import tkinter as tki
from tkinter import font
from PIL import Image, ImageTk
from diagram import *
import tools as tl
from window_pattern import *
from tkinter import colorchooser


class Window_edition(Window_pattern):
    def __init__(self, parent_window, diagram, destination):
        super().__init__(parent_window, diagram)
        if destination is not None:
            self.destination = destination
        else:
            self.cmd_cancel()
        self.parameters = dict()
        self.entries = dict()
        self.widget_grid = (
            dict()
        )  # keys: widget / values : tuple(line, column on the grid)
        self.next_entry_to_add = ""  # Name of the next node to add
        self.draw_grid()
        rootx = self.parent.can.winfo_rootx()
        rooty = self.parent.can.winfo_rooty()
        win_width, win_height = self.window_dimension(self.parent.tk.geometry())
        if type(self.destination) == Node:
            self.window.geometry(
                "300x180+{}+{}".format(
                    rootx + win_width - 300 - self.MARGIN, rooty + self.MARGIN
                )
            )
        elif type(self.destination) == Function_block:
            height = (len(self.widget_grid) + 1) * self.parent.text_char_height + 40
            self.window.geometry(
                "300x{}+{}+{}".format(
                    height, rootx + win_width - 300 - self.MARGIN, rooty + self.MARGIN
                )
            )
        elif type(self.destination) == Group:
            height = (len(self.widget_grid) + 1) * self.parent.text_char_height + 40
            self.window.geometry(
                "300x240+{}+{}".format(
                    rootx + win_width - 300 - self.MARGIN, rooty + self.MARGIN
                )
            )
        self.resize_height()

    def draw_grid(self):
        position = (
            str(self.destination.position[0]) + "," + str(self.destination.position[1])
        )
        self.parameters["name"] = self.create_entry(0, "Name", self.destination.name)
        self.parameters["name"].configure(state="disabled")
        self.parameters["name"].config(bg=self.colors["LABEL"])
        self.parameters["label"] = self.create_entry(1, "Label", self.destination.label)
        self.parameters["label"].bind("<FocusOut>", self.check_label)
        self.parameters["position"] = self.create_entry(2, "Position", str(position))
        self.parameters["position"].bind("<FocusOut>", self.check_position)
        self.parameters["fixed"] = self.create_box(
            3, "Auto/Fixed", int(self.destination.fixed)
        )
        # Add specfic lines for function or node
        if type(self.destination) == Node:
            self.node_parameters()
        elif type(self.destination) == Function_block:
            self.function_parameters()
        elif type(self.destination) == Group:
            self.group_parameters()

    def function_parameters(self):
        self.entries = dict()
        self.window.title("Edit function")
        dimension = (
            str(self.destination.dimension[0])
            + ","
            + str(self.destination.dimension[1])
        )
        self.parameters["dimension"] = self.create_entry(4, "Dimension", str(dimension))
        self.parameters["dimension"].bind("<FocusOut>", self.check_dimension)
        if not self.destination.fixed:
            self.parameters["dimension"].configure(state="disabled")
            self.parameters["dimension"].config(bg=self.colors["LABEL"])
        self.parameters["output"] = self.create_entry(
            5, "Output", str(self.destination.output.annotation)
        )
        self.parameters["output"].bind(
            "<FocusOut>",
            lambda event: self.change_node_attribut(
                self.destination.output, "annotation", self.parameters["output"].get()
            ),
        )
        self.parameters["output_visible"] = self.create_box(
            6, "Hide/Show output", int(self.destination.output.visible)
        )
        if self.destination.header_color is None:
            header_color = ""
        else:
            header_color = self.destination.header_color
        self.parameters["header_color"] = self.create_entry(
            7, "Header color", header_color
        )
        self.parameters["header_color"].bind("<FocusOut>", self.check_color)
        bt = tki.Button(
            self.frame, image=self.painting_can_image, command=self.colorchooser
        )
        bt.grid(row=7, column=2, ipadx=16)
        line_number = 8
        entry = None
        for entry in self.destination.entries:
            label_field, value_field, bt = self.create_parameter(
                line_number, entry, button="delete"
            )
            self.entries[entry.name] = (label_field, value_field, bt)
            label_field.bind("<FocusOut>", self.update_all_entries)
            value_field.bind("<FocusOut>", self.update_all_entries)
            line_number += 1
        if entry is not None:
            name = self.next_entry_name(entry.name)
        else:
            name = self.destination.name + "<0"
        previous_labels = [entry.label for entry in self.destination.entries]
        label = tl.new_label(previous_labels)
        next_entry = Node(name=name, label=label, annotation="")
        label_field, value_field, bt = self.create_parameter(
            line_number, next_entry, button="add"
        )
        self.next_entry_to_add = next_entry.name
        self.entries[next_entry.name] = (label_field, value_field, bt)

    def node_parameters(self):
        self.window.title("Edit node")
        self.parameters["annotation"] = self.create_entry(
            4, "Annotation", self.destination.annotation
        )
        self.parameters["annotation"].bind(
            "<FocusOut>",
            lambda event: self.change_destination_attribut(
                "annotation", self.parameters["annotation"].get()
            ),
        )
        self.parameters["justify"] = self.create_choice(
            5,
            "Justify",
            ["left", "center", "separator", "right"],
            self.destination.justify,
        )

    def group_parameters(self):
        self.window.title("Edit group")
        dimension = (
            str(self.destination.dimension[0])
            + ","
            + str(self.destination.dimension[1])
        )
        color = self.destination.color
        thickness = self.destination.thickness
        group_margin = self.destination.margin
        self.parameters["dimension"] = self.create_entry(4, "Dimension", dimension)
        self.parameters["dimension"].bind("<FocusOut>", self.check_dimension)
        if not self.destination.fixed:
            self.parameters["dimension"].configure(state="disabled")
            self.parameters["dimension"].config(bg=self.colors["LABEL"])
            self.parameters["position"].configure(state="disabled")
            self.parameters["position"].config(bg=self.colors["LABEL"])
        self.parameters["color"] = self.create_entry(5, "Color", color)
        self.parameters["color"].bind("<FocusOut>", self.check_color)
        bt = tki.Button(
            self.frame, image=self.painting_can_image, command=self.colorchooser
        )
        bt.grid(row=5, column=2, ipadx=16)
        self.parameters["thickness"] = self.create_entry(6, "Thickness", thickness)
        self.parameters["thickness"].bind("<FocusOut>", self.check_int)
        self.parameters["margin"] = self.create_entry(7, "Margin", group_margin)
        self.parameters["margin"].bind("<FocusOut>", self.check_margin)
        if self.destination.fixed:
            self.parameters["margin"].configure(state="disabled")
            self.parameters["margin"].config(bg=self.colors["LABEL"])
        nb_line = 8
        current_type = ""
        self.destination.update_existing_elements(self.diagram)
        for element in self.destination.elements:
            # Don't display elements that are not in the diagram
            element_Ok = False
            if element["type"] == "Node":
                if element["element"].name in self.diagram.nodes:
                    element_Ok = True
            elif element["type"] == "Function_block":
                if element["element"].name in self.diagram.functions:
                    element_Ok = True
            if element_Ok:
                if element["type"] != current_type:
                    current_type = element["type"]
                    label_title = "Node" if current_type == "Node" else "Function"
                    tki.Label(
                        self.frame,
                        text=label_title,
                        anchor="w",
                        font=font.Font(weight="bold"),
                    ).grid(row=nb_line, column=0, sticky=tki.W)
                    nb_line += 1
                ref = element["id"]
                self.parameters[current_type + element["element"].name] = (
                    self.create_group_box(
                        nb_line, ref, element["element"], element["enable"]
                    ),
                )
                nb_line += 1
        tki.Label(self.frame, text="Delete all!", anchor="w").grid(
            row=nb_line, column=0, sticky=tki.W
        )
        tki.Label(self.frame, text="group & selected items", anchor="w").grid(
            row=nb_line, column=1, sticky=tki.W
        )
        bt = tki.Button(
            self.frame,
            image=self.garbage_image,
            command=lambda: self.delete_all_elements(self.destination),
        )
        bt.grid(row=nb_line, column=2, ipadx=16)

    def create_entry(self, line_number, key, default_value, **kwargs):
        self.button = ""
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")
        tki.Label(self.frame, text=key, anchor="w").grid(
            row=line_number, column=0, sticky=tki.W
        )
        value = tki.StringVar()
        value.set(default_value)
        entry = tki.Entry(self.frame, textvariable=value)
        entry.grid(row=line_number, column=1, sticky=tki.W)
        self.widget_grid[entry] = (line_number, 1)
        return entry

    def create_parameter(self, line_number, entry, **kwargs):
        self.button = ""
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")
        label_var = tki.StringVar()
        label_var.set(entry.label)
        label_field = tki.Entry(self.frame, textvariable=label_var, justify=tki.CENTER)
        label_field.config(bg=self.colors["LABEL"])
        label_field.grid(row=line_number, column=0)
        self.widget_grid[label_field] = (line_number, 0)
        value = tki.StringVar()
        value.set(entry.annotation)
        value_field = tki.Entry(self.frame, textvariable=value)
        value_field.grid(row=line_number, column=1)
        self.widget_grid[value_field] = (line_number, 1)
        bt = None
        if self.button == "delete":
            bt = tki.Button(
                self.frame,
                image=self.garbage_image,
                command=lambda: self.delete_line(line_number, entry),
            )
            bt.grid(row=line_number, column=2, ipadx=16)
        elif self.button == "add":
            bt = tki.Button(
                self.frame,
                image=self.add_image,
                command=lambda: self.add_line(line_number),
            )
            bt.grid(row=line_number, column=2, ipadx=16)
        return label_field, value_field, bt

    def create_box(self, line_number, key, default_value, **kwargs):
        self.button = ""
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")
        tki.Label(self.frame, text=key, anchor="w").grid(
            row=line_number, column=0, sticky=tki.W
        )
        value = tki.IntVar()
        value.set(default_value)
        box = tki.Checkbutton(
            self.frame,
            variable=value,
            onvalue=1,
            offvalue=0,
            command=lambda: self.check_box(key, value.get()),
        )
        box.grid(sticky=tki.W, row=line_number, column=1)
        return box

    def create_group_box(self, line_number, ref, element, default_value, **kwargs):
        self.button = ""
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")
        tki.Label(self.frame, text=element.name, anchor="w").grid(
            row=line_number, column=0, sticky=tki.W
        )
        value = tki.IntVar()
        value.set(default_value)
        box = tki.Checkbutton(
            self.frame,
            variable=value,
            onvalue=1,
            offvalue=0,
            command=lambda: self.change_group_element(ref, value.get()),
        )
        box.grid(sticky=tki.W, row=line_number, column=1)
        return box

    def create_choice(self, line_number, key, choices, default_value, **kwargs):
        self.button = ""
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")
        tki.Label(self.frame, text=key, anchor="w").grid(
            row=line_number, column=0, sticky=tki.W
        )
        value = tki.StringVar()
        value.set(default_value)
        choice = tki.OptionMenu(self.frame, value, *choices, command=self.commit_choice)
        choice.grid(sticky=tki.W, row=line_number, column=1)
        return choice

    def cmd_commit(self):
        self.parameters["name"].focus_set()
        # Purge the list of deselected items for groups
        if type(self.destination) == Group:
            for ref in range(len(self.destination.elements) - 1, -1, -1):
                element = self.destination.elements[ref]
                if not element["enable"]:
                    self.destination.elements.pop(ref)
        if self.check_label(None):
            self.check_name()
            self.tk.after(10, lambda: self.validate_edition((1, 1)))
            self.tk.after(20, self.close_window)

    def validate_edition(self, grid_position):
        """Change focus twice on different entries to ensure changes are committed."""
        widget_focus = tl.key_of(self.widget_grid, grid_position)
        if widget_focus is not None:
            try:
                widget_focus.focus_set()
            except:
                pass
        else:
            self.parameters["label"].focus_set()

    def close_window(self):
        self.parent.memory.add(self.parent.diagram.export_to_text())
        self.parent.edition_in_progress = False
        self.tk.after(10, self.window.destroy())

    def cmd_cancel(self):
        self.parent.cmd_undo()
        self.parent.edition_in_progress = False
        self.window.destroy()

    def delete_line(self, line_number, entry):
        if entry in self.destination.entries:
            self.parent.diagram.delete_node(entry.name)
            self.destination.entries.remove(entry)
            self.update_windows()

    def add_line(self, line_number):
        label_field, value_field, bt = self.entries[self.next_entry_to_add]
        label = label_field.get()
        value = value_field.get()
        name = self.next_entry_to_add
        new_entry = Node(name=name, label=label, annotation=value)
        self.parent.diagram.add_node(new_entry)
        self.destination.entries.append(new_entry)
        self.update_windows()

    def update_windows(self):
        for entry_name, values in self.entries.items():
            label_field, value_field, bt = values
            label_field.destroy()
            value_field.destroy()
            bt.destroy()
        self.widget_grid = dict()
        self.draw_grid()
        self.resize_height()
        self.update_parent_window()

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

    def colorchooser(self):
        color = colorchooser.askcolor()[1]
        if type(self.destination) == Function_block:
            attribut = "header_color"
        elif type(self.destination) == Group:
            attribut = "color"
        entry = self.parameters[attribut]
        entry.delete(0, tki.END)
        entry.insert(0, color)
        self.change_destination_attribut(attribut, color)

    def check_name(self):
        """Test if this name is already taken by another element.
        Validate it if this is not the case, otherwise, propose a new free name.
        """
        previous_names = previous_names = tl.all_previous_names(self.diagram)
        label = self.parameters["label"].get()
        name = self.parameters["name"].get()
        if label != name.split("*")[0]:
            # name have to be changed
            next_name = label
            if next_name in previous_names:
                next_name = tl.new_label(previous_names, next_name + "*")
            self.diagram.change_destination_name(self.destination, next_name)

    def check_position(self, event):
        if "position" in self.parameters.keys():
            entry = self.parameters["position"]
            value = entry.get()
            if self.is_like_tuple(value):
                entry.config(bg="white")
                position = tl.coordinates(value)
                self.change_destination_attribut("position", position)
            else:
                entry.config(bg=self.colors["DANGER"])

    def check_int(self, event):
        if "thickness" in self.parameters.keys():
            entry = self.parameters["thickness"]
            value = entry.get()
            if value == "" or value.isdigit():
                entry.config(bg="white")
                self.change_destination_attribut("thickness", value)
            else:
                entry.config(bg=self.colors["DANGER"])

    def check_margin(self, event):
        if "margin" in self.parameters.keys():
            entry = self.parameters["margin"]
            value = entry.get()
            if value == "" or value.isdigit():
                entry.config(bg="white")
                self.change_destination_attribut("margin", value)
                self.destination.update_coordinates()
                self.update_windows()
            else:
                entry.config(bg=self.colors["DANGER"])

    def check_dimension(self, event):
        if "dimension" in self.parameters.keys():
            entry = self.parameters["dimension"]
            value = entry.get()
            if self.is_like_tuple(value):
                entry.config(bg="white")
                dimension = tl.coordinates(value)
                self.change_destination_attribut("dimension", dimension)
            else:
                entry.config(bg=self.colors["DANGER"])

    def check_label(self, event):
        if "label" in self.parameters.keys():
            entry = self.parameters["label"]
            value = entry.get()
            if "*" in value:
                entry.config(bg=self.colors["DANGER"])
                return False
            elif type(self.destination) != Group and value == "":
                entry.config(bg=self.colors["DANGER"])
                return False
            else:
                entry.config(bg="white")
                self.change_destination_attribut("label", value)
                self.check_name()
                return True

    def check_color(self, event):
        if type(self.destination) == Group:
            attribut = "color"
        elif type(self.destination) == Function_block:
            attribut = "header_color"
        if attribut in self.parameters.keys():
            entry = self.parameters[attribut]
            color = entry.get()
            color_ok = False
            if color == "":
                color = None
                color_ok = True
            elif tl.cast_to_color(color, "hex") is not None:
                color_ok = True
            elif tl.cast_to_color(color) is not None:
                color = tl.cast_rgb_to_hex_color(color)
                color_ok = True
            if color_ok == False:
                entry.config(bg=self.colors["DANGER"])
                return False
            else:
                entry.config(bg="white")
                self.change_destination_attribut(attribut, color)
                return True

    def check_box(self, key, value):
        if key == "Auto/Fixed":
            if bool(value):
                # Fixed mode: Just deselect all elements
                self.destination.__dict__["fixed"] = True
                if type(self.destination) == Group:
                    for ref, element in enumerate(self.destination.elements):
                        self.change_group_element(
                            ref, False, redraw=False, redim=bool(value)
                        )
            else:
                # Auto mode: Select all elements, update dimensions and update the window
                self.destination.__dict__["fixed"] = False
                if type(self.destination) == Group:
                    for ref, element in enumerate(self.destination.elements):
                        self.change_group_element(
                            ref, True, redraw=False, redim=bool(value)
                        )
                    self.destination.update_coordinates()
                    self.update_windows()
        elif key == "Hide/Show output":
            self.destination.set_output_visibility(value)
        self.update_windows()

    def commit_choice(self, event):
        value = self.parameters["justify"].cget("text")
        self.change_destination_attribut("justify", value)

    def change_destination_attribut(self, attribut, value):
        self.destination.__dict__[attribut] = value
        self.update_parent_window()

    def change_node_attribut(self, node, attribut, value):
        node.__dict__[attribut] = value
        self.update_parent_window()

    def change_group_element(self, ref, value, redraw=True, redim=True):
        group = self.destination
        elements = group.elements
        if ref < len(elements):
            elements[ref]["enable"] = bool(value)
            if redim:
                group.update_coordinates()
            if redraw:
                self.update_windows()

    def update_all_entries(self, event):
        # Abort changes if there are two labels with the same name
        labels = []
        for entry_name, (label_field, value_field, bt) in self.entries.items():
            labels.append(label_field.get())
        for label in labels:
            if labels.count(label) > 1:
                self.update_windows()
                return None
        # Commit all changes
        for entry_name, values in self.entries.items():
            label_field, value_field, bt = values
            node = self.destination.search_node(entry_name)
            if node is not None:
                label = label_field.get()
                self.change_node_attribut(node, "label", label)
                value = value_field.get()
                self.change_node_attribut(node, "annotation", value)
        self.update_windows()

    def next_entry_name(self, entry_name):
        """Return the name of the next entry: add one on the index after the '<' symbol"""
        if "<" in entry_name:
            sep_position = entry_name.index("<")
            prefix = entry_name[: sep_position + 1]
            suffix = entry_name[sep_position + 1 :]
            if suffix.isdigit():
                next_suffix = str(int(suffix) + 1)
                return prefix + next_suffix
        return None

    def delete_all_elements(self, group):
        """Delete all the elements (functions and nodes) in the group."""
        for element in group.elements:
            if element["enable"]:
                if type(element["element"]) == Function_block:
                    self.diagram.delete_function(element["element"].name)
                elif type(element["element"]) == Node:
                    self.diagram.delete_node(element["element"].name)
        self.diagram.delete_group(group.name)
        self.parent.draw()
        self.cmd_cancel()
