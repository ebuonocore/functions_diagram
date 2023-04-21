from tkinter import font as tkfont
import diagram as dia
from math import sqrt
from node import *
from link import *
from function_block import *
import matplotlib.colors as mcolors
from math import cos, sin, pi


def index_occurrence(char, string):
    """ Returns the list of indexes of occurrences of char in the string."""
    return [i for i, j in enumerate(string) if j == char]


def function_rank(function, function_list):
    """ Returns the index of occurrence of the function in the function_list."""
    rank = 0
    while rank < len(function_list):
        if function is function_list[rank]:
            return rank
        rank += 1
    return 0


def parameters_in(line):
    """
    Returns the list of strings in line separated by commas except those enclosed in parentheses.
    Example :
    >>> parameters_in("param1, param2, (2,4), param3, (5, 7)")
    (["param1", "param2", "(2,4)", "param3", "(5, 7)"]
    """
    parameters = []
    parameter = ""
    parenthesis = 0
    for char in line:
        if parenthesis == 0 and char == ',':
            parameters.append(parameter)
            parameter = ""
        elif char == '(':
            parenthesis += 1
        elif char == ')':
            parenthesis -= 1
        else:
            parameter += char
    parameters.append(parameter)
    return parameters


def coordinates(parameters):
    """
        If parameters is a pair of integer-castable strings, then returns the list of matching integers.
        Otherwise returns None.
        >>> coordinates("(12, 43)")
        [12,43]
        >>> coordinates("12, 43")
        [12,43]
    """
    parameters = parameters.replace(' ', '')
    if parameters[0] == '(' and parameters[-1] == ')':
        parameters = parameters[1:-1]
    pos_comma = index_occurrence(',', parameters)
    if len(pos_comma) == 1:
        x_str, y_str = parameters.split(',')
        if x_str.isdigit() and y_str.isdigit():
            x, y = int(x_str), int(y_str)
            return [x, y]
    return None


def character_dimensions(police, size):
    """ Returns the (width, height) of a character of a mono-spaced font."""
    nb_pixels_height = tkfont.Font(
        size=size, family=police).metrics('linespace')
    nb_pixels_width = tkfont.Font(size=size, family=police).measure('X')
    return (nb_pixels_width, nb_pixels_height)


def key_of(dictionary, value):
    """ Returns the first dictionary key that matches the searched value. Otherwise, returns None.
    """
    for k, v in dictionary.items():
        if v == value:
            return k
    return None


def create_definition_description(function):
    """ Create the string description of a function.
        Example : "def my_function(a:int, b:float)->float"
    """
    description = "def " + function.name + '('
    one_entry_or_more = False
    for entry in function.entries:
        one_entry_or_more = True
        description += entry.label
        if entry.annotation != '':
            description += ':' + entry.annotation
        description += ','
    if one_entry_or_more:
        description = description[:-1]
    description += ')'
    if function.output is not None:
        if function.output.visible == False or function.output.annotation != '':
            description += '->'
        if function.output.visible == False:
            description += '*'
        if function.output.annotation != '':
            description += function.output.annotation
    if function.header_color is not None:
        description += "  # header_color = \"" + function.header_color + "\""
    description += '\n'
    # Add the position
    description += function.name + ".position("
    description += str(int(function.position[0])) + ','
    description += str(int(function.position[1])) + ')\n'
    # Add the dimension
    if function.dimension != []:
        description += function.name + ".dimension("
        description += str(int(function.dimension[0])) + ','
        description += str(int(function.dimension[1])) + ')\n'
    return description


def create_node_description(node):
    """ Create the string description of a free node (not in a function).
        Example for the A node at position (800, 200): "node (A:str,(800,200))"
    """
    if node.free:
        description = "node" + '(' + node.name
        if node.annotation != '':
            description += ':' + node.annotation
        # Add the position
        description += ',('
        description += str(int(node.position[0])) + ','
        description += str(int(node.position[1])) + '))\n'
        return description
    else:
        return ''


def reverse(link_description):
    """ create the symmetric expression of the link between two nodes.
    Example for "A---B" : "B---A"
    """
    nodes = link_description.split('---')
    if len(nodes) == 2:
        return nodes[1] + '---' + nodes[0]


def distance(origin_position, target_position):
    x1, y1 = origin_position
    x2, y2 = target_position
    return sqrt((x2-x1)**2+(y2-y1)**2)


def nearest(mouse_position, targets):
    """ Return the nearest object (and the distance) from the mouse_position.
    """
    nearest_target = None
    nearest_target_distance = None
    for target in targets:
        compliant_target = False
        if type(target) == Function_block:
            compliant_target = True
            position_x = target.position[0] + target.dimension[0]//2
            position_y = target.position[1] + target.dimension[1]//2
            position = (position_x, position_y)
        if type(target) == Node or type(target) == Link:
            compliant_target = True
            position = target.position
        if compliant_target:  # target is a free node or a function
            dist = distance(mouse_position, position)
            if nearest_target_distance is None:
                nearest_target = target
                nearest_target_distance = dist
            elif dist < nearest_target_distance:
                nearest_target = target
                nearest_target_distance = dist
    return nearest_target, nearest_target_distance


def nearest_objet(mouse_position, diagram, target_types="movable"):
    """ Returns the nearest object from the cursor.
        target_types can be "all" (default), "function" or "node"
    """
    population = []
    if target_types != "node":
        population += diagram.functions.values()
    if target_types != "function":
        population += [node for node in diagram.nodes.values() if node.free]
    if target_types == "erasable":
        population += diagram.links

    nearest_target, nearest_target_distance = nearest(
        mouse_position, population)
    return nearest_target


def pointer_position(window):
    """ Returns the pointer position relative to the origin of the main canvas.
    """
    mouse_x = window.winfo_pointerx() - window.winfo_rootx()
    mouse_y = window.winfo_pointery() - window.winfo_rooty()
    return mouse_x, mouse_y


def new_label(previous_labels, label=None):
    """ Returns the next_label who's not in previous label.
        label (optional) is the current label.
    """
    if label is None:
        label = "a"
    while label in previous_labels:
        label = next_label(label)
    return label


def next_label(previous_label):
    """ Increment the last character of the previous_label string.
    """
    alphabet = [chr(i) for i in range(97, 123, 1)]
    parts = previous_label.split('*')
    substring = parts[-1]  # Part of the string to increment
    if substring == "" and len(parts) == 0:
        return 'a'
    elif substring == "" and len(parts) > 0:
        return parts[0]+'*a'
    # Increment the last character of the substring
    last_char = substring[-1]
    if last_char not in alphabet:
        last_char = 'a'
    last_char = chr(ord(last_char)+1)
    substring = substring[:-1] + last_char
    for i in range(len(substring)-1, 0, -1):
        if ord(substring[i]) >= 123:
            substring = change_str(substring, i, 'a')
            carry = chr(ord(substring[i-1])+1)
            substring = change_str(substring, i-1, carry)
    if ord(substring[0]) >= 123:
        substring = change_str(substring, len(substring)-1, 'a')
        substring = 'a' + substring
    if len(parts) == 1:
        return substring
    else:
        return parts[0]+'*'+substring


def change_str(string_source, index, char):
    """ Returns the string source with char at the index.
    """
    source = list(string_source)
    if index > len(source):
        return string_source
    source[index] = char
    return "".join(source)


def cast_to_float(value_str: str, shape=None) -> float:
    """ Takes a value (str) in parameter.
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
    if len(index_occurrence('.', value_str)) < 2:
        for element in value_str:
            if element not in '0123456789.':
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
    """ Takes a value (str) in parameter.
    if value is cast to integer, returns the integer value.
    Otherwise, returns None.
    if format is "8bits" returns the integer value only if it's between 0 and 255, .
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


def cast_to_color(color_str: str, format=None) -> str:
    """ Takes color_str in parameter : A specific name of mcolors.CSS4_COLORS key or a rgb format.
    if format is "hex" accepts  or colors in hexadecimal digits.
    Returns the good format to insert the color in the fill setting of the SVG file.
    Otherwise, returns None.
    >>> cast_to_color("green")
    green
    >>> cast_to_color("(42,0,255)")
    rgb(42,0,255)
    >>> cast_to_color("42")
    None
    """
    if format is None:
        if color_str == "":
            color_str = "white"
        if color_str in mcolors.CSS4_COLORS.keys():
            return color_str
        elif color_str[0] == '(' and color_str[-1] == ')':
            rgb = color_str[1:-1].replace(' ', '').split(',')
            if len(rgb) == 3:
                if test_compound(rgb[0]) and test_compound(rgb[1]) and test_compound(rgb[2]):
                    return 'rgb'+color_str
    elif format == "hex":
        if color_str[0] == '#':
            color_str = color_str[1:]
            if len(color_str) == 6 or len(color_str) == 3:
                format_ok = True
                hex_digits = [chr(i) for i in range(48, 58)]
                hex_digits += [chr(i) for i in range(65, 71)]
                hex_digits += [chr(i) for i in range(97, 103)]
                for digit in color_str:
                    if digit not in hex_digits:
                        format_ok = False
                if format_ok:
                    return color_str
    return None


def cast_rgb_to_hex_color(color_str):
    """ If color_str is a color tuple, it casts and returns this color in an hexadecimal format.
        Otherwise, it returns the unmodified colour string.
    """
    if color_str[0] == '(' and color_str[-1] == ')':
        rgb = color_str[1:-1].replace(' ', '').split(',')
        if len(rgb) == 3:
            if test_compound(rgb[0]) and test_compound(rgb[1]) and test_compound(rgb[2]):
                R, V, B = map(hex_digit, rgb)
                return '#'+R+V+B
    return color_str


def hex_digit(value_str):
    """ value_str is a string castable to an int , 0 < value < 255
        Casts value in hex and returns the two hexadecimal digits in a string format
    """
    if value_str.isdigit():
        value = int(value_str)
        return ('00'+str(hex(value)[2:]))[-2:]
    return 'FF'


def test_compound(compound: str) -> bool:
    """Takes a str in parameter.
    If compound is castable to int and lower than 256, returns True.
    """
    if compound.isdigit():
        if 0 <= int(compound) < 256:
            return True
    return False


def draw_box(can, x_start, y_start, x_end, y_end, **kwargs):
    """ Create a rectangle in the canvas (can).
        if rounded is True, create a rounded rectangle.
    """
    outline = 'black'
    fill = 'white'
    rounded_up = False
    rounded_down = False
    thickness = 1
    radius = 2  # bending_radius
    step = 20
    for k, v in kwargs.items():
        if k == 'outline':
            outline = v
        elif k == 'fill':
            fill = v
        elif k == 'rounded_up':
            rounded_up = v
        elif k == 'rounded_down':
            rounded_down = v
        elif k == 'thickness':
            thickness = v
        elif k == 'radius':
            radius = v
        elif k == 'step':
            step = v
    if rounded_up == True:
        d = max(radius, (y_end - y_start) // 2)
        x1 = x_start + d
        x2 = x_end - d
        ym = y_start + d
        curve_left = []
        curve_right = []
        for i in range(step):
            a = pi + i*pi/(step*2)
            curve_left.append(x1+d*cos(a))
            curve_left.append(ym+d*sin(a))
            b = a + pi/2
            curve_right.append(x2+d*cos(b))
            curve_right.append(ym+d*sin(b))
        vertices = [x_start, y_end, x_start, ym] + curve_left + [x1,
                                                                 y_start, x2, y_start] + curve_right + [x_end, ym, x_end, y_end]
        can.create_polygon(vertices,
                           outline=outline, fill=fill, width=thickness)
    elif rounded_down == True:
        d = max(radius, 2)
        x1 = x_start + d
        x2 = x_end - d
        ym = y_end - d
        curve_left = []
        curve_right = []
        for i in range(step):
            a = pi/2 + i*pi/(step*2)
            curve_left.append(x1+d*cos(a))
            curve_left.append(ym+d*sin(a))
            b = i*pi/(step*2)
            curve_right.append(x2+d*cos(b))
            curve_right.append(ym+d*sin(b))
        vertices = [x_start, y_start, x_end, y_start, x_end, ym] + curve_right + [x2,
                                                                                  y_end, x1, y_end] + curve_left + [x_start, y_start]
        can.create_polygon(vertices,
                           outline=outline, fill=fill, width=thickness)
    else:
        can.create_rectangle(x_start, y_start, x_end, y_end,
                             outline=outline, fill=fill, width=thickness)


def compare(element1, element2):
    """ Returns None if element1 and element2 are None.
        Otherwise returns the element who is not None.
    """
    if element1 is None and element2 is None:
        return None
    elif element1 is None:
        return element2
    else:
        return element1


if __name__ == "__main__":
    # Tests
    print("index_occurrence : ", index_occurrence("e", "ereieoel"))
    print("parameters_in", parameters_in(
        "param1, param2, (2,4), param3, (5, 7)"))
    print("coordinates : ", coordinates("(12, 43)"))
    d = {1: ['r', 't'], 2: ['a', 'e', 'r'], 3: ['u']}
    print(d.pop(1, None))
    print(d)
    print(new_label([]))
    print(new_label(['a', 'b']))
    print(new_label(['a', 'b', 'd']))
    print(cast_rgb_to_hex_color("(42,06,255)"))
