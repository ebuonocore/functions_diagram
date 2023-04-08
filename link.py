class Link:
    """ Link between two nodes in self.nodes list.
        self.position is the middle of the nodes
    """

    def __init__(self, **kwargs):
        self.nodes = list()  # list of the two nodes
        self.position = list()  # [pos_x, pos_y]
        # list of cardinal points of the link: start, first, middle, last, end
        self.points = list()  # List of tuples
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k] = v
            else:
                raise Exception("The key " + k + " doesn't exist.")
        self.update_positions()

    def update_positions(self):
        """ Update the position of the link."""
        if len(self.nodes) == 2:
            if self.nodes[0].position == [None, None]:
                return list()
            if self.nodes[1].position == [None, None]:
                return list()
            else:
                self.points = list()
                x_start, y_start = self.nodes[0].position  # Starting node
                x_end, y_end = self.nodes[1].position  # Ending node
                x_middle = (x_start + x_end) // 2
                y_middle = (y_start + y_end) // 2
                x_first = (x_start + x_middle) // 2
                y_first = (y_start + y_middle) // 2
                x_last = (x_end + x_middle) // 2
                y_last = (y_end + y_middle) // 2
                self.position = [x_middle, y_middle]
                self.points.append((x_start, y_start))
                self.points.append((x_first, y_first))
                self.points.append(tuple(self.position))
                self.points.append((x_last, y_last))
                self.points.append((x_end, y_end))  # Ending node
        else:
            return list()
