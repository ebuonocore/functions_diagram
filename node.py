class Node:
    """ Associated nodes: Entries or output of function-blocks.
        Free nodes: Not in functions. Intermediate between diagram nodes
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
        # Zone of this node. Only one output per zone.
        self.zone = None
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")
        if '>' in self.label:
            self.zone = self.name

    def explore_zone(self, level=None, visited=None):
        """ Recursively explores all nodes directly connected to the current node.
            Returns the level of the connected function output (otherwise None) and the set of
            the nodes at the same level.
        """
        if visited is None:
            visited = set()
        for connected_node in self.connections:
            if connected_node not in visited:
                visited.add(connected_node)
                if connected_node.zone is not None:
                    new_node_level = connected_node.zone
                    if level is None:
                        level = new_node_level
                    if new_node_level is not None:
                        level = max(new_node_level, level)
                level, visited = connected_node.explore_zone(level, visited)
        return level, visited

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
