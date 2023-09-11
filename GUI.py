from PIL import Image, ImageTk
from math import pi, cos, sin
from os import path
from tkinter import filedialog as fd
from tkinter import font as tkfont
import tkinter as tki
import tools as tl
import group as grp
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
        self.active_file = None
        self.memory = Memory(50, self.diagram.export_to_text())
        self.zooms = [i / 100 for i in range(10, 310, 10)]
        self.zoom_index = 9
        self.zoom = self.zooms[self.zoom_index]
        self.MARGINS = {"base":10, "up":10, "down":10}
        self.margins = tl.update_dict_ratio(self.MARGINS, self.zoom)  # Margin modified by zoom
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.screen_dimensions()
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
        self.blank = tki.Label(self.menu, width=1, bg="#F0F0F0")
        self.blank.pack(side=tki.LEFT)
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
        self.destination = None  # Element of the selection
        self.origin = None  # First element of the selection
        self.ref_origin = [0 ,0]  # Reference frame origin 
        self.ref_delta_drag = [0, 0]  # Reference offset during movement
        self.tempo_drag = 0  # >0 during drag movement.
        self.auto_resize_blocks()
        self.update_positions()
        message("Function_diagram v1.0", self.text_message)
        self.edition_in_progress = False
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
                    + 2 * self.MARGINS["base"]
                )
                max_height = (
                    max(len(function.entries), 1) * self.text_char_height
                    + 2 * self.MARGINS["base"]
                )
                function.dimension = (max_width, max_height)

    def position_functions_nodes(self):
        """Position the nodes linked to the functions."""
        title_char_height = self.title_char_height
        # Place the nodes of the functions
        for function in self.diagram.functions.values():
            # Benchmark: Body frame
            if function.position is not None:
                x, y = function.position
                function_width, function_height = function.dimension
                x_entry = x + self.MARGINS["base"]
                y_entry = y + title_char_height + self.MARGINS["base"]

                for entry in function.entries:
                    # Update the positions of the points in the block
                    entry.position = [
                        x_entry - self.MARGINS["base"],
                        y_entry + self.text_char_height // 2,
                    ]
                    entry.free = False
                    y_entry += self.text_char_height
                # Exit point of the block
                function.output.position = [
                    x + function_width,
                    y + title_char_height + function_height // 2,
                ]
                function.output.free = False

    def update_positions(self):
        """The relative positions of functions and points are determined by their floor.
        Unless the positions are fixed.
        Stage 0: Leaves of the directed graph described by self.floors.
        The functions are divided graphically between self.MARGINS["down"] and self.WIDTH - self.MARGINS["up"]
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
            interval_width = (self.WIDTH - 2 * self.MARGINS["base"]) // nb_intervals
            offset = 0
            if self.preferences["automatic spacing_int"].isdigit():
                preference_spacing = int(self.preferences["automatic spacing_int"])
                if preference_spacing > 0 and preference_spacing < interval_width:
                    interval_width = preference_spacing
                    offset = (self.WIDTH - interval_width * nb_intervals) // 2
            else:
                message("Invalid value for automatic spacing", self.text_message)
            free_height = self.HEIGHT - self.MARGINS["up"] - self.MARGINS["down"]
            for function in self.diagram.functions.values():
                floor = function.floor
                if function.fixed == False:
                    function.position[0] = (
                        self.MARGINS["base"]
                        + (floor + 0.5) * interval_width
                        + offset
                        - function.dimension[0] // 2
                    )
                    rank = tl.function_rank(function, self.diagram.floors[floor])
                    ratio = (rank + 1) / (len(self.diagram.floors[floor]) + 1)
                    function.position[1] = (
                        round(free_height * ratio)
                        + self.MARGINS["up"]
                        - function.dimension[1] // 2
                    )
            # Position the nodes linked to the functions
            self.position_functions_nodes()

            # Calculate the position of free nodes based on the positions of related non-free nodes.
            for node in self.diagram.nodes.values():
                if node.free and not node.fixed:
                    max_abscissas = self.WIDTH - self.MARGINS["base"] - offset // 2
                    min_abscissas = self.MARGINS["base"] + offset // 2
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
                        node.position[1] = self.MARGINS["up"] + free_height // 2
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
            print("Error during drawing.")


    def draw_nodes(self):
        """Draw discs for isolated points and arrows for points linked to blocks."""
        police = self.preferences["police"]
        text_size = int(self.preferences["text size_int"])
        font_texte = tkfont.Font(family=police, size=text_size, weight="normal")
        sep_lenght = tkfont.Font(
            size=text_size, family=police, weight="normal"
        ).measure(": ")
        color = self.preferences["line color_color"]
        text_color = self.preferences["text color_color"]
        d = int(self.preferences["text size_int"]) * self.zoom // 2
        for node in self.diagram.nodes.values():
            if node.position != [None, None] and node.visible:
                x, y = node.position
                x, y = tl.offset(self.ref_origin, self.zoom, x, y)
                if node.free:
                    justify = node.justify
                    if justify is None:
                        justify = self.preferences["justify_choice"]
                    self.can.create_oval(x - d, y - d, x + d, y + d, fill=color)
                    self.print_label(
                        x,
                        y - self.margins["base"],
                        node.label,
                        node.annotation,
                        "sw",
                        justify,
                    )
                else:  # Entry of a function
                    self.draw_triangle(x, y, 0)
                    if ">" in node.name:
                        self.print_label(
                            x + (self.margins["base"]) // 2 - sep_lenght,
                            y - self.margins["base"],
                            node.label,
                            node.annotation,
                            "w",
                        )
                    else:  # Entry of a function
                        self.print_label(x + 2, y, node.label, node.annotation, "w")

    def draw_triangle(self, x, y, orientation=0, color=None, d=None):
        """Draw an isosceles triangle. Origin = H, intersection of the main height and the base.
        Orientation: 0 = East, 1 = South, 2 = West, 3 = North
        """
        if color is None:
            color = self.preferences["line color_color"]
        if d is None:
            d = int(self.preferences["text size_int"])*self.zoom // 2
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
        text_size = int(text_size * self.zoom)
        font = tkfont.Font(family=police, size=text_size, weight="normal")
        text_color = self.preferences["text color_color"]
        if color is not None:
            text_color = color
        type_color = self.preferences["type color_color"]
        texts = {"name": label, "separator": label, "space": label, "real": label}
        if len(annotation) != 0:
            texts["separator"] = label + ":"
            texts["space"] = label + ": "
            texts["real"] = label + ": " + annotation
        # Calculate in pixels the lengths of the different texts
        lenghts = dict()
        for key, text in texts.items():
            lenghts[key] = (
                tkfont.Font(size=text_size, family=police, weight="normal").measure(
                    text
                )
            )
        # Calculate the offset of the text according to the justification
        # If justify is not None, its value is "left", "center","separator" or "right"
        justify_offset = {
            None: 0,
            "left": 0,
            "right": lenghts["real"] * self.zoom,
            "center": lenghts["real"] * self.zoom // 2,
            "separator": lenghts["separator"] * self.zoom,
        }
        if justify in justify_offset.keys():
            x -= justify_offset[justify]
        # Display the label
        if len(annotation) > 0 and len(label) > 0:
            label += ": "
        self.can.create_text(
            x, y, text=label, font=font, anchor=anchor, fill=text_color
        )
        if len(annotation) > 0:
            x_type = x + lenghts["space"]
            self.can.create_text(
                x_type, y, text=annotation, font=font, anchor=anchor, fill=type_color
            )

    def draw_functions(self):
        """Draw the function_block: Header, body frames.
        Update the positions of the points in the block: Inputs and outputs
        """
        title_char_height = self.title_char_height * self.zoom
        police = self.preferences["police"]
        title_size = int(self.preferences["title size_int"])
        title_size = int(title_size * self.zoom)
        text_size = int(self.preferences["text size_int"])
        text_size = int(text_size * self.zoom)
        text_color = self.preferences["text color_color"]
        thickness = int(self.preferences["border thickness_int"])
        thickness = thickness * self.zoom
        font_title = tkfont.Font(family=police, size=title_size, weight="bold")
        font_texte = tkfont.Font(family=police, size=text_size, weight="normal")
        border_color = self.preferences["border default color_color"]
        title_background_color = self.preferences["title background color_color"]
        function_background_color = self.preferences["function background color_color"]
        rounded = True if self.preferences["rounded functions_bool"] == 1 else False
        for function in self.diagram.functions.values():
            # Drawing of the body frame
            if function.position is not None:
                x, y = function.position
                x, y = tl.offset(self.ref_origin, self.zoom, x, y)
                function_width, function_height = function.dimension
                function_width *= self.zoom
                function_height *= self.zoom
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
                    y + title_char_height,
                    outline=border_color,
                    fill=header_color,
                    thickness=thickness,
                    rounded_up=rounded,
                )

                # Drawing of the body of the function
                tl.draw_box(
                    self.can,
                    x,
                    y + title_char_height,
                    x + function_width,
                    y + title_char_height + function_height,
                    outline=border_color,
                    fill=function_background_color,
                    thickness=thickness,
                    rounded_down=rounded,
                    radius=self.title_char_height // 2,
                )

                # Writing the function name
                x_titre = x + function_width // 2
                y_titre = y + title_char_height // 2
                texte = function.label
                self.can.create_text(
                    x_titre,
                    y_titre,
                    text=texte,
                    font=font_title,
                    anchor="center",
                    fill=text_color,
                )

    def draw_lines(self):
        """Draw the connections between the points: Vertical or horizontal lines."""
        thickness = int(self.preferences["line thickness_int"])
        thickness = thickness * self.zoom
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
            x_start, y_start = tl.offset(self.ref_origin, self.zoom, x_start, y_start)
            x_first, y_first  = tl.offset(self.ref_origin, self.zoom, x_first, y_first )
            x_middle, y_middle = tl.offset(self.ref_origin, self.zoom, x_middle, y_middle)
            x_last, y_last = tl.offset(self.ref_origin, self.zoom, x_last, y_last)
            x_end, y_end = tl.offset(self.ref_origin, self.zoom, x_end, y_end)
            if smooth:
                self.can.create_line(
                    (x_start, y_start),
                    (x_first, y_start),
                    (x_middle, y_middle),
                    (x_last, y_end),
                    (x_end, y_end),
                    fill=color,
                    width=thickness,
                    smooth="true",
                )
            else:
                self.can.create_line(
                    (x_start, y_start), (x_middle, y_start), fill=color, width=thickness
                )
                self.can.create_line(
                    (x_middle, y_start), (x_middle, y_end), fill=color, width=thickness
                )
                self.can.create_line(
                    (x_middle, y_end), (x_end, y_end), fill=color, width=thickness
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
            if group.position is not None:
                x_origin, y_origin = group.position
                x_origin, y_origin = tl.offset(self.ref_origin, self.zoom, x_origin, y_origin)
                width, height = group.dimension
                width *= self.zoom
                height *= self.zoom
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
        title_char_height = self.title_char_height * self.zoom
        if self.destination is None:
            return None
        x, y = self.destination.position
        x, y = tl.offset(self.ref_origin, self.zoom, x, y)
        if type(self.destination) == Link:
            d = 2 * int(self.preferences["text size_int"]) // 3
            self.can.create_rectangle(
                x - 2, y - 2, x + 2, y + 2, width=2, outline=color
            )
        elif type(self.destination) == Node:
            d = 2 * int(self.preferences["text size_int"]) // 3
            if self.destination.free:
                self.can.create_oval(x - d, y - d, x + d, y + d, fill=color)
            else:
                scale = int(self.preferences["text size_int"]) // 3
                self.draw_triangle(x - scale // 2, y, 0, color, scale)

        elif type(self.destination) == group.Corner_group:
            d = 2 * int(self.preferences["text size_int"]) // 3
            self.can.create_rectangle(x - d, y - d, x + d, y + d, fill=color)

        elif type(self.destination) == Function_block:
            width, height = self.destination.dimension
            width *= self.zoom
            height = height * self.zoom
            self.can.create_rectangle(
                x - 2,
                y - 2,
                x + width + 2,
                y + title_char_height + height + 2,
                width=2,
                outline=color,
            )
        elif type(self.destination) == Group:
            width, height = self.destination.dimension
            width *= self.zoom
            height *= self.zoom
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
            print("Error during window positioning.")

    @Decorators.disable_if_editing
    def cmd_new(self):
        """Clear the list of points and functions."""
        message("New diagram.", self.text_message)
        self.state = 1
        self.diagram = Diagram()
        self.draw()
        self.tk.title("Functions Diagram")
        self.active_file = None

    @Decorators.disable_if_editing
    def cmd_open(self):
        """Open the selected JSON file and rebuilds the system instance.
        Allow to choose the JSON format or the TXT
        Return True if the procedure succeeds otherwise False
        """
        self.can.config(cursor="arrow")
        message("Open file.", self.text_message)
        self.state = 1
        if self.active_file is not None:
            selected_file = fd.askopenfilename(
                title="Open", initialdir=path.split(self.active_file)[0]
            )
        else:
            selected_file = fd.askopenfilename(title="Open")
        self.active_file = selected_file
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
        self.tk.title("Functions Diagram" + " - " + file_name)
        self.memory.add(self.diagram.export_to_text())
        return True

    @Decorators.disable_if_editing
    def cmd_save(self):
        """Save the configuration of the diagram as a file."""
        self.can.config(cursor="arrow")
        message("Save diagram.", self.text_message)
        self.state = 1
        if self.active_file is not None:
            selected_file = fd.asksaveasfile(
                title="Save", initialdir=path.split(self.active_file)[0]
            )
        else:
            selected_file = fd.asksaveasfile(title="Save")
        diagram_datas = self.diagram.export_to_text()
        try:
            selected_file.write(diagram_datas)
            self.active_file = selected_file.name
            message("Diagram saved.", self.text_message)
            selected_file.close()
            file_name = selected_file.name
            file_name = path.split(file_name)[1]
            self.tk.title("Functions Diagram" + " - " + file_name)
            return True
        except:
            message("Backup canceled.", self.text_message)
            return False

    @Decorators.disable_if_editing
    def cmd_add_function(self):
        """Add a nex function block."""
        if self.edition_in_progress == False:
            message("Create a new function.", self.text_message)
            previous_names = tl.all_previous_names(self.diagram)
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
            previous_names = tl.all_previous_names(self.diagram)
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
                print("Error during window positioning.")
    
    def group_all(self, event):
        """ Create a group with all the elements : Functions and nodes
        """
        if self.state == 1:
            mouse_x, mouse_y = tl.pointer_position(self.can)
            origin = [mouse_x, mouse_y]
            previous_names = tl.all_previous_names(self.diagram)
            name = tl.new_label(previous_names)
            new_group = Group(
                name=name,
                label=name,
                fixed=False,
                position=origin,
                dimension=[100, 100],
            )
            elements = new_group.search_elements_in(
                self.diagram, origin, self.destination, True
            )
            new_group.elements = elements
            ok = new_group.update_coordinates()
            print("Update ?", ok)
            self.diagram.add_group(new_group)
            self.destination = new_group
            self.edit(self.destination)
            self.draw()


    def copy(self, event=None):
        if self.destination != None:
            text = "Element copied : " + self.destination.name
            message(text, self.text_message)
            self.state = 3
            new_name = self.destination.name
            if "*" not in new_name:
                new_name += "*"
            new_name = tl.new_label(tl.all_previous_names(self.diagram), new_name)
            if isinstance(self.destination, Node):
                self.destination = self.diagram.copy_node(self.destination, new_name)
            elif isinstance(self.destination, Function_block):
                self.destination = self.diagram.copy_function(
                    self.destination, new_name
                )
            elif isinstance(self.destination, Group):
                self.destination = self.diagram.copy_group(self.destination, new_name)
        else:
            message("No element selected to copy.", self.text_message)

    @Decorators.disable_if_editing
    def cmd_move(self):
        """Allow objects to move."""
        message(
            "Select the free node, the function or the group to move.",
            self.text_message,
        )
        self.can.config(cursor="fleur")
        self.state = 2

    @Decorators.disable_if_editing
    def cmd_edit(self):
        """Initiate the editing of the selected object."""
        if len(self.diagram.nodes) > 0 or len(self.diagram.functions) > 0:
            message(
                "Select the free node, the function or the group to to edit.",
                self.text_message,
            )
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
        message(
            "Select the free node, the function or the group to to erase.",
            self.text_message,
        )
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
        elif type(destination) == Group:
            group_to_delete = tl.key_of(self.diagram.groups, destination)
            self.diagram.delete_group(group_to_delete)

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

    def undo(self, event=None):
        # Undo from keyboard Ctrl+z
        self.cmd_undo()
    
    def redo(self, event=None):
        # Redo from keyboard Ctrl+y
        self.cmd_redo()

    def zoom_wheel(self, event):
        # Respond to Linux(event.delta) or Windows(event.num) wheel event
        if event.num == 4 or event.delta == 120:
            self.zoom_more()
        elif event.num == 5 or event.delta == -120:
            self.zoom_less()

    def zoom_more(self, event=None):
        """Zoom in"""
        if self.zoom_index < len(self.zooms) - 1:
            self.zoom_index += 1
        self.zoom_update()

    def zoom_less(self, event=None):
        """Zoom out"""
        if self.zoom_index > 0:
            self.zoom_index -= 1
        self.zoom_update()

    def zoom_update(self):
        """ Update the zoom parameter and the margins  in line with changes in the self.zoom_index.
        """
        self.zoom = self.zooms[self.zoom_index]
        message("Zoom: " + str(self.zoom) + "%", self.text_message)
        self.margins = tl.update_dict_ratio(self.MARGINS, self.zoom)  # Margin modified by zoom
        self.draw()

    def reset_origin(self, event):
        """ Original offset and zoom parameter
        """
        self.state = 1
        message("Origin reset.", self.text_message)
        self.ref_origin = [0, 0]
        self.zoom_index = 9
        self.zoom = self.zooms[self.zoom_index]
        self.margins = tl.update_dict_ratio(self.MARGINS, self.zoom)  # Margin modified by zoom
        self.draw()

    def drag_origin(self, event):
        """Initiate the drag of the diagram."""
        TTL = 4  # Time to live of the drag
        if self.state == 1:
            x, y = tl.pointer_position(self.can)
            if self.tempo_drag == 0:
                self.ref_delta_drag = [x, y]
                self.tempo_drag = TTL
                return None
            self.tempo_drag = TTL
            x_old, y_old = self.ref_delta_drag
            delta_x, delta_y = (x - x_old)//self.zoom, (y - y_old)//self.zoom
            self.ref_origin[0] += delta_x
            self.ref_origin[1] += delta_y
            self.ref_delta_drag = [x, y]
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
        #Xpix, Ypix = tl.subset(self.ref_origin, self.zoom, Xpix, Ypix)
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
            self.origin = tl.subset(self.ref_origin, self.zoom, *self.origin)
            self.destination = tl.subset(self.ref_origin, self.zoom, *self.destination)
            dimension = tl.get_dimension(self.origin, self.destination)
            elements = list()
            empty_zone = True
            previous_names = tl.all_previous_names(self.diagram)
            name = tl.new_label(previous_names)
            new_group = Group(
                name=name,
                label=name,
                elements=elements,
                fixed=empty_zone,
                position=self.origin,
                dimension=dimension,
            )
            elements = new_group.search_elements_in(
                self.diagram, self.origin, self.destination
            )
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

    def fermer_fenêtre(self):
        self.tk.quit()
        self.tk.destroy()

    def engine(self):
        """ State management :
        1 - Basic state
        2 - Move object : Select the origin
        3 - Move object : Select destination
        4 - Erase : Select object to erase
        5 - Edit : Select object to edit
        6 - Add link : Select the origin
        7 - Add link : Select destination
        8 - Add group : Selecting the first corner
        9 - Add group : Selecting the second corner
        """
        if self.tempo_drag > 0:
            self.tempo_drag -= 1
        else:
            self.tempo_drag = 0
        if self.state == 1:  # Basic state
            self.can.config(cursor="arrow")
        if self.state == 2:  # Move object: Select the origin
            mouse_x, mouse_y = tl.pointer_position(self.can)
            mouse_x, mouse_y = tl.subset(self.ref_origin, self.zoom, mouse_x, mouse_y)
            self.destination = tl.nearest_objet((mouse_x, mouse_y), self.diagram, self.zoom)
            self.draw()
            self.draw_destination_outine()
        elif self.state == 3 and self.destination is not None:  # Move to destination
            mouse_x, mouse_y = tl.pointer_position(self.can)
            mouse_x, mouse_y = tl.subset(self.ref_origin, self.zoom, mouse_x, mouse_y)
            self.destination.position = [mouse_x, mouse_y]
            # Move the elements of the group
            if type(self.destination) == Group:
                if self.destination.fixed == False:
                    other_groups = [
                        group
                        for group in self.diagram.groups.values()
                        if group != self.destination
                    ]
                    for element in self.destination.elements:
                        x_relative, y_relative = element["position"]
                        element["element"].position = [
                            mouse_x + x_relative,
                            mouse_y + y_relative,
                        ]

                    for group in other_groups:
                        for object in self.destination.elements:
                            group.follow(object["element"])
            elif type(self.destination) == grp.Corner_group:
                x_corner, y_corner = self.destination.position
                x_parent, y_parent = self.destination.parent_group.position
                self.destination.parent_group.dimension = [
                    x_corner - x_parent,
                    y_corner - y_parent,
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
            mouse_x, mouse_y = tl.subset(self.ref_origin, self.zoom, mouse_x, mouse_y)
            self.destination = tl.nearest_objet(
                (mouse_x, mouse_y), self.diagram, self.zoom, target_types="erasable"
            )
            self.draw()
            self.draw_destination_outine("red")
        elif self.state == 5:  # Select object to edit
            mouse_x, mouse_y = tl.pointer_position(self.can)
            mouse_x, mouse_y = tl.subset(self.ref_origin, self.zoom, mouse_x, mouse_y)
            self.destination = tl.nearest_objet((mouse_x, mouse_y), self.diagram, self.zoom)
            self.draw()
            self.draw_destination_outine("green")
        elif self.state == 6:  # Add link : Origin selected
            mouse_x, mouse_y = tl.pointer_position(self.can)
            mouse_x, mouse_y = tl.subset(self.ref_origin, self.zoom, mouse_x, mouse_y)
            self.destination, distance = tl.nearest(
                (mouse_x, mouse_y), self.diagram.nodes.values()
            )
            self.draw()
            self.draw_destination_outine()
        elif (
            self.state == 7 and self.origin is not None
        ):  # Add link : Destination selected
            mouse_x, mouse_y = tl.pointer_position(self.can)
            mouse_x, mouse_y = tl.subset(self.ref_origin, self.zoom, mouse_x, mouse_y)
            self.destination, distance = tl.nearest(
                (mouse_x, mouse_y), self.diagram.nodes.values()
            )
            self.draw()
            self.draw_destination_outine()
        elif self.state == 9:  # Add group : Selecting the second corner
            mouse_x, mouse_y = tl.pointer_position(self.can)
            #mouse_x, mouse_y = tl.subset(self.ref_origin, self.zoom, mouse_x, mouse_y)
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
