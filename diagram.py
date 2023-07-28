from function_block import *
from node import *
from group import *
from link import *

from design import Design
import tools as tl


class Diagram:
    """Container of de function-blocks and the nodes."""

    def __init__(self):
        self.functions = dict()  # keys = functions names, values = functions objects
        self.nodes = dict()  # keys = nodes names, values = nodes objects
        self.groups = dict()  # keys = groups names, values = groups objects
        # keys = floor number, values = list of functions in this floor.
        self.floors = dict()
        self.links = list()  # List of links

    def is_empty(self):
        """Return True if there is no function and no nodes"""
        return len(self.functions) == 0 and len(self.nodes) == 0

    def object_new_name(self, name):
        if "*" in name:
            star_pos = name.index("*")
            suffix = name[star_pos:]
            if suffix == "*":
                suffix = "*0"
            last_char = suffix[-1]
            new_last_char = chr(ord(last_char) + 1)
            new_suffix = suffix[:-1] + new_last_char
            new_name = name[:star_pos] + new_suffix
        else:
            new_name = name + "*0"
        return new_name

    def add_function(self, new_function):
        """Add a new function in the diagram.
        If the function's name already exist, increment the name and add the modifies function.
        """
        if new_function.name in self.functions.keys():
            new_function.name = self.object_new_name(new_function.name)
        self.functions[new_function.name] = new_function
        for entry in new_function.entries:
            self.add_node(entry)
        self.add_node(new_function.output)

    def delete_function(self, function_name):
        """Delete the function in the diagram. Remove all the nodes of these function."""
        if function_name in self.functions.keys():
            function = self.functions[function_name]
            pop_result = self.functions.pop(function_name)
            if pop_result is not None:
                for node in function.entries:
                    self.delete_node(node.name)
                self.delete_node(function.output.name)
            return pop_result
        else:
            return None

    def delete_node(self, node_name):
        """Delete the node in the diagram and all references of this node in the list of connections of the other node."""
        if node_name in self.nodes.keys():
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
        else:
            return None

    def delete_group(self, group_name):
        """Delete the group in the diagram. Don't remove the elements inside."""
        if group_name in self.groups.keys():
            pop_result = self.groups.pop(group_name)
            return pop_result
        else:
            return None

    def add_node(self, new_node):
        """Add a new node in the diagram."""
        test_new_name = new_node.name not in tl.all_previous_names(self)
        if type(new_node) == Node and test_new_name:
            self.nodes[new_node.name] = new_node
            return True
        else:
            return False

    def add_group(self, new_group):
        """Add a new group in the diagram."""
        test_new_name = new_group.name not in tl.all_previous_names(self)
        if type(new_group) == Group and test_new_name:
            self.groups[new_group.name] = new_group
            return True
        else:
            return False

    def nodes_connection(self, A, B):
        """Create a link between the nodes node_A and node_B designated by the names A and B respectively."""
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
        """Disconnect the two nodes of the link."""
        if len(link.nodes) == 2:
            node_A = link.nodes[0]
            node_B = link.nodes[1]
            if node_B in node_A.connections:
                node_A.connections.remove(node_B)
            if node_A in node_B.connections:
                node_B.connections.remove(node_A)
        if link in self.links:
            self.links.remove(link)

    def update_links(self):
        self.links = list()
        lines_ok = set()  # Set of tuples (point_of_departure, point_of_arrival)
        for start_node in self.nodes.values():
            for end_node in start_node.connections:
                if (end_node, start_node) not in lines_ok:
                    link = Link(nodes=[start_node, end_node])
                    self.links.append(link)
                    lines_ok.add((start_node, end_node))

    def export_to_text(self):
        diagram_datas = ""
        for function in self.functions.values():
            diagram_datas += tl.create_definition_description(function) + "\n"
        for node in self.nodes.values():
            diagram_datas += tl.create_node_description(node)
        diagram_datas += "\n"
        for group in self.groups.values():
            diagram_datas += tl.create_group_description(group) + "\n"
        links = []  # list of str : descriptions of the links
        for node in self.nodes.values():
            for connection in node.connections:
                link_description = node.name + "---" + connection.name
                if tl.reverse(link_description) not in links:
                    diagram_datas += link_description + "\n"
                    links.append(link_description)
        return diagram_datas

    def change_destination_name(self, destination, new_name):
        """Change the name attribute of the destination (a node or a function).
        If it is a node, update the diagram's node dictionnary.
        If it is a function, update the diagram's node dictionnary and changes the name of all these nodes.
        Return True if change is ok. Otherwise return False.
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
                parts = entry.name.split("<")
                if len(parts) > 0:
                    entry_prefix = parts[0]
                    entry_suffix = "<" + parts[1]
                self.change_node_name(entry, new_name + entry_suffix)
            self.change_node_name(function.output, new_name + ">")
            return True
        return False

    def change_node_name(self, node, new_name):
        """Change the name attribute of the node (destination).
        Update the diagram's node dictionary.
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
