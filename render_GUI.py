from PIL import Image, ImageTk
from math import pi, cos, sin
from os import path
from tkinter import font as tkfont
import tkinter as tki
import tools as tl
import group as grp
from diagram import *
from node import *
from files import *

COLOR_OUTLINE = "#FFFF00"


class Window:
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
        self.zooms = [i / 100 for i in range(10, 310, 10)]
        self.zoom_index = 9
        self.zoom = self.zooms[self.zoom_index]
        self.MARGINS = {"base": 10, "up": 10, "down": 10}
        self.margins = tl.update_dict_ratio(
            self.MARGINS, self.zoom
        )  # Margin modified by zoom
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.screen_dimensions()
        self.MENU_HEIGHT = 80
        self.smooth_lines = True
        self.can = tki.Canvas(
            self.tk,
            width=self.SCREEN_WIDTH,
            height=self.SCREEN_HEIGHT,
            bg=self.preferences["main background color_color"],
        )
        self.can.pack()
        self.tk.update()
        self.WIDTH, self.HEIGHT = self.canvas_dimensions()
        self.destination = None  # Element of the selection
        self.origin = None  # First element of the selection
        self.ref_origin = [0, 0]  # Reference frame origin
        self.ref_delta_drag = [0, 0]  # Reference offset during movement
        self.tempo_drag = 0  # >0 during drag movement.
        self.auto_resize_blocks()
        self.update_positions()
        self.edition_in_progress = False
        self.stop_engine = False
        self.after_id = None

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
            return False

    def draw(self):
        """Update the system display in the Tkinter window"""
        if True:
            # Delete all objects from the canvas before recreating them
            self.can.delete("all")
            self.can.configure(bg=self.preferences["main background color_color"])
            # Draw all the elements of the system
            self.draw_functions()
            self.draw_nodes()
            self.draw_lines()
            self.draw_groups()
        """
        except:
            print("Error during drawing.")"""

    def draw_nodes(self):
        """Draw discs for isolated points and arrows for points linked to blocks."""
        police = self.preferences["police"]
        text_size = int(self.preferences["text size_int"])
        font_texte = tkfont.Font(family=police, size=text_size, weight="normal")
        sep_lenght = (
            tkfont.Font(size=text_size, family=police, weight="normal").measure(": ")
            * self.zoom
        )
        color = self.preferences["line color_color"]
        text_color = self.preferences["text color_color"]
        type_color = self.preferences["type color_color"]
        comment_color = self.preferences["comment color_color"]
        comment_border_color = tl.darker(comment_color, 0.7)
        d = int(self.preferences["text size_int"]) * self.zoom // 2
        for node in self.diagram.nodes.values():
            if node.position != [None, None] and node.visible:
                x, y = node.position
                x, y = tl.offset(self.ref_origin, self.zoom, x, y)
                if node.free:
                    justify = node.justify
                    if justify is None or justify == "None":
                        justify = self.preferences["justify_choice"]
                    if justify == "separator":
                        comment_justify = "center"
                    else:
                        comment_justify = justify
                    self.can.create_oval(x - d, y - d, x + d, y + d, fill=color)
                    self.print_label(
                        x,
                        y - self.margins["base"],
                        node.label,
                        node.annotation,
                        "sw",
                        justify,
                    )
                    # Display comments (example of values)
                    if node.comment != "":
                        # Display the comment on multiple lines
                        # Replace the character string "\n" with the character chr(10)
                        node.comment = node.comment.replace(chr(10), "\\n")
                        comment_lines = node.comment.split("\\n")
                        comment_height = (
                            len(comment_lines) * self.text_char_height * self.zoom
                        )
                        # Calculate the maximum width of the comment area
                        comment_max = ""
                        for comment_line in comment_lines:
                            if len(comment_line) > len(comment_max):
                                comment_max = comment_line
                        text_size = int(self.preferences["text size_int"])
                        text_size = int(text_size * self.zoom)
                        font = tkfont.Font(
                            family=police, size=text_size, weight="normal"
                        )
                        comment_width = tkfont.Font(
                            size=text_size, family=police, weight="normal"
                        ).measure(comment_max)
                        # Calculate the maximum width of the comment area
                        comment_offset = {
                            "left": 0,
                            "right": comment_width,
                            "center": comment_width // 2,
                        }
                        x_comment = x - comment_offset[comment_justify]
                        y_ref = (
                            y
                            - self.margins["base"] // 2
                            + self.text_char_height * self.zoom
                        )
                        # Display the lines of the comment
                        for n_line in range(len(comment_lines)):
                            y_comment = (
                                y_ref + self.text_char_height * n_line * self.zoom
                            )
                            comment = comment_lines[n_line]
                            self.can.create_text(
                                x_comment,
                                y_comment,
                                text=comment,
                                font=font,
                                anchor="nw",
                                fill=comment_color,
                            )
                        margin = self.margins["base"] // 2
                        dash = tl.byte_homotety(2, self.zoom)
                        # Display the dashed border of the comment area
                        self.can.create_rectangle(
                            x_comment - margin,
                            y_ref - margin,
                            x_comment + comment_width + margin,
                            y_ref + comment_height + margin,
                            outline=comment_border_color,
                            width=max(1, dash // 2),
                            dash=(dash, dash * 2),
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
            d = int(self.preferences["text size_int"]) * self.zoom // 2
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
            lenghts[key] = tkfont.Font(
                size=text_size, family=police, weight="normal"
            ).measure(text)
        # Calculate the offset of the text according to the justification
        # If justify is not None, its value is "left", "center","separator" or "right"
        justify_offset = {
            None: 0,
            "left": 0,
            "right": lenghts["real"],
            "center": lenghts["real"] // 2,
            "separator": lenghts["separator"],
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
            x_first, y_first = tl.offset(self.ref_origin, self.zoom, x_first, y_first)
            x_middle, y_middle = tl.offset(
                self.ref_origin, self.zoom, x_middle, y_middle
            )
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
            dash = tl.byte_homotety(int(thickness), self.zoom)
            if group.position is not None:
                x_origin, y_origin = group.position
                x_origin, y_origin = tl.offset(
                    self.ref_origin, self.zoom, x_origin, y_origin
                )
                width, height = group.dimension
                width *= self.zoom
                height *= self.zoom
                x_end, y_end = x_origin + width, y_origin + height
                self.can.create_rectangle(
                    x_origin,
                    y_origin,
                    x_end,
                    y_end,
                    dash=(2 * dash, 2 * dash),
                    fill="",
                    outline=color,
                    width=dash,
                )
                self.print_label(
                    x_origin,
                    y_origin - self.text_char_height * self.zoom,
                    group.label,
                    color=color,
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
            else:
                self.update_positions()

        self.draw()

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
        """Update the zoom parameter and the margins  in line with changes in the self.zoom_index."""
        self.zoom = self.zooms[self.zoom_index]
        self.margins = tl.update_dict_ratio(
            self.MARGINS, self.zoom
        )  # Margin modified by zoom
        self.draw()

    def reset_origin(self, event):
        """Original offset and zoom parameter"""
        self.state = 1
        self.ref_origin = [0, 0]
        self.zoom_index = 9
        self.zoom = self.zooms[self.zoom_index]
        self.margins = tl.update_dict_ratio(
            self.MARGINS, self.zoom
        )  # Margin modified by zoom
        self.draw()

    def quit(self):
        self.stop_engine = True
        if self.after_id is not None:
            self.tk.after_cancel(self.after_id)
        self.tk.quit()
        self.tk.destroy()
