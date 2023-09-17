import tools as tl
import diagram as dia
from function_block import *
from node import *
import group


def open_file(file_name):
    """Open and reads file_name."""
    with open(file_name) as f:
        file_text = f.read()
    diagram = read_state(file_text, file_name)
    return diagram


def read_state(file_text, file_name=None):
    """Build the function blocks and the nodes relatives
    to the different lines of the state text. Return a diagram.
    """
    error_message = ""
    diagram = dia.Diagram()
    if file_text is None:
        error_message += "File error.\n"
        return diagram
    lines = file_text.split("\n")
    for line_number, line in enumerate(lines):
        # def : Définition of a function
        if line[0:4] == "def " and test_parentheses(line):
            new_function = function_definition(line)
            if new_function is not None:
                if new_function.name not in diagram.functions.keys():
                    diagram.add_function(new_function)
                else:
                    error_message += add_message(
                        line_number, line, new_function.name + " already exists."
                    )
            else:
                error_message += add_message(
                    line_number, line, new_function.name + " not congruant."
                )
        # Connections between nodes
        # Syntax: "A---B" connexion between nodes A and B
        if "---" in line:
            line = line.replace(" ", "")
            pos_sep = line.index("---")
            A = line[:pos_sep]
            B = line[pos_sep + 3 :]
            connection_ok = diagram.nodes_connection(A, B)
            if not connection_ok:
                error_message += add_message(line_number, line, "Connexion not done.")
        # Create a node
        # Syntax : node(A) or node(B:int, (x,y))
        if line[:4] == "node" and test_parentheses(line):
            add_node_ok = diagram.add_node(node_definition(line))
            if not add_node_ok:
                error_message += add_message(line_number, line, "Node not added.")
        # Create a group
        # Syntax : group g1(margin=20, mode="Auto", color="#a0a000", thickness=2)
        if line[:5] == "group" and test_parentheses(line):
            new_group = group_definition(line)
            if new_group is not None:
                diagram.add_group(new_group)
            else:
                error_message += add_message(line_number, line, "Group not added.")
        # Move the function_block position
        # Syntax : funct.position(x, y)
        if ".position" in line and test_parentheses(line):
            element = change_parameter("position", diagram, line)
            if element is None:
                error_message += add_message(
                    line_number,
                    line,
                    "This element doesn't exist. Cannot change the position. ",
                )
        # Change the dimension of a function_block
        # Syntax : funct.dimension(x, y)
        if ".dimension" in line and test_parentheses(line):
            function_block = change_parameter("dimension", diagram, line)
            if function_block is None:
                error_message += add_message(
                    line_number,
                    line,
                    "This element doesn't exist. Cannot change the dimension.",
                )
        # Set element's mode on Fixed or Auto
        # Syntax : funct.fixed(1) to fix funct, funct.fixed(0) to set funct on Auto mode
        if ".fixed" in line and test_parentheses(line):
            element = change_parameter("fixed", diagram, line)
            if element is None:
                error_message += add_message(
                    line_number, line, "This node, function or group doesn't exist."
                )
        if ".add_function" in line and test_parentheses(line):
            method_index = line.index(".add_function")
            first_open_parentheses = tl.index_occurrence("(", line)[0]
            last_closed_parentheses = tl.index_occurrence(")", line)[-1]
            group_name = line[:method_index]
            if group_name in diagram.groups.keys():
                group = diagram.groups[group_name]
                parameters_serie = line[
                    first_open_parentheses + 1 : last_closed_parentheses
                ]
                parameters = tl.parameters_in(parameters_serie)
                for parameter in parameters:
                    if parameter in diagram.functions.keys():
                        new_function = diagram.functions[parameter]
                        group.add_function(new_function)
                    else:
                        error_message += add_message(
                            line_number, line, parameter + " doesn't exist."
                        )

        if ".add_node" in line and test_parentheses(line):
            method_index = line.index(".add_node")
            first_open_parentheses = tl.index_occurrence("(", line)[0]
            last_closed_parentheses = tl.index_occurrence(")", line)[-1]
            group_name = line[:method_index]
            if group_name in diagram.groups.keys():
                group = diagram.groups[group_name]
                parameters_serie = line[
                    first_open_parentheses + 1 : last_closed_parentheses
                ]
                parameters = tl.parameters_in(parameters_serie)
                for parameter in parameters:
                    if parameter in diagram.nodes.keys():
                        new_node = diagram.nodes[parameter]
                        group.add_node(new_node)
                    else:
                        error_message += add_message(
                            line_number, line, parameter + " doesn't exist."
                        )

    if file_name is not None and error_message != "":
        error_file = file_name.split(".")[0] + ".err"
        f = open(error_file, "w")
        f.write(error_message)
        f.close()
    return diagram


def test_parentheses(line):
    """Return True if '(' is before ')' in the string."""
    open_parentheses = tl.index_occurrence("(", line)
    closed_parentheses = tl.index_occurrence(")", line)
    if len(open_parentheses) > 0 and len(closed_parentheses) > 0:
        return open_parentheses[0] < closed_parentheses[-1]
    else:
        return False


def function_definition(line):
    """
    Return  the new function_block object described in a def line.
    line starts by "def " string. It includes '(' and ')' after the function's name.
    the function label is identical to the function name except if it contains the '*' character.
    In this case, the characters from '*' are ignored in the label.
    The definition line can end with ':', but this is optional.
    Comments at the end of the line after '#' allow to specify parameters such as the header color.
    Comments are separated by semicolons.
    Examples :
    def f1(a: int, b: bool):
    def f1*(a: int, b: bool)->str
    def f1*1(a: int, b: bool)->*
    These lines define three different functions with the same label (f1).
    the output of the last one is hidden. And the function is on the fixed mode
    def f1(a, b):  # header_color = "grey"; fixed
    """
    error = False
    labels = []
    line = line.replace(" ", "")
    if "#" in line:
        sep_index = line.index("#")
        comments_line = line[sep_index + 1 :]
        line = line[:sep_index]
    else:
        comments_line = None
    first_open_parentheses = tl.index_occurrence("(", line)[0]
    last_closed_parentheses = tl.index_occurrence(")", line)[-1]
    # function's name is between the "def " string and the first '('
    function_name = line[3:first_open_parentheses]
    # Abort the definition if the function_name contains '<' or '>'
    if "<" in function_name or ">" in function_name:
        return None
    function_label = function_name.split("*")[0]
    new_function = Function_block(name=function_name, label=function_label)
    entries = []  # list of the differents parameters of the funcion
    parameters_line = line[first_open_parentheses + 1 : last_closed_parentheses]
    parameters = tl.split_unembed(parameters_line, ",")
    if len(parameters) > 0:
        for index, parameter in enumerate(parameters):
            if ":" in parameter:
                entry_label, annotation = parameter.split(":")
            else:
                entry_label = parameter
                annotation = ""
            if len(entry_label) > 0:
                if entry_label not in labels:
                    entry_name = function_name + "<" + str(index)
                    new_node = Node(
                        name=entry_name,
                        label=entry_label,
                        annotation=annotation,
                        free=False,
                    )
                    entries.append(new_node)
                    labels.append(entry_label)
                else:
                    error = True
        new_function.entries = entries
    output_name = function_name + ">"
    def_output = line[last_closed_parentheses + 1 :]
    if "->" in def_output:
        if def_output[-1] == ":":
            output_annotation = def_output[2:-1]
        else:
            output_annotation = def_output[2:]
        if output_annotation[0] == "*":
            visible = False
            output_annotation = output_annotation[1:]
        else:
            visible = True
        new_node = Node(
            name=output_name, annotation=output_annotation, visible=visible, free=False
        )
    else:
        new_node = Node(name=output_name, free=False)
    new_function.position = [0, 0]
    new_function.output = new_node
    new_function.fixed = False
    if comments_line is not None:
        comments = comments_line.split(";")
        for comment in comments:
            if 'header_color="' in comment:
                start = comment.index('header_color="') + len('header_color="')
                color = comment[start:-1]
                if tl.cast_to_color(color, "hex") is not None:
                    new_function.header_color = color
                elif tl.cast_to_color(color) is not None:
                    new_function.header_color = color
            if "fixed" in comment:
                new_function.fixed = True
    if error == False:
        return new_function
    else:
        return None


def node_definition(line):
    """Return the new node describe in the line.
    Syntax : node(A) or node(B:float) or node(C:int, (x,y))  # fixed
    """
    line = line.replace(" ", "")
    if "#fixed" in line:
        fixed = True
    else:
        fixed = False
    # line = line.replace('"', "'")
    first_open_parentheses = tl.index_occurrence("(", line)[0]
    last_closed_parentheses = tl.index_occurrence(")", line)[-1]
    parameters_serie = line[first_open_parentheses + 1 : last_closed_parentheses]
    parameters = tl.parameters_in(parameters_serie)
    pos_separation_type = tl.index_occurrence(":", parameters[0])
    if len(pos_separation_type) == 1:
        node_name = parameters[0][: pos_separation_type[0]]
        annotation = parameters[0][pos_separation_type[0] + 1 :]
    else:
        node_name = parameters[0]
        annotation = ""
    label = node_name.split("*")[0]
    if len(parameters) > 1:
        position = tl.coordinates(parameters[1])
    else:
        position = [0, 0]
    new_node = Node(
        name=node_name,
        label=label,
        annotation=annotation,
        position=position,
        free=True,
        fixed=fixed,
    )
    for parameter in parameters[2:]:
        if "justify" in parameter:
            if "=" in parameter:
                pos_equal = parameter.index("=")
                value = parameter[pos_equal + 1 :]
                if value in ['"left"', '"right"', '"center"', '"separator"']:
                    new_node.justify = value[1:-1]
    return new_node


def group_definition(line: str) -> group.Group:
    """Return the group object described in the line.
    Example with group g1 of position (150, 200) and dimensions (250, 250) containing functions f1, f1* and nodes n1, n2 and n3. Margin 20 pixels. Auto mode.

    group g1(margin=20, mode="Auto", color="#a0a000", thickness=2)
    g1.add_functions(f1, f1*)
    g1.add_nodes(n1, n2, n3)
    g1.position(150, 200)
    g1.dimension(250, 250)

    ** Minimum settings **
    By default, if the group contains elements (functions or nodes) the mode is "Auto", otherwise it is "Fixed". In this case, the position and dimension entered are used.
    If the margin, color and thickness parameters are not set, the default values are those in the preferences.

    group g2()

    g2 cannot be created because it does not have enough parameters.

    group g3()
    g3.position(100, 200)
    g3.dimension(300, 300)

    g3 can be created with preferences values in "Fixed" mode.

    group g4()
    g4.add_functions(f1, f2)

    g4 can be created with preferences values in "Auto" mode if f1 and/or f2 exist(s).
    """
    line = line.replace(" ", "")
    line = line.replace('"', "'")
    first_open_parentheses = tl.index_occurrence("(", line)[0]
    last_closed_parentheses = tl.index_occurrence(")", line)[-1]
    group_name = line[5:first_open_parentheses]
    group_label = group_name.split("*")[0]
    parameters_serie = line[first_open_parentheses + 1 : last_closed_parentheses]
    parameters = tl.parameters_in(parameters_serie)
    new_group = group.Group(name=group_name, label=group_label)
    if len(parameters) > 1:
        for parameter in parameters:
            if "=" in parameter:
                pos_equal = parameter.index("=")
                parameter_name = parameter[:pos_equal]
                value = parameter[pos_equal + 1 :]
                if parameter_name == "margin":
                    new_group.margin = int(value)
                elif parameter_name == "mode":
                    new_group.fixed = value == "Fixed"
                elif parameter_name == "color":
                    new_group.color = value.replace("'", "")
                elif parameter_name == "thickness":
                    new_group.thickness = int(value)
    return new_group


def change_parameter(parameter, diagram, line):
    """Change the parameter of the function_block or the group designated in the line.
    parameter is 'position' or 'dimension'
    Return the function_block object/group.
    Example : funct1.postion(42, 24)
    """
    line = line.replace(" ", "")
    pos_parameter = line.index("." + parameter)
    element_name = line[:pos_parameter]
    if element_name in diagram.functions.keys():
        element = diagram.functions[element_name]
    elif element_name in diagram.groups.keys():
        element = diagram.groups[element_name]
    elif element_name in diagram.nodes.keys():
        element = diagram.nodes[element_name]
    else:
        return None
    index_parameter = pos_parameter + len(parameter) + 2
    new_parameters = tl.coordinates(line[index_parameter:-1])
    element.__dict__[parameter] = new_parameters
    return element


def add_message(line_number, line, message):
    return "in line " + str(line_number) + ": " + line + "\n    " + message + "\n"
