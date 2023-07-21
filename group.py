from node import *
from function_block import *


class Group:
    """Area defined by its dimensions or the set of functions and nodes it contains."""

    def __init__(self, **kwargs):
        self.name = None  # Unique reference of the function block
        self.label = ""  # Label to be print in screen
        # List of dictionaries of elements. [{"id":int, "type":str,"enable":boolean,"element":Node|Function_block,  "position":[int, int]}]
        self.elements = list()
        self.position = [None, None]  # [pos_x, pos_y]
        self.dimension = []  # [width, height]
        # True if the position is fixed (Auto mode can't move this function).
        self.fixed = False
        self.color = ""
        self.thickness = ""
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")

    def __repr__(self):
        pass
