from pynput import keyboard
from PIL import Image, ImageTk
from math import pi, cos, sin
from os import path
from tkinter import filedialog as fd
from tkinter import font as tkfont
import tkinter as tki
import tools as tl
from diagram import *
from node import *
from files import *
from memory import *
from window_edition import *
from window_export_image import *
from window_information import *
from window_configuration import *


COLOR_OUTLINE = "#FFFF00"


def message(message, destination=None):
    """Display the message in the console or in the text box on Tkinter."""
    if destination is None:
        print(message)
    else:
        destination.set(message)


class Window:
    class Decorators:
        @classmethod
        def disable_if_editing(cls, func):
            """Decorator function: Invokes the target function if self.edition_in_progress is True"""

            def edition_test(obj):
                result = None
                if obj.edition_in_progress == False:
                    result = func(obj)
                else:
                    message(
                        "Warning: First close the editing window.", obj.text_message
                    )
                    # obj.lift_window(obj.window_edition.window)
                return result

            return edition_test

    def __init__(self, diagram=None):
        self.tk = tki.Tk()
        self.tk.title("Functions Diagram")
        if diagram is None:
            self.diagram = Diagram()
        else:
            self.diagram = diagram
        # Configuration
        self.preferences = tl.load_preferences()
        police = self.preferences["police"]
        title_size = int(self.preferences["title size_int"])
        text_size = int(self.preferences["text size_int"])
        self.title_size = tkfont.Font(family=police, size=title_size, weight="bold")
        self.text_size = tkfont.Font(family=police, size=text_size, weight="normal")
        self.title_char_width, self.title_char_height = tl.character_dimensions(
            police, title_size
        )
        self.text_char_width, self.text_char_height = tl.character_dimensions(
            police, text_size
        )
        # Initialization
        self.state = 1
        self.memory = Memory(50, self.diagram.export_to_text())
        self.MARGIN = 10
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.screen_dimensions()
        self.MARGIN_DOWN = 10
        self.MARGIN_UP = 10
        self.MENU_HEIGHT = 80
        self.smooth_lines = True
        self.window_edition = None
        self.can = tki.Canvas(
            self.tk,
            width=self.SCREEN_WIDTH,
            height=self.SCREEN_HEIGHT,
            bg=self.preferences["main background color_color"],
        )
        self.menu = tki.Canvas(
            self.tk, width=self.SCREEN_WIDTH, height=self.MENU_HEIGHT, bg="#F0F0F0"
        )
        self.menu_label = tki.Label(self.menu)
        self.menu_label.pack(padx=1, pady=1, fill=tki.X, side=tki.LEFT)
        self.margin = tki.Label(self.menu, width=1, bg="#F0F0F0")
        self.margin.pack(side=tki.LEFT)
        self.text_message = tki.StringVar()
        self.text_message.set("\n")
        self.message = tki.Label(
            self.menu, textvariable=self.text_message, bg="#F0F0F0", justify=tki.LEFT
        )
        self.message.pack(side=tki.LEFT)
        self.images, self.images_mini = self.build_images_bank()
        self.buttons = {}
        self.add_buttons()
        self.menu.pack(fill=tki.X)
        self.can.pack()
        self.tk.update()
        self.WIDTH, self.HEIGHT = self.canvas_dimensions()
        self.destination = None
        self.origin = None
        self.auto_resize_blocks()
        self.update_positions()
        message("Function_diagram v1.0", self.text_message)
        self.edition_in_progress = False
        self.listener = keyboard.Listener(on_press=self.cmd_keyboard_event)
        self.listener.start()
        self.engine()  # Starts state management

    def screen_dimensions(self):
        WIDTH = self.tk.winfo_screenwidth()
        HEIGHT = self.tk.winfo_screenheight()
        return WIDTH, HEIGHT

    def canvas_dimensions(self):
        WIDTH = self.tk.winfo_width()
        HEIGHT = self.tk.winfo_height() - self.MENU_HEIGHT
        return WIDTH, HEIGHT

    def auto_resize_blocks(self):
        """Scan all function_blocks and automatically resizes those that do not have dimensions (to []).
        Take into account the font size.
        height: function of the number of entries + 1
        width: function of the maximum number of characters of the longest entry or title
        """
        for function in self.diagram.functions.values():
            if not function.fixed:
                if len(function.entries) > 0:
                    longest_name = max(
                        [
                            len(entry.label) + len(entry.annotation)
                            for entry in function.entries
                        ]
                    )
                    # Ajout de 2 caractèreAdd two characters ': '
                    max_width = (longest_name + 2) * self.text_char_width
                else:
                    max_width = 0
                max_width = (
                    max(max_width, len(function.label) * self.title_char_width)
                    + 2 * self.MARGIN
                )
                max_height = (
                    max(len(function.entries), 1) * self.text_char_height
                    + 2 * self.MARGIN
                )
                function.dimension = (max_width, max_height)

    def position_functions_nodes(self):
        """Position the nodes linked to the functions."""
        # Place the nodes of the functions
        for function in self.diagram.functions.values():
            # Benchmark: Body frame
            if function.position is not None:
                x, y = function.position
                function_width, function_height = function.dimension
                x_entry = x + self.MARGIN
                y_entry = y + self.title_char_height + self.MARGIN

                for entry in function.entries:
                    # Update the positions of the points in the block
                    entry.position = [
                        x_entry - self.MARGIN,
                        y_entry + self.text_char_height // 2,
                    ]
                    entry.free = False
                    y_entry += self.text_char_height
                # Exit point of the block
                function.output.position = [
                    x + function_width,
                    y + self.title_char_height + function_height // 2,
                ]
                function.output.free = False

    def update_positions(self):
        """The relative positions of functions and points are determined by their floor.
        Unless the positions are fixed.
        Stage 0: Leaves of the directed graph described by self.floors.
        The functions are divided graphically between self.MARGIN_DOWN and self.WIDTH - self.MARGIN_UP
        The free points (not associated with functions) are located on the intermediate levels.
        Update the group positions.
        Return True if the positions have been updated.
        Otherwise, return False if it's not possible (loopback).
        Automatic positioning is deactivated if loopbacks are activated in the settings.
        """
        design = Design(self.diagram.nodes.values(), self.diagram.functions.values())
        if design.status < 300:  # The diagram is valid : No error, no loopback
            message("Automatic positionning", self.text_message)
            functions_dict, self.diagram.floors = design.report()
            for function, level in functions_dict.items():
                function.floor = level
            # Search for the maximum floor
            floor_max = design.max_floor
            # Imposes the abscissa of unfixed function_blocks.
            nb_intervals = floor_max + 1
            interval_width = (self.WIDTH - 2 * self.MARGIN) // nb_intervals
            offset = 0
            if self.preferences["automatic spacing_int"].isdigit():
                preference_spacing = int(self.preferences["automatic spacing_int"])
                if preference_spacing > 0 and preference_spacing < interval_width:
                    interval_width = preference_spacing
                    offset = (self.WIDTH - interval_width * nb_intervals) // 2
            else:
                message("Invalid value for automatic spacing", self.text_message)
            free_height = self.HEIGHT - self.MARGIN_UP - self.MARGIN_DOWN
            for function in self.diagram.functions.values():
                floor = function.floor
                if function.fixed == False:
                    function.position[0] = (
                        self.MARGIN
                        + (floor + 0.5) * interval_width
                        + offset
                        - function.dimension[0] // 2
                    )
                    rank = tl.function_rank(function, self.diagram.floors[floor])
                    ratio = (rank + 1) / (len(self.diagram.floors[floor]) + 1)
                    function.position[1] = (
                        round(free_height * ratio)
                        + self.MARGIN_UP
                        - function.dimension[1] // 2
                    )
            # Position the nodes linked to the functions
            self.position_functions_nodes()

            # Calculate the position of free nodes based on the positions of related non-free nodes.
            for node in self.diagram.nodes.values():
                if node.free and not node.fixed:
                    max_abscissas = self.WIDTH - self.MARGIN - offset // 2
                    min_abscissas = self.MARGIN + offset // 2
                    ordinates = []
                    for connected_node in node.connections:
                        # This point is a function input
                        if "<" in connected_node.name:
                            ordinates.append(connected_node.position[1])
                            max_abscissas = min(
                                max_abscissas, connected_node.position[0]
                            )
                        # This point is a function output
                        elif ">" in connected_node.name:
                            ordinates.append(connected_node.position[1])
                            min_abscissas = max(
                                min_abscissas, connected_node.position[0]
                            )
                    node.position[0] = (min_abscissas + max_abscissas) // 2
                    if len(ordinates) == 0:
                        node.position[1] = self.MARGIN_UP + free_height // 2
                    else:
                        node.position[1] = sum(ordinates) / len(ordinates)
            for group in self.diagram.groups.values():
                if group.fixed == False:
                    group.update_coordinates()
            return True
        else:
            message("Position update impossible: Cycle detected.", self.text_message)
            return False

    def draw(self):
        """Update the system display in the Tkinter window"""
        try:
            # Delete all objects from the canvas before recreating them
            self.can.delete("all")
            self.can.configure(bg=self.preferences["main background color_color"])
            # Draw all the elements of the system
            self.draw_functions()
            self.draw_nodes()
            self.draw_lines()
            self.draw_groups()
        except:
            pass

    def draw_nodes(self):
        """Draw discs for isolated points and arrows for points linked to blocks."""
        police = self.preferences["police"]
        text_size = int(self.preferences["text size_int"])

        font_texte = tkfont.Font(family=police, size=text_size, weight="normal")
        color = self.preferences["line color_color"]
        text_color = self.preferences["text color_color"]
        d = int(self.preferences["text size_int"]) // 2
        for node_name, node in self.diagram.nodes.items():
            if node.position != [None, None] and node.visible:
                x, y = node.position
                if node.free:
                    justify = node.justify
                    if justify is None:
                        justify = self.preferences["justify_choice"]
                    self.can.create_oval(x - d, y - d, x + d, y + d, fill=color)
                    self.print_label(
                        x,
                        y - self.MARGIN,
                        node.label,
                        node.annotation,
                        "sw",
                        justify,
                    )
                else:  # Entry of a function
                    self.draw_triangle(x, y, 0)
                    if ">" in node.name:
                        self.print_label(
                            x + (self.MARGIN) // 3,
                            y - self.MARGIN,
                            node.label,
                            node.annotation,
                            "w",
                        )
                    else:  # Exit of a function
                        self.print_label(x + 2, y, node.label, node.annotation, "w")

    def draw_triangle(self, x, y, orientation=0, color=None, d=None):
        """Draw an isosceles triangle. Origin = H, intersection of the main height and the base.
        Orientation: 0 = East, 1 = South, 2 = West, 3 = North
        """
        if color is None:
            color = self.preferences["line color_color"]
        if d is None:
            d = int(self.preferences["text size_int"]) // 2
        perimeter = [
            [x - 2 * d, y - d, x, y, x - 2 * d, y + d],
            [x - d, y + 2 * d, x, y, x + d, y + 2 * d],
            [x + 2 * d, y - d, x, y, x + 2 * d, y + d],
            [x - d, y - 2 * d, x, y, x + d, y - 2 * d],
        ]
        self.can.create_polygon(perimeter[orientation], fill=color)

    def print_label(
        self, x, y, label, annotation="", anchor="nw", justify=None, color=None
    ):
        """Write the label and if necessary the type annotation separated by :"""
        police = self.preferences["police"]
        text_size = int(self.preferences["text size_int"])
        font = tkfont.Font(family=police, size=text_size, weight="normal")
        text_color = self.preferences["text color_color"]
        if color is not None:
            text_color = color
        type_color = self.preferences["type color_color"]
        # If justify is not None, its value is "left", "center","separator" or "right"
        total_text = label
        sep_text = label
        if len(annotation) != 0:
            total_text += ": " + annotation
            sep_text += ":"
        len_total_text = tkfont.Font(
            size=text_size, family=police, weight="normal"
        ).measure(total_text)
        len_sep_text = tkfont.Font(
            size=text_size, family=police, weight="normal"
        ).measure(sep_text)
        # Calculate the offset of the text according to the justification
        justify_offset = {
            None: 0,
            "left": 0,
            "right": len_total_text,
            "center": len_total_text // 2,
            "separator": len_sep_text,
        }
        x -= justify_offset[justify]
        # Display the label
        if len(annotation) > 0 and len(label) > 0:
            label += ": "
        self.can.create_text(
            x, y, text=label, font=font, anchor=anchor, fill=text_color
        )
        if len(annotation) > 0:
            offset = tkfont.Font(
                size=text_size, family=police, weight="normal"
            ).measure(label)
            x_type = x + offset
            self.can.create_text(
                x_type, y, text=annotation, font=font, anchor=anchor, fill=type_color
            )

    def draw_functions(self):
        """Draw the function_block: Header, body frames.
        Update the positions of the points in the block: Inputs and outputs
        """
        police = self.preferences["police"]
        title_size = int(self.preferences["title size_int"])
        text_size = int(self.preferences["text size_int"])
        text_color = self.preferences["text color_color"]
        thickness = int(self.preferences["border thickness_int"])
        font_titre = tkfont.Font(family=police, size=title_size, weight="bold")
        font_texte = tkfont.Font(family=police, size=text_size, weight="normal")
        border_color = self.preferences["borders default color_color"]
        title_background_color = self.preferences["title background color_color"]
        function_background_color = self.preferences["function background color_color"]
        rounded = True if self.preferences["rounded functions_bool"] == 1 else False
        for function in self.diagram.functions.values():
            # Drawing of the body frame
            if function.position is not None:
                x, y = function.position
                function_width, function_height = function.dimension
                if function.header_color is None:
                    header_color = title_background_color
                else:
                    header_color = function.header_color
                # Drawing of the function name frame
                tl.draw_box(
                    self.can,
                    x,
                    y,
                    x + function_width,
                    y + self.title_char_height,
                    outline=border_color,
                    fill=header_color,
                    thickness=thickness,
                    rounded_up=rounded,
                )

                # Drawing of the body of the function
                tl.draw_box(
                    self.can,
                    x,
                    y + self.title_char_height,
                    x + function_width,
                    y + self.title_char_height + function_height,
                    outline=border_color,
                    fill=function_background_color,
                    thickness=thickness,
                    rounded_down=rounded,
                    radius=self.title_char_height // 2,
                )

                # Writing the function name
                x_titre = x + function_width // 2
                y_titre = y + self.title_char_height // 2
                texte = function.label
                self.can.create_text(
                    x_titre,
                    y_titre,
                    text=texte,
                    font=font_titre,
                    anchor="center",
                    fill=text_color,
                )

    def draw_lines(self):
        """Draw the connections between the points: Vertical or horizontal lines."""
        thikness = int(self.preferences["line thikness_int"])
        color = self.preferences["line color_color"]
        smooth = True if self.preferences["smooth lines_bool"] == 1 else False
        self.diagram.update_links()
        lines_ok = set()  # Set of tuples (point_of_departure, point_of_arrival)
        for link in self.diagram.links:
            x_start, y_start = link.points[0]
            x_first, y_first = link.points[1]
            x_middle, y_middle = link.points[2]
            x_last, y_last = link.points[3]
            x_end, y_end = link.points[4]
            if smooth:
                self.can.create_line(
                    (x_start, y_start),
                    (x_first, y_start),
                    (x_middle, y_middle),
                    (x_last, y_end),
                    (x_end, y_end),
                    fill=color,
                    width=thikness,
                    smooth="true",
                )
            else:
                self.can.create_line(
                    (x_start, y_start), (x_middle, y_start), fill=color, width=thikness
                )
                self.can.create_line(
                    (x_middle, y_start), (x_middle, y_end), fill=color, width=thikness
                )
                self.can.create_line(
                    (x_middle, y_end), (x_end, y_end), fill=color, width=thikness
                )

    def draw_groups(self):
        pref_color = self.preferences["group color_color"]
        pref_thickness = int(self.preferences["group thickness_int"])
        for group in self.diagram.groups.values():
            if group.color == "" or group.color is None:
                color = pref_color
            else:
                color = group.color
            thickness = group.thickness if group.thickness != "" else pref_thickness
            dash = int(thickness) * 2
            x_origin, y_origin = group.position
            width, height = group.dimension
            x_end, y_end = x_origin + width, y_origin + height
            self.can.create_rectangle(
                x_origin,
                y_origin,
                x_end,
                y_end,
                dash=(dash, dash),
                fill="",
                outline=color,
                width=thickness,
            )
            self.print_label(
                x_origin, y_origin - self.text_char_height, group.label, color=color
            )

    def draw_destination_outine(self, color=COLOR_OUTLINE):
        if type(self.destination) == Link:
            d = 2 * int(self.preferences["text size_int"]) // 3
            x, y = self.destination.position
            self.can.create_rectangle(
                x - 2, y - 2, x + 2, y + 2, width=2, outline=color
            )
        if type(self.destination) == Node:
            d = 2 * int(self.preferences["text size_int"]) // 3
            x, y = self.destination.position
            if self.destination.free:
                self.can.create_oval(x - d, y - d, x + d, y + d, fill=color)
            else:
                scale = int(self.preferences["text size_int"]) // 3
                self.draw_triangle(x - scale // 2, y, 0, color, scale)
        elif type(self.destination) == Function_block:
            x, y = self.destination.position
            width, height = self.destination.dimension
            self.can.create_rectangle(
                x - 2,
                y - 2,
                x + width + 2,
                y + self.title_char_height + height + 2,
                width=2,
                outline=color,
            )
        elif type(self.destination) == Group:
            x, y = self.destination.position
            width, height = self.destination.dimension
            self.can.create_rectangle(
                x - 2,
                y - 2,
                x + width + 2,
                y + height + 2,
                width=2,
                outline=color,
            )

    def import_image(self, name):
        """Import the image according to the name passed in parameter
        Return the refernces of the original image and the resized image.
        """
        file = "images/" + name + ".png"
        image_source = Image.open(file)
        image = ImageTk.PhotoImage(image_source)
        resized_image = image_source.resize((25, 25), Image.ANTIALIAS)
        image_mini = ImageTk.PhotoImage(resized_image)
        return image, image_mini

    def build_images_bank(self):
        bank = dict()
        bank_mini = dict()
        for button_name in [
            "new",
            "open",
            "save",
            "export",
            "move",
            "add_function",
            "add_node",
            "group",
            "add_link",
            "edit",
            "erase",
            "auto",
            "undo",
            "redo",
            "configuration",
            "information",
        ]:
            bank[button_name], bank_mini[button_name] = self.import_image(button_name)
        return bank, bank_mini

    def create_button(self, name, command):
        self.buttons[name] = tki.Button(
            self.menu_label, image=self.images[name], command=command
        )

    def add_buttons(self):
        """Add the buttons"""
        self.create_button("new", self.cmd_new)  # state:1
        self.create_button("open", self.cmd_open)  # state:1
        self.create_button("save", self.cmd_save)  # state:1
        self.create_button("export", self.cmd_export)
        self.create_button("move", self.cmd_move)  # state:2, 3, 4
        self.create_button("add_function", self.cmd_add_function)
        self.create_button("add_node", self.cmd_add_node)
        self.create_button("group", self.cmd_add_group)
        self.create_button("add_link", self.cmd_add_link)
        self.create_button("edit", self.cmd_edit)
        self.create_button("erase", self.cmd_erase)
        self.create_button("undo", self.cmd_undo)
        self.create_button("redo", self.cmd_redo)
        self.create_button("auto", self.cmd_auto)
        self.create_button("configuration", self.cmd_configuration)
        self.create_button("information", self.cmd_information)
        for button in self.buttons.values():
            button.pack(side=tki.LEFT)

    def lift_window(self, child_window):
        """Move the parent window and the child_window in the stack."""
        try:
            child_window.lift()
            child_window.focus_force()
            child_window.update()
        except:
            pass

    @Decorators.disable_if_editing
    def cmd_new(self):
        """Clear the list of points and functions."""
        message("New diagram.", self.text_message)
        self.state = 1
        self.diagram = Diagram()
        self.draw()

    @Decorators.disable_if_editing
    def cmd_open(self):
        """Open the selected JSON file and rebuilds the system instance.
        Allow to choose the JSON format or the TXT
        Return True if the procedure succeeds otherwise False
        """
        self.can.config(cursor="arrow")
        message("Open file.", self.text_message)
        self.state = 1
        selected_file = fd.askopenfilename(title="Open")
        if selected_file == "":
            message("Canceled opening.", self.text_message)
            return False
        self.diagram = open_file(selected_file)
        file_name = selected_file
        if "/" in file_name:
            file_name = file_name.split("/")[-1]
        if "\\" in file_name:
            file_name = file_name.split("\\")[-1]
        self.auto_resize_blocks()
        self.position_functions_nodes()
        self.draw()
        message("File " + file_name + " opened.", self.text_message)
        self.memory.add(self.diagram.export_to_text())
        return True

    @Decorators.disable_if_editing
    def cmd_save(self):
        """Save the configuration of the diagram as a file."""
        self.can.config(cursor="arrow")
        message("Save diagram.", self.text_message)
        self.state = 1
        selected_file = fd.asksaveasfile(title="Save")
        diagram_datas = self.diagram.export_to_text()
        try:
            selected_file.write(diagram_datas)
            message("Diagram saved.", self.text_message)
            selected_file.close()
            return True
        except:
            message("Backup canceled.", self.text_message)
            return False

    @Decorators.disable_if_editing
    def cmd_add_function(self):
        """Add a nex function block."""
        if self.edition_in_progress == False:
            message("Create a new function.", self.text_message)
            previous_names = [function for function in self.diagram.functions.keys()]
            name = tl.new_label(previous_names)
            label = name.split("*")[0]
            output = Node(name=name + ">")
            new_function = Function_block(
                name=name,
                label=label,
                position=[100, 100],
                dimension=[20, 20],
                output=output,
            )
            self.diagram.add_function(new_function)
            self.destination = new_function
            self.edit(self.destination)
            self.draw()
        else:
            message("Edition already open.", self.text_message)
            self.lift_window(self.window_edition.window)

    @Decorators.disable_if_editing
    def cmd_add_node(self):
        """Add a new node."""
        if self.edition_in_progress == False:
            message("Create a new node.", self.text_message)
            previous_names = [node for node in self.diagram.nodes.keys()]
            name = tl.new_label(previous_names)
            new_node = Node(name=name, label=name, free=True, position=[100, 100])
            self.diagram.add_node(new_node)
            self.destination = new_node
            self.edit(self.destination)
            self.draw()
        else:
            message("Edition already open.", self.text_message)
            self.lift_window(self.window_edition.window)

    @Decorators.disable_if_editing
    def cmd_add_group(self):
        """Add a new group."""
        message(
            "Create a new group. Click to select two corners of the zone.",
            self.text_message,
        )
        self.can.config(cursor="plus")
        self.state = 8

    @Decorators.disable_if_editing
    def cmd_add_link(self):
        """Add a link between two nodes."""
        if len(self.diagram.nodes) > 0 or len(self.diagram.functions) > 0:
            message("Select the first node.", self.text_message)
            self.can.config(cursor="plus")
            self.state = 6
        else:
            self.state = 1
            message("No object to edit.", self.text_message)
            try:
                self.lift_window(self.window_edition.window)
            except:
                pass

    @Decorators.disable_if_editing
    def cmd_move(self):
        """Allow objects to move."""
        message("Select the free node or the function to move.", self.text_message)
        self.can.config(cursor="fleur")
        self.state = 2

    @Decorators.disable_if_editing
    def cmd_edit(self):
        """Initiate the editing of the selected object."""
        if len(self.diagram.nodes) > 0 or len(self.diagram.functions) > 0:
            message("Select the free node or the function to edit.", self.text_message)
            self.can.config(cursor="pencil")
            self.state = 5
        else:
            self.state = 1
            message("No object to edit.", self.text_message)
            self.lift_window(self.window_edition.window)

    def edit(self, destination):
        """Edit the selected object."""
        self.memory.add(self.diagram.export_to_text())
        self.edition_in_progress = True
        self.window_edition = Window_edition(self, self.diagram, destination)
        self.lift_window(self.window_edition.window)

    @Decorators.disable_if_editing
    def cmd_erase(self):
        """Initiate object deletion."""
        message("Select the free node or the function to erase.", self.text_message)
        self.can.config(cursor="pirate")
        self.state = 4

    def erase(self, destination):
        """Delete the destination object from the functions or the nodes dictionary."""
        if type(destination) == Node:
            node_to_delete = tl.key_of(self.diagram.nodes, destination)
            self.diagram.delete_node(node_to_delete)
        elif type(destination) == Link:
            self.diagram.disconnect_nodes(destination)
        elif type(destination) == Function_block:
            function_to_delete = tl.key_of(self.diagram.functions, destination)
            self.diagram.delete_function(function_to_delete)

    @Decorators.disable_if_editing
    def cmd_export(self):
        """Initiate exportation to image."""
        message("Export diagram to image.", self.text_message)
        self.state = 1
        Window_export_image(self, self.diagram)

    @Decorators.disable_if_editing
    def cmd_auto(self):
        """Update automatically the dimensions and positions of functions and nodes
        to fit the diagram. if loopback detection is enable and if there's no loopback.
        """
        self.state = 1
        self.auto_resize_blocks()
        if self.preferences["enable loopback_bool"] == 0:
            design = Design(
                self.diagram.nodes.values(), self.diagram.functions.values()
            )
            if design.status >= 300:  # Warning or Error detected
                self.preferences["enable loopback_bool"] = 1
                tl.write_preferences(self.preferences)
                message("Loopback detected.", self.text_message)
            else:
                self.update_positions()
            self.memory.add(self.diagram.export_to_text())
        else:
            message("Loopback is enabled.", self.text_message)
        self.draw()

    @Decorators.disable_if_editing
    def cmd_undo(self):
        """ """
        state_description = self.memory.undo()
        if state_description is not None:
            self.diagram = read_state(state_description)
            self.auto_resize_blocks()
            self.position_functions_nodes()
            message(
                "Undo: " + str(self.memory.pointer) + "/" + str(self.memory.size),
                self.text_message,
            )
            self.draw()

    @Decorators.disable_if_editing
    def cmd_redo(self):
        """ """
        state_description = self.memory.redo()
        if state_description is not None:
            self.diagram = read_state(state_description)
            self.auto_resize_blocks()
            self.position_functions_nodes()
            message(
                "Redo: " + str(self.memory.pointer) + "/" + str(self.memory.size),
                self.text_message,
            )
            self.draw()

    @Decorators.disable_if_editing
    def cmd_configuration(self):
        """ """
        Window_configuration(self)

    @Decorators.disable_if_editing
    def cmd_information(self):
        """ """
        Window_information(self, self.images_mini)

    def left_click(self, event):
        Xpix = event.x
        Ypix = event.y
        if self.state == 2:  # Target to move selected
            self.state = 3  # Destination selection
        elif self.state == 3:  # Destination selected
            self.state = 2  # Choose another target to move
            self.memory.add(self.diagram.export_to_text())
        elif self.state == 4:  # Destination to erase selected
            self.erase(self.destination)
            self.memory.add(self.diagram.export_to_text())
            self.draw()
        elif self.state == 5:  # Destination to edit selected
            if self.destination is None:
                self.state = 1
                message("No object to edit.", self.text_message)
            self.edit(self.destination)
            message("", self.text_message)
            self.draw()
            self.state = 1
        elif self.state == 6:  # Add link : Source selected
            self.origin = self.destination
            if self.origin is not None:
                message("Select the node to connect.", self.text_message)
                self.state = 7  # Destination selection
        elif self.state == 7:  # Destination selected
            test_connection = False
            if self.preferences["enable loopback_bool"] == 1:
                test_connection = True
            else:  # Design methods are recursive and should not be launched if there are cycles.
                design = Design(
                    self.diagram.nodes.values(), self.diagram.functions.values()
                )
                if design.status < 300:
                    test_connection = design.are_reachables(
                        self.origin, self.destination
                    )
            if test_connection:
                message("Nodes connected. Select another origin.", self.text_message)
                self.diagram.nodes_connection(self.origin.name, self.destination.name)
            else:
                message("Forbiden link: Output shortcut (loopback).", self.text_message)
            self.draw()
            self.state = 6  # Choose another target to link
            self.memory.add(self.diagram.export_to_text())
        elif self.state == 8:  # Add group : Selecting the first corner
            self.origin = (Xpix, Ypix)
            message("Select the second corner of the group zone.", self.text_message)
            self.state = 9  # Selecting the second corner
        elif self.state == 9:  # Selecting the second corner
            self.destination = (Xpix, Ypix)
            dimension = tl.get_dimension(self.origin, self.destination)
            elements = list()
            empty_zone = True
            previous_names = [group for group in self.diagram.groups.keys()]
            name = tl.new_label(previous_names)
            new_group = Group(
                name=name,
                label=name,
                elements=elements,
                fixed=empty_zone,
                position=self.origin,
                dimension=dimension,
            )
            elements = new_group.search_elements_in(self.diagram, self.origin, self.destination)
            new_group.elements = elements
            self.diagram.add_group(new_group)
            self.destination = new_group
            self.state = 1  # Returns to basic state
            self.edit(self.destination)
            self.draw()

        else:
            self.state = 1  # Returns to basic state

    def right_click(self, event):
        message("", self.text_message)
        self.state = 1
        self.draw()

    def mouse_movement(self, event):
        Xpix = event.x
        Ypix = event.y

    def fermer_fenêtre(self):
        self.tk.quit()
        self.tk.destroy()

    def copy_all(self, event):
        message("Copy all", self.text_message)

    def cmd_keyboard_event(self, key):
        """Cancel operation if the user press Enter or Escape."""
        if key in (keyboard.Key.esc, keyboard.Key.enter):
            if not self.edition_in_progress:
                message("Selection canceled", self.text_message)
                self.state = 1

    def engine(self):
        """State management :
        1 - Basic state
        2 - Move object : Select the origin
        3 - Move object : Select destination
        4 - Erase : Select object to erase
        5 - Edit : Select object to edit
        6 - Add link : Select the origin
        7 - Add link : Select destination
        """
        if self.state == 1:  # Basic state
            self.can.config(cursor="arrow")
        if self.state == 2:  # Move object: Select the origin
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination = tl.nearest_objet((mouse_x, mouse_y), self.diagram)
            self.draw()
            self.draw_destination_outine()
        elif self.state == 3 and self.destination is not None:  # Move to destination
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination.position = [mouse_x, mouse_y]
            # Move the elements of the group
            if type(self.destination) == Group:
                if self.destination.fixed == False:
                    for element in self.destination.elements:
                        x_relative, y_relative = element["position"]
                        element["element"].position = [
                            mouse_x + x_relative,
                            mouse_y + y_relative,
                        ]
            # If it's an element of a group, update the dimensions of the group
            else:
                for group in self.diagram.groups.values():
                    if group.fixed == False:
                        group.follow(self.destination)
            self.position_functions_nodes()
            self.draw()
        elif self.state == 4:  # Select object to erase
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination = tl.nearest_objet(
                (mouse_x, mouse_y), self.diagram, target_types="erasable"
            )
            self.draw()
            self.draw_destination_outine("red")
        elif self.state == 5:  # Select object to edit
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination = tl.nearest_objet((mouse_x, mouse_y), self.diagram)
            self.draw()
            self.draw_destination_outine("green")
        elif self.state == 6:  # Add link : Origin selected
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination, distance = tl.nearest(
                (mouse_x, mouse_y), self.diagram.nodes.values()
            )
            self.draw()
            self.draw_destination_outine()
        elif (
            self.state == 7 and self.origin is not None
        ):  # Add link : Destination selected
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination, distance = tl.nearest(
                (mouse_x, mouse_y), self.diagram.nodes.values()
            )
            self.draw()
            self.draw_destination_outine()
        elif self.state == 9:  # Add group : Selecting the first corner
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.draw()
            if type(self.origin) == tuple:
                x_origin, y_origin = self.origin
                self.can.create_rectangle(
                    x_origin,
                    y_origin,
                    mouse_x,
                    mouse_y,
                    dash=(4, 4),
                    fill="",
                    outline="grey",
                )

        self.tk.after(100, self.engine)  # Restarts state management
