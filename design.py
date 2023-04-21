# from function_block import *
# from node import *
import tools as tl


class Design:
    """ A graph structure fed by a list of nodes and functions.
        Gathers elements of the same area (directly connected to each other) by group instances.
        Provides dictionaries (self.nodes_levels and self.functions_levels) to locate nodes and
        functions by levels for a linear representation of the diagram.
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
            group.update_level(0)

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
        # Set of the groups of the next level.
        group1.next = group1.next.union(group2.next)
        # Set of the nodes of this group
        group1.nodes = group1.nodes.union(group2.nodes)
        group1.functions = group1.functions.union(
            group2.functions)  # Set of the functions of this group
        group1.level = tl.compare(group2.level, group2.level)
        self.groups.remove(group2)

    def report(self):
        """ Returns a tuple of dictionaries:
            + functions_dict : dictionnary with the functions as keys and their level as values.
            + floors_dict : dictionnary whose keys are the floors and whose values are the functions that belong to them.
        """
        self.max_floor = 0
        functions_dict = dict()
        floors_dict = dict()
        for group in self.groups:
            for function in group.functions:
                functions_dict[function] = group.level
                self.max_floor = max(self.max_floor, group.level)
                if group.level in floors_dict.keys():
                    floors_dict[group.level].append(function)
                else:
                    floors_dict[group.level] = [function]
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
        All function entries are used to determine the list self.next: List of groups on the next level.
    """

    def __init__(self, node):
        # Previous level group: Group of the output node function if it exists.
        self.previous = None
        self.next = set()  # Set of the groups of the next level.
        self.nodes = set()  # Set of the nodes of this group
        self.nodes.add(node)
        # Set of the functions of this group
        self.functions = set()
        # Level of this group: Relative position in the diagram, from left (level 0) to right.
        self.level = None

    def update_level(self, level):
        """ Updates the levels of the group. Recursively call the update level for each next group.
        """
        if self.level is None:
            self.level = level
        else:
            self.level = max(self.level, level)
        for function in self.functions:
            function.level = self.level
        for node in self.nodes:
            node.level = self.level
        for group in self.next:
            group.update_level(self.level+1)

    def __repr__(self):
        line = "Level: " + str(self.level)
        line += "Nodes: "
        for node in self.nodes:
            line += ". " + str(node)
        line += " / Functions: "
        for function in self.functions:
            line += "+ " + str(function)
        line += " / Nb of next groups: "+str(len(self.next))
        return line
