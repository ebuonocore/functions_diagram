import tools as tl


class Design:
    """ A graph structure fed by a list of nodes and functions.
        Gathers elements of the same area (directly connected to each other) by group instances.
        Provides dictionaries (self.nodes_floors and self.functions_floors) to locate nodes and
        functions by floors for a linear representation of the diagram.
    """

    def __init__(self, nodes=None, functions=None):
        self.groups = []  # Group aggregator
        self.leaves = []  # List of groups without output function nodes
        self.max_floor = -1
        # List of nodes
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes
        # List of functions
        if functions is None:
            self.functions = []
        else:
            self.functions = functions
        self.initialize_groupes()

    def initialize_groupes(self):
        """ Build groups of nodes and functions of the same area: directly connected to each other
        """
        # Creates a group for each node
        for node in self.nodes:
            group = Group(node)
            self.groups.append(group)
        # Browses the groups and merges those whose nodes are connected.
        for node in self.nodes:
            group = self.group_with_node(node)
            for connected_node in node.connections:
                if connected_node not in group.nodes:
                    other_group = self.group_with_node(
                        connected_node)
                    if other_group is not None:
                        self.merge(group, other_group)
        # Browse all the groups. Search node entries of function and update the function list of the group.
        for group in self.groups:
            leave = True  # True if there is no output function node in this group
            for node in group.nodes:
                if '>' in node.name:
                    leave = False
                if '<' in node.name:
                    function = self.function_with_node(node)
                    if function is not None:
                        group.functions.add(function)
            if leave:
                self.leaves.append(group)  # Update the list of leaves
        # Browse all groups. Find the outputs group of any functions and update the set of next groups.
        for group in self.groups:
            for function in group.functions:
                next_group = self.group_with_node(function.output)
                if next_group is not None:
                    group.next.add(next_group)
        for group in self.leaves:
            group.update_floor(0)

    def group_with_node(self, node):
        """ If it exists, return the group of the node. Otherwise, returns None
        """
        for group in self.groups:
            if node in group.nodes:
                return group
        return None

    def group_with_function(self, function):
        """ If it exists, return the group of the function. Otherwise, returns None
        """
        for group in self.groups:
            if function in group.functions:
                return group
        return None

    def function_with_node(self, node):
        """ If it exists, return the function of the node. Otherwise, returns None
        """
        for function in self.functions:
            if node in function.entries or node == function.output:
                return function
        return None

    def merge(self, group1, group2):
        """ Merges all the elements of group2 in group1.
            Deletes group2 from the self.groups list.
        """
        # Set of the groups of the next floor.
        group1.next = group1.next.union(group2.next)
        # Set of the nodes of this group
        group1.nodes = group1.nodes.union(group2.nodes)
        group1.functions = group1.functions.union(
            group2.functions)  # Set of the functions of this group
        group1.floor = tl.compare(group2.floor, group2.floor)
        self.groups.remove(group2)

    def are_reachables(self, origin, destination):
        """ origin and destination are nodes of the diagram.
            If one of these nodes is not an antecedent of the other, it returns True.
            Otherwise, returns False.
        """
        if origin not in self.nodes:
            return False
        if destination not in self.nodes:
            return False
        origin_group = self.group_with_node(origin)
        destination_group = self.group_with_node(destination)
        # At least one of the two nodes must belong to a leaf group.
        if origin_group not in self.leaves and destination_group not in self.leaves:
            return False
        # destination is not a successor of origin
        test_destination = origin_group.is_successor(destination)
        if test_destination == False:
            return False
        # origin is not a successsor of destination
        return destination_group.is_successor(origin)

    def report(self):
        """ Returns a tuple of dictionaries:
            + functions_dict : dictionnary with the functions as keys and their floor as values.
            + floors_dict : dictionnary whose keys are the floors and whose values are the functions that belong to them.
        """
        self.max_floor = 0
        functions_dict = dict()
        floors_dict = dict()
        for function in self.functions:
            functions_dict[function] = function.floor
            self.max_floor = max(self.max_floor, function.floor)
            if function.floor in floors_dict.keys():
                floors_dict[function.floor].append(function)
            else:
                floors_dict[function.floor] = [function]
        return functions_dict, floors_dict

    def __repr__(self):
        line = "Groups: "
        for group in self.groups:
            line += "\nGroup : " + str(group)
        return line


class Group:
    """ Groups the elements (nodes and functions) of the same area: directly connected to each other.
        A group can contain only one output function.
        In this case, self.previous refers to the group of this function.
        All function entries are used to determine the list self.next: List of groups on the next floor.
    """

    def __init__(self, node):
        # Previous floor group: Group of the output node function if it exists.
        self.previous = None
        self.next = set()  # Set of the groups of the next floor.
        self.nodes = set()  # Set of the nodes of this group
        self.nodes.add(node)
        # Set of the functions of this group
        self.functions = set()
        # floor of this group: Relative position in the diagram, from left (floor 0) to right.
        self.floor = None

    def update_floor(self, floor):
        """ Updates the floors of the group. Recursively call the update floor for each next group.
        """
        if self.floor is None:
            self.floor = floor
        else:
            self.floor = max(self.floor, floor)
        for function in self.functions:
            if function.floor < self.floor:
                function.floor = self.floor
        for node in self.nodes:
            node.floor = self.floor
        for group in self.next:
            group.update_floor(self.floor+1)

    def is_successor(self, node):
        """ Recursively traverses all subsequent groups.
            If the node appears in one of the following groups, it returns False.
            Otherwise, it returns True.
        """
        if node in self.nodes:
            return False
        for next_group in self.next:
            if next_group.is_successor(node) == False:
                return False
        return True

    def __repr__(self):
        line = "floor: " + str(self.floor)
        line += " / Nodes: "
        for node in self.nodes:
            line += str(node) + " "
        line += " / Functions: "
        for function in self.functions:
            line += str(function) + " "
        line += " / Nb of next groups: " + str(len(self.next))
        return line
