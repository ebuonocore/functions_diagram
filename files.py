import tools as tl
import diagram as dia
from function_block import *
from node import *


def open_file(file_name):
    """ Opens and reads file_name.
    """
    with open(file_name) as f:
        file_text = f.read()
    diagram = read_state(file_text, file_name)
    return diagram


def read_state(file_text, file_name=None):
    """ Builds the function blocks and the nodes relatives
        to the different lines of the state text. Returns a diagram.
    """
    error_message = ""
    diagram = dia.Diagram()
    if file_text is None:
        error_message += "File error.\n"
        return diagram
    lines = file_text.split('\n')
    for line_number, line in enumerate(lines):
        # def : Définition of a function
        if line[0:4] == "def " and test_parentheses(line):
            new_function = function_definition(line)
            if new_function is not None:
                if new_function.name not in diagram.functions.keys():
                    diagram.add_function(new_function)
                else:
                    error_message += add_message(line_number,
                                                 line, new_function.name+" already exists.")
            else:
                error_message += add_message(line_number,
                                             line, new_function.name+" not congruant.")
        # Connections between nodes
        # Syntax: "A---B" connexion between nodes A and B
        if "---" in line:
            line = line.replace(' ', '')
            pos_sep = line.index("---")
            A = line[:pos_sep]
            B = line[pos_sep+3:]
            connection_ok = diagram.nodes_connection(A, B)
            if not connection_ok:
                error_message += add_message(line_number,
                                             line, "Connexion not done.")
        # Create a node
        # Syntax : node(A) or node(B:int, (x,y))
        if line[:4] == "node" and test_parentheses(line):
            add_node_ok = diagram.add_node(node_definition(line))
            if not add_node_ok:
                error_message += add_message(line_number,
                                             line, "Node not added.")
        # Move the function_block position
        # Syntax : funct.position(x, y)
        if ".position" in line and test_parentheses(line):
            function_block = change_parameter("position", diagram, line)
            if function_block is not None:
                function_block.fixe = True
            else:
                error_message += add_message(line_number,
                                             line, "This function doesn't exist.")
        # Change the dimension of a function_block
        # Syntax : funct.dimension(x, y)
        if ".dimension" in line and test_parentheses(line):
            function_block = change_parameter("dimension", diagram, line)
            if function_block is None:
                error_message += add_message(line_number,
                                             line, "This function doesn't exist.")
    if file_name is not None and error_message != "":
        error_file = file_name.split('.')[0] + '.err'
        f = open(error_file, "w")
        f.write(error_message)
        f.close()
    return diagram


def test_parentheses(line):
    """ Returns True if '(' is before ')' in the string.
    """
    open_parentheses = tl.index_occurrence('(', line)
    closed_parentheses = tl.index_occurrence(')', line)
    if len(open_parentheses) > 0 and len(closed_parentheses) > 0:
        return open_parentheses[0] < closed_parentheses[-1]
    else:
        return False


def function_definition(line):
    """
        Returns the new function_block object described in a def line.
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
        the output of the last one is hidden.
        def f1(a, b):  # header_color = "grey";
    """
    error = False
    labels = []
    line = line.replace(' ', '')
    if '#' in line:
        sep_index = line.index('#')
        comments_line = line[sep_index+1:]
        line = line[:sep_index]
    else:
        comments_line = None
    first_open_parentheses = tl.index_occurrence('(', line)[0]
    last_closed_parentheses = tl.index_occurrence(')', line)[-1]
    # function's name is between the "def " string and the first '('
    function_name = line[3:first_open_parentheses]
    # Abort the definition if the function_name contains '<' or '>'
    if '<' in function_name or '>' in function_name:
        return None
    function_label = function_name.split('*')[0]
    new_function = Function_block(
        name=function_name, label=function_label)
    entries = []  # list of the differents parameters of the funcion
    parameters_line = line[first_open_parentheses+1: last_closed_parentheses]
    parameters = parameters_line.split(',')
    if len(parameters) > 0:
        for index, parameter in enumerate(parameters):
            if ':' in parameter:
                entry_label, annotation = parameter.split(':')
            else:
                entry_label = parameter
                annotation = ''
            if len(entry_label) > 0:
                if entry_label not in labels:
                    entry_name = function_name + '<' + str(index)
                    new_node = Node(name=entry_name, label=entry_label,
                                    annotation=annotation, free=False)
                    entries.append(new_node)
                    labels.append(entry_label)
                else:
                    error = True
        new_function.entries = entries
    output_name = function_name + '>'
    def_output = line[last_closed_parentheses+1:]
    if '->' in def_output:
        if def_output[-1] == ':':
            output_annotation = def_output[2:-1]
        else:
            output_annotation = def_output[2:]
        if output_annotation[0] == "*":
            visible = False
            output_annotation = output_annotation[1:]
        else:
            visible = True
        new_node = Node(name=output_name,
                        annotation=output_annotation, visible=visible, free=False)
    else:
        new_node = Node(name=output_name,  free=False)
    new_function.position = [0, 0]
    new_function.output = new_node
    if comments_line is not None:
        comments = comments_line.split(';')
        for comment in comments:
            if "header_color=\"" in comment:
                start = comment.index("header_color=\"") + \
                    len("header_color=\"")
                color = comment[start:-1]
                if tl.cast_to_color(color, "hex") is not None:
                    new_function.header_color = color
                elif tl.cast_to_color(color) is not None:
                    new_function.header_color = color
    if error == False:
        return new_function
    else:
        return None


def node_definition(line):
    """ In the diagram, create the node describe in the line.
        Syntax : node(A) or node(B:float) or node(C:int, (x,y))  # fixed
    """
    if '#fixed' in line:
        fixed = True
    else:
        fixed = False
    line = line.replace(' ', '')
    first_open_parentheses = tl.index_occurrence('(', line)[0]
    last_closed_parentheses = tl.index_occurrence(')', line)[-1]
    parameters_serie = line[first_open_parentheses+1: last_closed_parentheses]
    parameters = tl.parameters_in(parameters_serie)
    pos_separation_type = tl.index_occurrence(':', parameters[0])
    if len(pos_separation_type) == 1:
        node_name = parameters[0][:pos_separation_type[0]]
        annotation = parameters[0][pos_separation_type[0]+1:]
    else:
        node_name = parameters[0]
        annotation = ''
    if len(parameters) > 1:
        position = tl.coordinates(parameters[1])
    else:
        position = [0, 0]
    label = node_name.split('*')[0]
    return Node(name=node_name, label=label, annotation=annotation, position=position, free=True, fixed=fixed)


def change_parameter(parameter, diagram, line):
    """ Changes the parameter of the function_block designated in the line.
        Parameter is 'position' or 'dimension'
        Returns de function_block object.
        Example : funct1.postion(42, 24)
    """
    line = line.replace(' ', '')
    pos_parameter = line.index('.'+parameter)
    function_name = line[:pos_parameter]
    if function_name in diagram.functions.keys():
        function = diagram.functions[function_name]
        index_parameter = pos_parameter + len(parameter) + 2
        new_parameters = tl.coordinates(line[index_parameter:-1])
        function.__dict__[parameter] = new_parameters
        return function
    else:
        return None


def add_message(line_number, line, message):
    return "in line " + str(line_number) + ": " + line + "\n    " + message + "\n"
