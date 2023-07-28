import tools as tl
from node import Node
from function_block import Function_block


def sup(a, b):
    """Return the maximum between a and b.
    if a is None, return b.
    """
    if a is None:
        return b
    if a > b:
        return a
    return b


def inf(a, b):
    """Return the minimum between a and b.
    if a is None, return b.
    """
    if a is None:
        return b
    if a < b:
        return a
    return b


class Group:
    """Area defined by its dimensions or the set of functions and nodes it contains."""

    def __init__(self, **kwargs):
        self.name = None  # Unique reference of the function block
        self.label = ""  # Label to be print in screen
        # List of dictionaries of elements. [{"id":int, "type":str,"enable":boolean,"element":Node|Function_block,  "position":[int, int]}]
        self.elements = list()
        # list of dictionaries : {"id": ref, "type": type_element, "enable": True, "element": element, "position": position}
        self.position = [None, None]  # [pos_x, pos_y]
        self.dimension = []  # [width, height]
        # True if the position is fixed (Auto mode can't move this function).
        self.fixed = True
        self.preferences = tl.load_preferences()
        self.color = self.preferences["group color_color"]
        self.thickness = self.preferences["group thickness_int"]
        self.margin = int(self.preferences["group margin_int"])
        police = self.preferences["police"]
        title_size = int(self.preferences["title size_int"])
        self.title_char_width, self.title_char_height = tl.character_dimensions(
            police, title_size
        )
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")

    def update_existing_elements(self, diagram):
        """check if the element exists in the diagram. Otherwise, remove it from the list."""
        for element in self.elements:
            if element["type"] == "Function_block":
                if element["element"] not in diagram.functions.values():
                    self.elements.remove(element)
            elif element["type"] == "Node":
                if element["element"] not in diagram.nodes.values():
                    self.elements.remove(element)

    def add_function(self, new_function):
        """Add a new function in the elements list if it doesn't already exists."""
        for element in self.elements:
            if element["element"] == new_function:
                return False
        self.elements.append(
            {
                "id": len(self.elements),
                "type": "Function_block",
                "enable": True,
                "element": new_function,
                "position": [0, 0],
            }
        )
        self.update_coordinates()
        return True

    def add_node(self, new_node):
        """Add a new node in the elements list if it doesn't already exists."""
        for element in self.elements:
            if element["element"] == new_node:
                return False
        self.elements.append(
            {
                "id": len(self.elements),
                "type": "Node",
                "enable": True,
                "element": new_node,
                "position": [0, 0],
            }
        )
        self.update_coordinates()
        return True

    def search_elements_in(self, diagram, origin, destination):
        elements = list()
        x_origin, y_origin = origin
        objects = tl.search_in_rectangle(diagram, origin, destination)
        for ref, element in enumerate(objects):
            x_element, y_element = element.position
            type_element = type(element).__name__
            position = [x_element - x_origin, y_element - y_origin]
            elements.append(
                {
                    "id": ref,
                    "type": type_element,
                    "enable": True,
                    "element": element,
                    "position": position,
                }
            )
        return elements

    def update_coordinates(self):
        """Update the coordinates of the group based on the elements it contains."""
        if self.fixed:
            return False
        x_min = None
        y_min = None
        x_max = None
        y_max = None
        if len(self.elements) == 0:
            return False
        for element in self.elements:
            if element["type"] == "Node" and element["enable"]:
                x, y = element["element"].position
                x_min = inf(x_min, x)
                y_min = inf(y_min, y)
                x_max = sup(x_max, x)
                y_max = sup(y_max, y)

            elif element["type"] == "Function_block" and element["enable"]:
                x_left, y_top = element["element"].position
                x_right = x_left + element["element"].dimension[0]
                y_bottom = (
                    y_top + element["element"].dimension[1] + self.title_char_height
                )
                x_min = inf(x_min, x_left)
                y_min = inf(y_min, y_top)
                x_max = sup(x_max, x_right)
                y_max = sup(y_max, y_bottom)
        margin = int(self.margin)
        if x_min is not None and y_min is not None:
            self.position = [x_min - margin, y_min - margin]
            self.dimension = [
                x_max - x_min + 2 * margin,
                y_max - y_min + 2 * margin,
            ]
        else:
            return False
        # Update the position of the elements in the group
        x, y = self.position
        for element in self.elements:
            xe = element["element"].position[0]
            ye = element["element"].position[1]
            element["position"] = [xe - x, ye - y]
        return True

    def follow(self, destination):
        for element in self.elements:
            if element["element"] == destination:
                if element["enable"]:
                    self.update_coordinates()

    def __repr__(self):
        line = str(self.name) + "("
        line += "fixed: " + str(self.fixed) + ", "
        line += "margin: " + str(self.margin) + ", "
        line += "color: " + str(self.color) + ", "
        line += "thickness: " + str(self.thickness) + ")"
        return line
