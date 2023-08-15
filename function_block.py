from node import *


class Function_block:
    """Functions of a diagram."""

    def __init__(self, **kwargs):
        self.name = None  # Unique reference of the function block
        self.label = ""  # Label to be print in screen
        self.entries = []  # List of nodes
        self.output = None  # Output node
        # False if the output is hided. True if it's visible.
        self.position = [None, None]  # [pos_x, pos_y]
        self.dimension = []  # [width, height]
        # True if the position is fixed (Auto mode can't move this function).
        self.fixed = False
        self.floor = -1  # Depth in the graph. Leaves at 0.
        self.header_color = None
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")

    def search_node(self, name):
        """Return the input node named name."""
        for entry in self.entries:
            if entry.name == name:
                return entry
        return None

    def set_output_visibility(self, visible: bool):
        """Set the output visibility."""
        self.output.visible = visible

    def copy(self, new_name=None):
        """Return a copy of the function_block with an other name if new_name is not None."""
        next_function = Function_block(**self.__dict__)
        if new_name is not None:
            next_function.name = new_name
        next_function.entries = []
        for entry in self.entries:
            next_function.entries.append(entry.copy())
        next_function.output = self.output.copy()
        next_function.floor = -1
        return next_function

    def __repr__(self):
        line = str(self.name)
        """
        line = "** Function:" + str(self.name) + '\n'
        line += "Parameters: "
        for entry in self.entries:
            line += entry.name + '(' + entry.label
            if len(entry.annotation) > 0:
                line += ':' + entry.annotation
            line += ') '
        line += '\n'
        if self.output is not None:
            line += "Output: " + str(self.output.annotation) + '\n'
        if self.position != []:
            line += "Position: " + str(self.position) + '\n'
        if self.dimension != []:
            line += "Dimension: " + str(self.dimension) + '\n'
        """
        return line
