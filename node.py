class Node:
    """ Associated nodes: Entries or output of function-blocks.
        Free nodes: Not in functions.
    """

    def __init__(self, **kwargs):
        self.name = ''
        self.label = ''
        self.annotation = ''
        # True if it's a free node (not in a function-block).
        self.free = False
        # False if the node is hided. True if it's visible.
        self.visible = True
        self.position = [None, None]  # [pos_x, pos_y]
        self.connections = []  # List of nodes connected
        self.fixed = False  # True if the position is fixed (can't be moved).
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")

    def __repr__(self):
        line = self.name
        """
        line = self.name + ":" + self.annotation + ' '
        line += str(len(self.connections)) + " Connection(s) "
        if self.position != []:
            line += "Position: " + str(self.position)
        """
        return line


if __name__ == "__main__":
    pass
