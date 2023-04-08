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

    def update_zone(self):
        """ Fixe la zone du noeud par appel récursif des noeuds connectés.
            Renvoie la zone du noeud de sortie de fonction trouvée ou -1.
            La zone des noeuds non encore visités ont pour value None. 
        """
        if self.zone is None:
            self.zone = -1
        else:
            return self.zone
        for connected_node in self.connections:
            zone = connected_node.update_zone()
            if zone != -1:
                self.zone = zone
                return zone
        self.zone = -1
        return -1

    def __repr__(self):
        line = self.name + ":" + self.annotation + ' '
        line += str(len(self.connections)) + " Connection(s) "
        if self.position != []:
            line += "Position: " + str(self.position)
        return line + "\n"


if __name__ == "__main__":
    pass
