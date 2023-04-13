from function_block import *
from node import *
from link import *
import tools as tl


class Diagram:
    """ Container of de function-blocks and the nodes."""

    def __init__(self):
        self.functions = dict()  # keys = functions names, values = functions objects
        self.nodes = dict()  # keys = nodes names, valeus = nodes objects
        # Grouping of connected points (same potential linked at most to a function output)
        self.zones = dict()  #
        # keys = floor number, values = list of functions in this floor.
        self.floors = dict()
        self.links = list()  # List of Links
        self.zones_tree = {}  # liste of description des niveaux antécédentes pour chaque niveau

    def is_empty(self):
        """ Returns True if there is no function and no nodes
        """
        return len(self.functions) == 0 and len(self.nodes) == 0

    def object_new_name(self, name):
        if '*' in name:
            star_pos = name.index('*')
            suffix = name[star_pos:]
            if suffix == "*":
                suffix = '*0'
            last_char = suffix[-1]
            new_last_char = chr(ord(last_char)+1)
            new_suffix = suffix[:-1] + new_last_char
            new_name = name[:star_pos] + new_suffix
        else:
            new_name = name + '*0'
        return new_name

    def add_function(self, new_function):
        """
            Add a new function in the diagram.
            If the function's name already exist, increment the name and add the modifies function.
        """
        if new_function.name in self.functions.keys():
            new_function.name = self.object_new_name(new_function.name)
        self.functions[new_function.name] = new_function
        for entry in new_function.entries:
            self.add_node(entry)
        self.add_node(new_function.output)

    def delete_function(self, function_name):
        """ Delete the function in the diagram. Remove all the nodes of these function.
        """
        function = self.functions[function_name]
        pop_result = self.functions.pop(function_name)
        if pop_result is not None:
            for node in function.entries:
                self.delete_node(node.name)
            self.delete_node(function.output.name)
        return pop_result

    def add_node(self, new_node):
        """
            Add a new node in the diagram.
        """
        if type(new_node) == Node and new_node.name not in self.nodes.keys():
            self.nodes[new_node.name] = new_node
            return True
        else:
            return False

    def delete_node(self, node_name):
        """ Deletes the node in the diagram and all references of this node in the list of connections of the other node.
        """
        pop_result = self.nodes.pop(node_name)
        if pop_result is not None:
            for node in self.nodes.values():
                for node_connected in node.connections:
                    if node_name == node_connected.name:
                        node.connections.remove(node_connected)
            for link in self.links:
                if pop_result in link.nodes:
                    self.links.remove(link)
        return pop_result

    def nodes_connection(self, A, B):
        """
            Create a link between the nodes node_A and node_B designated by the names A and B respectively.
        """
        if A in self.nodes.keys() and B in self.nodes.keys():
            node_A = self.nodes[A]
            node_B = self.nodes[B]
            node_B.connections.append(node_A)
            node_A.connections.append(node_B)
            link = Link(nodes=[node_A, node_B])
            self.links.append(link)
            return True
        return False

    def disconnect_nodes(self, link):
        """ Disconnects the two nodes of the link.
        """
        if len(link.nodes) == 2:
            node_A = link.nodes[0]
            node_B = link.nodes[1]
            if node_B in node_A.connections:
                node_A.connections.remove(node_B)
            if node_A in node_B.connections:
                node_B.connections.remove(node_A)
        if link in self.links:
            self.links.remove(destination)

    def update_zones(self):
        """ Explores all the nodes of the diagram. Builds the dictionary of zones containing
            their levels and the lists of nodes at the same level (connected together)
            The level of a zone connected to an output is positive.
            Zones not connected to an output have a negative level.
        """
        # Initialization
        self.zones = {}
        current_level = 0
        for node in self.nodes.values():
            node.zone = None
        for function in self.functions.values():
            self.zones[current_level] = [function.output]
            function.output.zone = current_level
            current_level += 1
        current_level = -1
        to_visit = {node for node in self.nodes.values()}
        # Explore and update all nodes
        while len(to_visit) > 0:
            node = to_visit.pop()
            level, visited = node.explore_zone(node.zone, {node})
            if level is None:
                level = current_level
                self.zones[level] = []
                current_level -= 1
            for node in visited:
                node.zone = level
                if node not in self.zones[level]:
                    self.zones[level].append(node)
                if node in to_visit:
                    to_visit.remove(node)
        self.update_zones_tree()

    def update_zones_tree(self):
        self.zones_tree = dict()
        for level, nodes in self.zones.items():
            if level >= 0:
                function = self.function_in(nodes)
                if function is not None:
                    antecedents = []
                    for entry in function.entries:
                        antecedents.append(entry.zone)
                    self.zones_tree[level] = antecedents

    def function_in(self, nodes: list):
        """ Returns the function whose output is in the list of nodes.
        """
        for node in nodes:
            if '>' in node.name:
                function_name = node.name.split('>')[0]
                if function_name in self.functions:
                    return self.functions[function_name]
        return None

    def are_reachables(self, node_A, node_B):
        """ Returns True if a link can be created between node_A and node_B without creating a feedback loop.
        """
        self.update_zones()
        level_A = node_A.zone
        level_B = node_B.zone
        antecedent_A = self.antecedents(level_A)
        antecedent_B = self.antecedents(level_B)
        print(level_A, level_B, antecedent_A, antecedent_B)
        # False if node_A and node_B are linked to different outputs.
        if level_A >= 0 and level_B >= 0:
            return False
        # False a node is a antecedent of the other one.
        elif level_B in antecedent_A:
            return False
        elif level_A in antecedent_B:
            return False
        else:
            return True

    def antecedents(self, level, levels=None):
        if levels is None:
            levels = set()
        if level in levels:
            return levels
        levels.add(level)
        if level < 0:
            return levels
        for zone_level in self.zones_tree[level]:
            levels = self.antecedents(zone_level, levels)
        return levels

    def update_function_floor(self, function):
        # function.floor already update
        if function.floor >= 0:
            return function.floor
        # Build the list of the daughter functions
        zone = function.output.zone
        neighbors = self.zones[zone]
        daughters = []
        for neighbor in neighbors:
            if '<' in neighbor.name:
                function_name = neighbor.name.split('<')[0]
                if function_name in self.functions:
                    daughters.append(self.functions[function_name])
        # Leave find
        if len(daughters) == 0:
            function.floor = 0
            return 0
        # Function with daughters
        min_floor = 0
        for daughter in daughters:
            daughter_floor = self.update_function_floor(daughter)
            if daughter_floor > min_floor:
                min_floor = daughter_floor
        function.floor = min_floor + 1
        return function.floor

    def update_floors(self):
        """ Initialise tous les étages des fonctions à -1
        """
        self.floors = dict()
        for function in self.functions.values():
            function.floor = -1
        """
        for function in self.functions.values():
            floor = self.update_function_floor(function)
            if floor in self.floors.keys():
                self.floors[floor].append(function)
            else:
                self.floors[floor] = [function]
        """

    def update_links(self):
        self.links = list()
        lines_ok = set()  # Ensemble de tuples (point_de_depart, point_d_arrivee)
        for start_node in self.nodes.values():
            for end_node in start_node.connections:
                if (end_node, start_node) not in lines_ok:
                    link = Link(nodes=[start_node, end_node])
                    self.links.append(link)
                    lines_ok.add((start_node, end_node))

    def export_to_text(self):
        diagram_datas = ""
        for function in self.functions.values():
            diagram_datas += tl.create_definition_description(
                function) + '\n'
        for node in self.nodes.values():
            diagram_datas += tl.create_node_description(node)
        links = []  # list of str : descriptions of the links
        for node in self.nodes.values():
            for connection in node.connections:
                link_description = node.name + '---' + connection.name
                if tl.reverse(link_description) not in links:
                    diagram_datas += link_description + '\n'
                    links.append(link_description)
        return diagram_datas

    def change_destination_name(self, destination, new_name):
        """ Changes the name attribute of the destination (a node or a function).
            If it is a node, updates the diagram's node dictionnary.
            If it is a function, updates the diagram's node dictionnary and changes the name of all these nodes.
            Returns True if change is ok. Otherwise retruns False.
        """
        if type(destination) == Node:
            return self.change_node_name(destination, new_name)
        elif type(destination) == Function_block:
            return self.change_function_name(destination, new_name)
        return False

    def change_function_name(self, function, new_name):
        if function.name in self.functions.keys():
            del self.functions[function.name]
            function.name = new_name
            self.functions[function.name] = function
            for entry in function.entries:
                parts = entry.name.split('<')
                if len(parts) > 0:
                    entry_prefix = parts[0]
                    entry_suffix = '<' + parts[1]
                self.change_node_name(entry, new_name+entry_suffix)
            self.change_node_name(function.output, new_name+'>')
            return True
        return False

    def change_node_name(self, node, new_name):
        """ Changes the name attribute of the node (destination).
            Updates the diagram's node dictionnary.
        """
        if node.name in self.nodes.keys():
            del self.nodes[node.name]
            node.name = new_name
            self.nodes[node.name] = node
            return True
        return False

    def __repr__(self):
        line = "***** Functions\n"
        for func in self.functions.values():
            line += repr(func)
        line += "***** Nodes\n"
        for node in self.nodes.values():
            line += repr(node)
        return line + "\n"
