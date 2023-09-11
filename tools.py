import matplotlib.colors as mcolors
from math import sqrt
from tkinter import font as tkfont
import tkinter as tki
from math import cos, sin, pi
import json
import diagram as dia
from node import Node
from link import Link
from function_block import Function_block
import group as grp  # To avoid circular import


def index_occurrence(char, string):
    """Return the list of indexes of occurrences of char in the string."""
    return [i for i, j in enumerate(string) if j == char]


def function_rank(function, function_list):
    """Return the index of occurrence of the function in the function_list."""
    rank = 0
    while rank < len(function_list):
        if function is function_list[rank]:
            return rank
        rank += 1
    return 0


def parameters_in(line):
    """Return the list of strings in line separated by commas except those enclosed in parentheses.
    Example :
    >>> parameters_in("param1, param2, (2,4), param3, (5, 7)")
    (["param1", "param2", "(2,4)", "param3", "(5, 7)"]
    """
    parameters = []
    parameter = ""
    parenthesis = 0
    for char in line:
        if parenthesis == 0 and char == ",":
            parameters.append(parameter)
            parameter = ""
        elif char == "(":
            parenthesis += 1
        elif char == ")":
            parenthesis -= 1
        else:
            parameter += char
    parameters.append(parameter)
    return parameters


def coordinates(parameters):
    """If parameters is a pair of integer-castable strings, then return the list of matching integers.
    Otherwise returns None.
    >>> coordinates("(12, 43)")
    [12,43]
    >>> coordinates("12, 43")
    [12,43]
    """
    parameters = parameters.replace(" ", "")
    if parameters[0] == "(" and parameters[-1] == ")":
        parameters = parameters[1:-1]
    pos_comma = index_occurrence(",", parameters)
    if len(pos_comma) == 1:
        x_str, y_str = parameters.split(",")
        if x_str.isdigit() and y_str.isdigit():
            x, y = int(x_str), int(y_str)
            return [x, y]
    return None


def character_dimensions(police, size):
    """Return the (width, height) of a character of a mono-spaced font."""
    nb_pixels_height = tkfont.Font(size=size, family=police).metrics("linespace")
    nb_pixels_width = tkfont.Font(size=size, family=police).measure("X")
    return (nb_pixels_width, nb_pixels_height)


def key_of(dictionary, value):
    """Return the first dictionary key that matches the searched value. Otherwise, return None."""
    for k, v in dictionary.items():
        if v == value:
            return k
    return None


def create_definition_description(function):
    """Create the string description of a function.
    Example : "def my_function(a:int, b:float)->float"
    """
    description = "def " + function.name + "("
    one_entry_or_more = False
    for entry in function.entries:
        one_entry_or_more = True
        description += entry.label
        if entry.annotation != "":
            description += ":" + entry.annotation
        description += ","
    if one_entry_or_more:
        description = description[:-1]
    description += ")"
    if function.output is not None:
        if function.output.visible == False or function.output.annotation != "":
            description += "->"
        if function.output.visible == False:
            description += "*"
        if function.output.annotation != "":
            description += function.output.annotation
    if function.header_color is not None:
        description += '  # header_color = "' + function.header_color + '"'
    description += "\n"
    # Add the position
    description += function.name + ".position("
    description += str(int(function.position[0])) + ","
    description += str(int(function.position[1])) + ")\n"
    # Add the dimension
    if function.dimension != []:
        description += function.name + ".dimension("
        description += str(int(function.dimension[0])) + ","
        description += str(int(function.dimension[1])) + ")\n"
    return description


def create_node_description(node):
    """Create the string description of a free node (not in a function).
    Example for the A node at position (800, 200): "node (A:str,(800,200))"
    """
    if node.position is None:
        return ""
    if len(node.position) < 2:
        return ""
    elif node.position[0] is None and node.position[1] is None:
        return ""
    elif node.free:
        description = "node" + "(" + node.name
        if node.annotation != "":
            description += ":" + node.annotation
        # Add the position
        if node.position != [0, 0]:
            description += ",("
            description += str(int(node.position[0])) + ","
            description += str(int(node.position[1])) + ")"
        if node.justify is not None:
            if node.justify in ["left", "right", "center", "separator"]:
                description += ',justify="' + node.justify + '"'
        description += ")"
        if node.fixed:
            description += "  # fixed"
        description += "\n"
        return description
    else:
        return ""


def create_group_description(group):
    """Create the string description of a group.
    Example with group g1 of position (150, 200) and dimensions (250, 250) containing functions f1, f1* and nodes n1, n2 and n3. Margin 20 pixels. Auto mode.

    group g1(margin=20, mode="Auto", color="#a0a000", thickness=2)
    g1.add_functions(f1, f1*)
    g1.add_nodes(n1, n2, n3)
    g1.position(150, 200)
    g1.dimension(250, 250)
    """
    description = "group " + group.name + "("
    description += "margin=" + str(group.margin) + ", "
    if group.fixed:
        description += 'mode="Fixed", '
    else:
        description += 'mode="Auto", '
    description += 'color="' + group.color + '", '
    description += "thickness=" + str(group.thickness)
    description += ")\n"
    associated_functions = []
    associated_nodes = []
    for element in group.elements:
        if element["type"] == "Function_block":
            associated_functions.append(element["element"])
        if element["type"] == "Node":
            associated_nodes.append(element["element"])
    if len(associated_functions) > 0:
        description += group.name + ".add_function("
        for function in associated_functions:
            description += function.name + ","
        description = description[:-1] + ")\n"
    if len(associated_nodes) > 0:
        description += group.name + ".add_node("
        for node in associated_nodes:
            description += node.name + ","
        description = description[:-1] + ")\n"
    if group.position != [None, None]:
        description += group.name + ".position("
        description += str(int(group.position[0])) + ","
        description += str(int(group.position[1])) + ")\n"
    if group.dimension != []:
        description += group.name + ".dimension("
        description += str(int(group.dimension[0])) + ","
        description += str(int(group.dimension[1])) + ")\n"
    return description


def reverse(link_description):
    """Create the symmetric expression of the link between two nodes.
    Example for "A---B" : "B---A"
    """
    nodes = link_description.split("---")
    if len(nodes) == 2:
        return nodes[1] + "---" + nodes[0]


def distance(origin_position, target_position):
    if origin_position is None or target_position is None:
        return None
    x1, y1 = origin_position
    x2, y2 = target_position
    if x1 is None or y1 is None or x2 is None or y2 is None:
        return None
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def nearest(mouse_position, targets):
    """Return the nearest object, and the distance, from the mouse_position."""
    nearest_target = None
    nearest_target_distance = None
    for target in targets:
        compliant_target = False
        if type(target) == Function_block and target.position is not None:
            compliant_target = True
            position_x = target.position[0] + target.dimension[0] // 2
            position_y = target.position[1] + target.dimension[1] // 2
            position = (position_x, position_y)
        elif type(target) in [Node, Link, grp.Group, grp.Corner_group]:
            compliant_target = True
            position = target.position
        if compliant_target:  # target is a free node or a function
            dist = distance(mouse_position, position)
            if dist is None:
                pass
            elif nearest_target_distance is None:
                nearest_target = target
                nearest_target_distance = dist
            elif dist < nearest_target_distance:
                nearest_target = target
                nearest_target_distance = dist
    return nearest_target, nearest_target_distance


def nearest_objet(mouse_position, diagram, zoom=1, target_types="movable"):
    """Return the nearest object from the cursor.
    target_types can be "all" (default), "function" or "node"
    """
    population = []
    population += diagram.groups.values()
    for group in diagram.groups.values():
        if group.fixed:
            new_corner = grp.Corner_group(group)
            population += [new_corner]
    if target_types != "node":
        population += diagram.functions.values()
    if target_types != "function":
        population += [node for node in diagram.nodes.values() if node.free]
    if target_types == "erasable":
        population += diagram.links
    nearest_target, nearest_target_distance = nearest(mouse_position, population)
    return nearest_target


def pointer_position(window):
    """Return the pointer position relative to the origin of the main canvas."""
    mouse_x = window.winfo_pointerx() - window.winfo_rootx()
    mouse_y = window.winfo_pointery() - window.winfo_rooty()
    return mouse_x, mouse_y


def get_dimension(origin, destination):
    """Return the tuple (x,y) where x is the difference between the abscissa of the origin and the destination and y is the difference between the ordinate of the origin and the destination."""
    x = destination[0] - origin[0]
    y = destination[1] - origin[1]
    return (x, y)

def offset(origin, zoom, x, y):
    """ origin is a list [x_offset, y_offset].
        Return the list modified by thr zoom factor and the offset (origin).
    """
    return [(origin[0])+zoom*x, (origin[1])+zoom*y]

def subset(origin, zoom, x, y):
    """ origin is a list [x_offset, y_offset].
        Take the x,y position of the mouse. Translate it by the offset (origin) and divide it by the zoom factor.
        Return the corresponding position.
    """
    return [(x-origin[0])//zoom , (y-origin[1])//zoom]

def update_dict_ratio(dico:dict, zoom:float):
    """ Retrun the dico with all values multiplied by zoom.
    """
    new_dico = dict()
    for key, value in dico.items():
        new_dico[key] = value * zoom
    return new_dico

def search_in_rectangle(diagram, origin, destination):
    """Return the list of functions and nodes in the rectangle defined by the positions origin (x1, y1) and destination (x2, y2)."""
    objects = []
    x1, y1 = origin
    x2, y2 = destination
    for function in diagram.functions.values():
        x, y = function.position
        if x1 <= x <= x2 and y1 <= y <= y2:
            objects.append(function)
    for node in diagram.nodes.values():
        if node.free:
            x, y = node.position
            if x1 <= x <= x2 and y1 <= y <= y2:
                objects.append(node)
    return objects


def all_previous_names(diagram):
    """Return the list of all names of functions, nodes and groups in the diagram."""
    names = []
    for function in diagram.functions.values():
        names.append(function.name)
    for node in diagram.nodes.values():
        names.append(node.name)
    for group in diagram.groups.values():
        names.append(group.name)
    return names


def new_label(previous_labels, label=None):
    """Return the next_label who's not in previous label.
    label (optional) is the current label.
    """
    if label is None:
        label = "a"
    while label in previous_labels:
        label = next_label(label)
    return label


def next_label(previous_label):
    """Increment the last character of the previous_label string."""
    alphabet = [chr(i) for i in range(97, 123, 1)]
    parts = previous_label.split("*")
    substring = parts[-1]  # Part of the string to increment
    if substring == "" and len(parts) == 0:
        return "a"
    elif substring == "" and len(parts) > 0:
        return parts[0] + "*a"
    # Increment the last character of the substring
    last_char = substring[-1]
    if last_char not in alphabet:
        last_char = "a"
    last_char = chr(ord(last_char) + 1)
    substring = substring[:-1] + last_char
    for i in range(len(substring) - 1, 0, -1):
        if ord(substring[i]) >= 123:
            substring = change_str(substring, i, "a")
            carry = chr(ord(substring[i - 1]) + 1)
            substring = change_str(substring, i - 1, carry)
    if ord(substring[0]) >= 123:
        substring = change_str(substring, len(substring) - 1, "a")
        substring = "a" + substring
    if len(parts) == 1:
        return substring
    else:
        return parts[0] + "*" + substring


def change_str(string_source, index, char):
    """Return the string source with char at the index."""
    source = list(string_source)
    if index > len(source):
        return string_source
    source[index] = char
    return "".join(source)


def cast_to_float(value_str: str, shape=None) -> float:
    """Take a value (str) in parameter.
    if value is castable to float, returns the float value.
    Otherwise, returns None.
    if shape is "unit" returns the float value only if it's between 0.0 and 1.0, .
    >>> cast_to_float("0.4")
    0.4
    >>> cast_to_float("4.2", "unit")
    None
    """
    if value_str == "":
        value_str = "0"
    good_format = True
    if len(index_occurrence(".", value_str)) < 2:
        for element in value_str:
            if element not in "0123456789.":
                good_format = False
    else:
        good_format = False
    if good_format:
        value = float(value_str)
        if shape is None:
            return value
        elif shape == "unit":
            if 0.0 <= value <= 1.0:
                return value
    return None


def cast_to_int(value_str: str, format=None) -> int:
    """Take a value (str) in parameter.
    if value is cast to integer, return the integer value.
    Otherwise, returns None.
    if format is "8bits" return the integer value only if it's between 0 and 255, .
    >>> cast_to_int("42")
    42
    """
    if value_str.isdigit():
        value_int = int(value_str)
        if format is None:
            return value_int
        elif format == "8bits":
            if 0 <= value_int <= 255:
                return value_int
    return None


def cast_to_color(color_str: str, col_format=None) -> str:
    """Take color_str in parameter : A specific name of mcolors.CSS4_COLORS key or a rgb format.
    Accept if col_format is "hex" and colors in hexadecimal digits.
    Return the good format to insert the color in the fill setting of the SVG file.
    Otherwise, return None.
    >>> cast_to_color("green")
    green
    >>> cast_to_color("(42,0,255)")
    rgb(42,0,255)
    >>> cast_to_color("42")
    None
    """
    if col_format is None and color_str[0] == "#":
        col_format = "hex"
    if col_format is None:
        if color_str == "":
            color_str = "white"
        if color_str in mcolors.CSS4_COLORS.keys():
            return color_str
        elif color_str[0] == "(" and color_str[-1] == ")":
            rgb = color_str[1:-1].replace(" ", "").split(",")
            if len(rgb) == 3:
                if (
                    test_compound(rgb[0])
                    and test_compound(rgb[1])
                    and test_compound(rgb[2])
                ):
                    return "rgb" + color_str
    elif col_format == "hex":
        if color_str[0] == "#":
            if len(color_str) == 7 or len(color_str) == 4:
                format_ok = True
                digits = color_str[1:]
                hex_digits = [chr(i) for i in range(48, 58)]
                hex_digits += [chr(i) for i in range(65, 71)]
                hex_digits += [chr(i) for i in range(97, 103)]
                for digit in digits:
                    if digit not in hex_digits:
                        format_ok = False
                if format_ok:
                    return color_str
    return None


def cast_rgb_to_hex_color(color_str):
    """If color_str is a color tuple, cast and return this color in an hexadecimal format.
    Otherwise, return the unmodified color string.
    """
    if color_str[0] == "(" and color_str[-1] == ")":
        rgb = color_str[1:-1].replace(" ", "").split(",")
        if len(rgb) == 3:
            if (
                test_compound(rgb[0])
                and test_compound(rgb[1])
                and test_compound(rgb[2])
            ):
                R, V, B = map(hex_digit, rgb)
                return "#" + R + V + B
    return color_str


def hex_digit(value_str):
    """value_str is a string castable to an int , 0 < value < 255
    Cast value in hex and return the two hexadecimal digits in a string format
    """
    if value_str.isdigit():
        value = int(value_str)
        return ("00" + str(hex(value)[2:]))[-2:]
    return "FF"


def test_compound(compound: str) -> bool:
    """Take a str in parameter.
    If compound is castable to int and lower than 256, return True.
    """
    if compound.isdigit():
        if 0 <= int(compound) < 256:
            return True
    return False


def draw_box(can, x_start, y_start, x_end, y_end, **kwargs):
    """Create a rectangle in the canvas (can).
    If rounded is True, create a rounded rectangle.
    """
    outline = "black"
    fill = "white"
    rounded_up = False
    rounded_down = False
    thickness = 1
    radius = 2  # bending_radius
    step = 20
    for k, v in kwargs.items():
        if k == "outline":
            outline = v
        elif k == "fill":
            fill = v
        elif k == "rounded_up":
            rounded_up = v
        elif k == "rounded_down":
            rounded_down = v
        elif k == "thickness":
            thickness = v
        elif k == "radius":
            radius = v
        elif k == "step":
            step = v
    if rounded_up == True:
        d = max(radius, (y_end - y_start) // 2)
        x1 = x_start + d
        x2 = x_end - d
        ym = y_start + d
        curve_left = []
        curve_right = []
        for i in range(step):
            a = pi + i * pi / (step * 2)
            curve_left.append(x1 + d * cos(a))
            curve_left.append(ym + d * sin(a))
            b = a + pi / 2
            curve_right.append(x2 + d * cos(b))
            curve_right.append(ym + d * sin(b))
        vertices = (
            [x_start, y_end, x_start, ym]
            + curve_left
            + [x1, y_start, x2, y_start]
            + curve_right
            + [x_end, ym, x_end, y_end]
        )
        can.create_polygon(vertices, outline=outline, fill=fill, width=thickness)
    elif rounded_down == True:
        d = max(radius, 2)
        x1 = x_start + d
        x2 = x_end - d
        ym = y_end - d
        curve_left = []
        curve_right = []
        for i in range(step):
            a = pi / 2 + i * pi / (step * 2)
            curve_left.append(x1 + d * cos(a))
            curve_left.append(ym + d * sin(a))
            b = i * pi / (step * 2)
            curve_right.append(x2 + d * cos(b))
            curve_right.append(ym + d * sin(b))
        vertices = (
            [x_start, y_start, x_end, y_start, x_end, ym]
            + curve_right
            + [x2, y_end, x1, y_end]
            + curve_left
            + [x_start, y_start]
        )
        can.create_polygon(vertices, outline=outline, fill=fill, width=thickness)
    else:
        can.create_rectangle(
            x_start, y_start, x_end, y_end, outline=outline, fill=fill, width=thickness
        )


def compare(element1, element2):
    """Return None if element1 and element2 are None.
    Otherwise return the element who is not None.
    """
    if element1 is None and element2 is None:
        return None
    elif element1 is None:
        return element2
    else:
        return element1


def split_unembed(line: str, separator: str = ",") -> list[str]:
    """Split a string line with the separator when it's not between two brackets or two parenthesis.
    Return a list of strings."""
    elements = []
    last_element = ""
    nb_opened_brackets = 0
    nb_opened_parenthesis = 0
    for char in line:
        if char == separator and nb_opened_brackets == 0 and nb_opened_parenthesis == 0:
            elements.append(last_element)
            last_element = ""
        elif char == "(":
            nb_opened_parenthesis += 1
            last_element += char
        elif char == ")":
            nb_opened_parenthesis -= 1
            last_element += char
        elif char == "[":
            nb_opened_brackets += 1
            last_element += char
        elif char == "]":
            nb_opened_brackets -= 1
            last_element += char
        else:
            last_element += char
    elements.append(last_element)
    return elements


def load_preferences(file=None):
    """Load the information stored in the preferences.json file."""
    security_file = "preferences_security.json"
    with open(security_file, "r") as f:
        security_pref = json.load(f)
    if file is None:
        file = "preferences.json"
    elif file == "dark":
        file = "preferences_default_dark.json"
    elif file == "light":
        file = "preferences_default_light.json"
    with open(file, "r") as f:
        preferences = json.load(f)
    # Checking data typing for int and bool
    for key, value in preferences.items():
        if "_int" in key:
            if type(value) == str:
                if not value.isdigit():
                    preferences[key] = security_pref[key]
                    # print(key, value, "changed to default value", security_pref[key])
            else:
                preferences[key] = security_pref[key]
        elif "_bool" in key:
            if type(value) == int:
                if value not in {0, 1}:
                    preferences[key] = security_pref[key]
            else:
                preferences[key] = security_pref[key]
        elif "_choice" in key:
            if type(value) == str:
                if value not in ["left", "center", "separator", "right"]:
                    preferences[key] = security_pref[key]
            else:
                preferences[key] = security_pref[key]
        else:
            if type(value) != type(security_pref[key]):
                preferences[key] = security_pref[key]
    return preferences


def write_preferences(preferences: dict):
    """Write the information stored in preferences dictionary
    in the preferences.json file
    """
    # Serializing json
    json_object = json.dumps(preferences, indent=4)
    with open("preferences.json", "w") as fichier:
        fichier.write(json_object)


class ScrollableFrame(tki.Frame):
    """source: https://blog.teclado.com/tkinter-scrollable-frames/"""

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tki.Canvas(self)
        scrollbar = tki.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tki.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


if __name__ == "__main__":
    # Tests
    print(split_unembed("a, b,(f, g), h", ","))
    print(split_unembed("a, b, [(c, d), e, (f, g)], i, j", ","))
    """
    print("index_occurrence : ", index_occurrence("e", "ereieoel"))
    print("parameters_in", parameters_in("param1, param2, (2,4), param3, (5, 7)"))
    print("coordinates : ", coordinates("(12, 43)"))
    d = {1: ["r", "t"], 2: ["a", "e", "r"], 3: ["u"]}
    print(d.pop(1, None))
    print(d)
    print(new_label([]))
    print(new_label(["a", "b"]))
    print(new_label(["a", "b", "d"]))
    print(cast_rgb_to_hex_color("(42,06,255)"))
    """
