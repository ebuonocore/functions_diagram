from tkinter import filedialog as fd
from tkinter import font as tkfont
import tkinter as tki
from PIL import Image, ImageTk
import json
import tools as tl
from diagram import *
from node import *
from files import *
from memory import *
from math import pi, cos, sin
from os import path
from window_edition import *
from window_export_image import *
from PIL import Image

COLOR_OUTLINE = "#FFFF00"


def message(message, destination=None):
    """ Affiche le message dans la console en attendant de créer les zones de texte sur Tkinter
    """
    if destination is None:
        print(message)
    else:
        destination.set(message)


class Window:

    def __init__(self, diagram=None):
        self.tk = tki.Tk()
        self.tk.title('Functions Diagram')
        if diagram is None:
            self.diagram = Diagram()
        else:
            self.diagram = diagram
        # Configuration
        self.preferences = self.load_preferences()
        police = self.preferences["police"]
        title_size = self.preferences["title_size"]
        text_size = self.preferences["text_size"]
        self.title_size = tkfont.Font(
            family=police, size=title_size, weight="bold")
        self.text_size = tkfont.Font(
            family=police, size=text_size, weight="normal")
        self.title_char_width, self.title_char_height = tl.character_dimensions(police,
                                                                                title_size)
        self.text_char_width, self.text_char_height = tl.character_dimensions(police,
                                                                              text_size)
        # Initialisation
        self.state = 1
        self.memory = Memory(50, self.diagram.export_to_text())
        self.MARGIN = 10
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.screen_dimensions()
        self.MARGIN_DOWN = 10
        self.MARGIN_UP = 10
        self.MENU_HEIGHT = 80
        self.smooth_lines = True
        self.window_edition = None
        self.can = tki.Canvas(self.tk, width=self.SCREEN_WIDTH,
                              height=self.SCREEN_HEIGHT, bg='white')
        self.menu = tki.Canvas(self.tk, width=self.SCREEN_WIDTH, height=self.MENU_HEIGHT,
                               bg='#F0F0F0')
        self.menu_label = tki.Label(self.menu)
        self.menu_label.pack(padx=1, pady=1, fill=tki.X, side=tki.LEFT)
        self.marge = tki.Label(self.menu, width=1, bg='#F0F0F0')
        self.marge.pack(side=tki.LEFT)
        self.text_message = tki.StringVar()
        self.text_message.set('\n')
        self.message = tki.Label(
            self.menu, textvariable=self.text_message, bg='#F0F0F0', justify=tki.LEFT)
        self.message.pack(side=tki.LEFT)
        self.images = self.build_images_bank()
        self.buttons = {}
        self.add_buttons()
        self.menu.pack(fill=tki.X)
        self.can.pack()
        self.tk.update()
        self.WIDTH, self.HEIGHT = self.canvas_dimensions()
        self.destination = None
        self.origin = None
        self.auto_resize_blocks()
        self.update_positions()
        message("Function_diagram v1.0", self.text_message)
        self.edition_in_progress = False
        self.engine()  # Starts state management

    def load_preferences(self):
        """ Charge les informations stockées dans le fichiers préférences.json
            et met à jour les attributs du systeme et du paquet
        """
        with open('preferences.json', 'r') as fichier:
            return json.load(fichier)

    def screen_dimensions(self):
        WIDTH = self.tk.winfo_screenwidth()
        HEIGHT = self.tk.winfo_screenheight()
        return WIDTH, HEIGHT

    def canvas_dimensions(self):
        WIDTH = self.tk.winfo_width()
        HEIGHT = self.tk.winfo_height() - self.MENU_HEIGHT
        return WIDTH, HEIGHT

    def auto_resize_blocks(self):
        """ Parcourt tous les blocs_fonctions et redimensionne automatiquement ceux qui n'ont pas de
            dimensions imposées (à None).
            Tiens compte de la taille de la police.
            hauteur : fonction du nombre d'entrées + 1
            largeur : fonction du nombre de caractères max de la plus longue entrée ou du titre
        """
        for function in self.diagram.functions.values():
            if function.dimension == [] or not function.fixed:
                if len(function.entries) > 0:
                    longest_name = max(
                        [len(entry.label)+len(entry.annotation) for entry in function.entries])
                    # Ajout de 2 caractères ': '
                    max_width = (longest_name+2) * self.text_char_width
                else:
                    max_width = 0
                max_width = max(max_width,
                                len(function.label)*self.title_char_width) + 2*self.MARGIN
                max_height = max(len(function.entries),
                                 1) * self.text_char_height + 2*self.MARGIN
                function.dimension = (max_width, max_height)

    def position_functions_nodes(self):
        """ Positions the nodes linked to the functions.
        """
        # Place les positions des noeuds des fonctions
        for function in self.diagram.functions.values():
            # Points de repère : Cadre du corps
            if function.position is not None:
                x, y = function.position
                function_width, function_height = function.dimension
                x_entry = x + self.MARGIN
                y_entry = y + self.title_char_height + self.MARGIN

                for entry in function.entries:
                    # Met à jour, les positions des points du bloc
                    entry.position = [x_entry-self.MARGIN,
                                      y_entry + self.text_char_height//2]
                    entry.free = False
                    y_entry += self.text_char_height
                # Point de sortie du bloc
                function.output.position = [x+function_width,
                                            y+self.title_char_height+function_height//2]
                function.output.free = False

    def update_positions(self):
        """ Les positions relatives des fonctions et des points sont déterminées par leur étage.
            Sauf si les positions sont fixées.
            Etage 0 : Feuilles du graphe orienté décrit par self.matrice.
            Les fonctions se répartissent graphiquement entre self.MARGIN_DOWN et self.WIDTH - self.MARGIN_UP
            Les points libres (non-associés à des fonctions) se situent sur les étages intermédiaires.
        """
        self.diagram.update_zones()
        self.diagram.update_floors()
        # Recherche l'étage maximum
        floor_max = len(self.diagram.floors)
        # Impose l'abscisse des blocs_fonctions non fixés.
        nb_intervals = floor_max + 1
        interval_width = (self.WIDTH - 2*self.MARGIN) // nb_intervals
        free_height = (self.HEIGHT - self.MARGIN_UP - self.MARGIN_DOWN)
        for function in self.diagram.functions.values():
            floor = function.floor
            if function.fixed == False:
                function.position[0] = (self.MARGIN
                                        + (floor_max - floor) * interval_width
                                        - function.dimension[0]//2)
                rank = tl.function_rank(function, self.diagram.floors[floor])
                ratio = (rank+1) / (len(self.diagram.floors[floor])+1)
                function.position[1] = round(
                    free_height * ratio) + self.MARGIN_UP - function.dimension[1]//2

        # Positions the nodes linked to the functions
        self.position_functions_nodes()

        # Calcul la position des noeud libres en fonction des positions des noeuds non-libres connexes.
        for node in self.diagram.nodes.values():
            if node.free and not node.fixed:
                output_abscissas = None
                output_ordinate = None
                max_abscissas = None
                ordinates = []
                for connected_node in node.connections:
                    # Ce point est une entrée de fonction
                    if '<' in connected_node.name:
                        ordinates.append(connected_node.position[1])
                        if max_abscissas is None:
                            max_abscissas = connected_node.position[0]
                        elif connected_node.position[0] < max_abscissas:
                            max_abscissas = connected_node.position[0]
                    # Ce point est une sortie de fonction
                    elif '>' in connected_node.name or '<' in connected_node.name:
                        output_abscissas = connected_node.position[0]
                        output_ordinate = connected_node.position[1]
                if output_abscissas is None:
                    output_abscissas = self.MARGIN + interval_width//2
                if max_abscissas is None:
                    max_abscissas = self.WIDTH - \
                        (self.MARGIN + interval_width//2)
                node.position[0] = (output_abscissas + max_abscissas) // 2
                if len(ordinates) == 0:
                    node.position[1] = self.MARGIN_UP + free_height//2
                elif output_ordinate is not None:
                    node.position[1] = output_ordinate
                else:
                    node.position[1] = sum(ordinates) / len(ordinates)

    def draw(self):
        """ Met à jour l'affichage du systeme dans la fenêtre Tkinter
        """
        # Efface tous les objets du canevas avant de les recréer
        self.can.delete("all")
        # Dessine tous les éléments du système
        self.draw_function()
        self.draw_nodes()
        self.draw_lines()

    def draw_nodes(self):
        """ Dessine des disque pour les points isolés et des flèches pour les points liés à des blocs.
        """
        police = self.preferences["police"]
        text_size = self.preferences["text_size"]

        font_texte = tkfont.Font(
            family=police, size=text_size, weight="normal")
        color = self.preferences["line_color"]
        text_color = self.preferences["text_color"]
        d = self.preferences["text_size"] // 2
        for node_name, node in self.diagram.nodes.items():
            if node.position != [None, None] and node.visible:
                x, y = node.position
                if node.free:
                    self.can.create_oval(x-d, y-d, x+d, y+d, fill=color)
                    self.print_label(x, y-self.MARGIN,
                                     node.label, node.annotation, 's')
                else:
                    self.draw_triangle(x, y, 0)
                    if '>' in node.name:
                        self.print_label(x, y-self.MARGIN,
                                         node.label, node.annotation, 'w')
                    else:
                        self.print_label(x+2, y, node.label,
                                         node.annotation, 'w')

    def draw_triangle(self, x, y, orientation=0, color=None, d=None):
        """ Dessine un triangle isocèle. Origine = H, intersection de la hauteur principale et de la base.
            Orientation : 0 = Est, 1 = Sud, 2 = Ouest, 3 = Nord
        """
        if color is None:
            color = self.preferences["line_color"]
        if d is None:
            d = self.preferences["text_size"] // 2
        perimeter = [[x-2*d, y-d, x, y, x-2*d, y+d],
                     [x-d, y+2*d, x, y, x+d, y+2*d],
                     [x+2*d, y-d, x, y, x+2*d, y+d],
                     [x-d, y-2*d, x, y, x+d, y-2*d]]
        self.can.create_polygon(perimeter[orientation], fill=color)

    def print_label(self, x, y, label, annotation, ancre='nw'):
        """ Écrit le label et si besoin l'annotation de type séparé par :
        """
        police = self.preferences["police"]
        text_size = self.preferences["text_size"]
        font = tkfont.Font(family=police, size=text_size, weight="normal")
        text_color = self.preferences["text_color"]
        type_color = self.preferences["type_color"]
        # Écrit le label
        if len(annotation) > 0 and len(label) > 0:
            label += ': '
        self.can.create_text(x, y, text=label, font=font,
                             anchor=ancre, fill=text_color)
        if len(annotation) > 0:
            offset = tkfont.Font(size=text_size, family=police).measure(label)
            x_type = x + offset
            self.can.create_text(x_type, y, text=annotation, font=font,
                                 anchor=ancre, fill=type_color)

    def draw_function(self):
        """ Dessin le bloc_fonction : Cadres de l'entête, du corps.
            Met à jour les positions des points du bloc : Entrées et sortie
        """
        police = self.preferences["police"]
        title_size = self.preferences["title_size"]
        text_size = self.preferences["text_size"]
        text_color = self.preferences["text_color"]
        font_titre = tkfont.Font(
            family=police, size=title_size, weight="bold")
        font_texte = tkfont.Font(
            family=police, size=text_size, weight="normal")
        border_color = self.preferences["borders_default_color"]
        title_background_color = self.preferences["title_background_color"]
        main_background_color = self.preferences["main_background_color"]
        for function in self.diagram.functions.values():
            # Dessin du cadre du corps
            if function.position is not None:
                x, y = function.position
                function_width, function_height = function.dimension
                if function.header_color is None:
                    header_color = title_background_color
                else:
                    header_color = function.header_color
                # Dessin du cadre du nom de la fonction
                self.can.create_rectangle(x, y, x+function_width, y+self.title_char_height,
                                          outline=border_color, fill=header_color)

                # Dessin du cadre du corps de la fonction
                self.can.create_rectangle(x, y+self.title_char_height, x+function_width,
                                          y+self.title_char_height+function_height,
                                          outline=border_color, fill=main_background_color)

                # Ecriture du nom de la fonction
                x_titre = x + function_width // 2
                y_titre = y + self.title_char_height // 2
                texte = function.label
                self.can.create_text(x_titre, y_titre, text=texte, font=font_titre,
                                     anchor='center', fill=text_color)

    def draw_lines(self):
        """ Dessine les liaisons entre les points : Traits verticaux ou horizontaux.
        """
        thikness = self.preferences["line_thikness"]
        self.diagram.update_links()
        lines_ok = set()  # Ensemble de tuples (point_de_depart, point_d_arrivee)
        for link in self.diagram.links:
            x_start, y_start = link.points[0]
            x_first, y_first = link.points[1]
            x_middle, y_middle = link.points[2]
            x_last, y_last = link.points[3]
            x_end, y_end = link.points[4]
            if self.smooth_lines == True:
                self.can.create_line((x_start, y_start),
                                     (x_first, y_start),
                                     (x_middle, y_middle),
                                     (x_last, y_end),
                                     (x_end, y_end),
                                     smooth="true")
            else:
                self.can.create_line((x_start, y_start),
                                     (x_middle, y_start),
                                     width=thikness)
                self.can.create_line((x_middle, y_start),
                                     (x_middle, y_end),
                                     width=thikness)
                self.can.create_line((x_middle, y_end),
                                     (x_end, y_end),
                                     width=thikness)

    def draw_destination_outine(self, color=COLOR_OUTLINE):
        if type(self.destination) == Link:
            d = 2 * self.preferences["text_size"] // 3
            x, y = self.destination.position
            self.can.create_rectangle(x-2, y-2, x+2, y+2, width=2,
                                      outline=color)
        if type(self.destination) == Node:
            d = 2 * self.preferences["text_size"] // 3
            x, y = self.destination.position
            if self.destination.free:
                self.can.create_oval(x-d, y-d, x+d, y+d, fill=color)
            else:
                scale = self.preferences["text_size"] // 3
                self.draw_triangle(
                    x-scale//2, y, 0, color, scale)
        elif type(self.destination) == Function_block:
            x, y = self.destination.position
            width, height = self.destination.dimension
            self.can.create_rectangle(x-2, y-2, x+width+2, y+self.title_char_height+height+2, width=2,
                                      outline=color)

    def import_image(self, banque, name):
        """ Importe l'image en fonction du nom passé en paramètre
            et l'associe à une clef du dictionnaire banque
        """
        file = 'images/' + name + '.png'
        image = Image.open(file)
        banque[name] = ImageTk.PhotoImage(image)

    def build_images_bank(self):
        banque = dict()
        self.import_image(banque, 'new')
        self.import_image(banque, 'open')
        self.import_image(banque, 'save')
        self.import_image(banque, 'move')
        self.import_image(banque, 'add_function')
        self.import_image(banque, 'add_node')
        self.import_image(banque, 'add_link')
        self.import_image(banque, 'edit')
        self.import_image(banque, 'erase')
        self.import_image(banque, 'auto')
        self.import_image(banque, 'undo')
        self.import_image(banque, 'redo')
        self.import_image(banque, 'export')
        self.import_image(banque, 'configuration')
        self.import_image(banque, 'information')
        return banque

    def create_button(self, name, command):
        self.buttons[name] = tki.Button(self.menu_label,
                                        image=self.images[name],
                                        command=command)

    def add_buttons(self):
        """ Ajoute les boutons
        """
        self.create_button('new', self.cmd_new)  # state:1
        self.create_button('open', self.cmd_open)  # state:1
        self.create_button('save', self.cmd_save)  # state:1
        self.create_button('export', self.cmd_export)
        self.create_button('move', self.cmd_move)  # state:2, 3, 4
        self.create_button('add_function', self.cmd_add_function)
        self.create_button('add_node', self.cmd_add_node)
        self.create_button('add_link', self.cmd_add_link)
        self.create_button('edit', self.cmd_edit)
        self.create_button('erase', self.cmd_erase)
        self.create_button('undo', self.cmd_undo)
        self.create_button('redo', self.cmd_redo)
        self.create_button('auto', self.cmd_auto)
        self.create_button('configuration', self.cmd_configuration)
        self.create_button('information', self.cmd_information)
        for button in self.buttons.values():
            button.pack(side=tki.LEFT)

    def lift_window(self, child_window):
        """ Moves the parent window and the child_window in the stack.
        """
        child_window.lift()
        child_window.focus_force()
        child_window.update()

    def cmd_new(self):
        """ Vide la liste des points et des fonctions
        """
        message('New diagram.', self.text_message)
        self.state = 1
        self.diagram = Diagram()
        self.draw()

    def cmd_open(self):
        """ Ouvre le fichier JSON sélectionné et reconstruit l'instance de systeme.
            Permet de choisir le format JSON ou le TXT
            Renvoie True si la procédure aboutit sinon False
        """
        self.can.config(cursor="arrow")
        message('Open file.', self.text_message)
        self.state = 1
        selected_file = fd.askopenfilename(title='Open')
        if selected_file == '':
            message('Canceled opening.', self.text_message)
            return False
        self.diagram = open_file(selected_file)
        file_name = selected_file
        if '/' in file_name:
            file_name = file_name.split('/')[-1]
        if '\\' in file_name:
            file_name = file_name.split('\\')[-1]
        self.auto_resize_blocks()
        self.position_functions_nodes()
        self.draw()
        message('File ' + file_name + ' opened.', self.text_message)
        self.memory.add(self.diagram.export_to_text())
        return True

    def cmd_save(self):
        """ Save the configuration of the diagram as a file.
        """
        self.can.config(cursor="arrow")
        message('Save diagram.', self.text_message)
        self.state = 1
        selected_file = fd.asksaveasfile(title='Save')
        diagram_datas = self.diagram.export_to_text()
        try:
            selected_file.write(diagram_datas)
            message('Diagram saved.', self.text_message)
            selected_file.close()
            return True
        except:
            message('Backup canceled.', self.text_message)
            return False

    def cmd_add_function(self):
        """
        """
        if self.edition_in_progress == False:
            message('Create a new function.', self.text_message)
            previous_names = [
                function for function in self.diagram.functions.keys()]
            name = tl.new_label(previous_names)
            label = name.split('*')[0]
            output = Node(name=name+'>')
            new_function = Function_block(
                name=name, label=label, position=[100, 100], dimension=[20, 20], output=output)
            self.diagram.add_function(new_function)
            self.destination = new_function
            self.edit(self.destination)
            self.draw()
        else:
            message('Edition already open.', self.text_message)
            self.lift_window(self.window_edition.window)

    def cmd_add_node(self):
        """
        """
        if self.edition_in_progress == False:
            message('Create a new node.', self.text_message)
            previous_names = [
                node for node in self.diagram.nodes.keys()]
            name = tl.new_label(previous_names)
            new_node = Node(name=name, label=name,
                            free=True, position=[100, 100])
            self.diagram.add_node(new_node)
            self.destination = new_node
            self.edit(self.destination)
            self.draw()
        else:
            message('Edition already open.', self.text_message)
            self.lift_window(self.window_edition.window)

    def cmd_add_link(self):
        """
        """
        message('Select the first node.', self.text_message)
        self.can.config(cursor="plus")
        self.state = 6

    def cmd_move(self):
        """
        """
        message('Select the free node or the function to move.', self.text_message)
        self.can.config(cursor="fleur")
        self.state = 2

    def cmd_edit(self):
        """
        """
        if self.edition_in_progress == False:
            message('Select the free node or the function to edit.',
                    self.text_message)
            self.can.config(cursor="pencil")
            self.state = 5
        else:
            message('Edition already open.', self.text_message)
            self.lift_window(self.window_edition.window)

    def edit(self, destination):
        """
        """
        self.memory.add(self.diagram.export_to_text())
        self.edition_in_progress = True
        self.window_edition = Window_edition(self, self.diagram, destination)
        self.lift_window(self.window_edition.window)

    def cmd_erase(self):
        """
        """
        message('Select the free node or the function to erase.',
                self.text_message)
        self.can.config(cursor="pirate")
        self.state = 4

    def erase(self, destination):
        """ Delete the destination object from the functions or the nodes dictionary.
        """
        if type(destination) == Node:
            node_to_delete = tl.key_of(self.diagram.nodes, destination)
            self.diagram.delete_node(node_to_delete)
        elif type(destination) == Link:
            self.diagram.disconnect_nodes(destination)
        elif type(destination) == Function_block:
            function_to_delete = tl.key_of(
                self.diagram.functions, destination)
            self.diagram.delete_function(function_to_delete)

    def cmd_export(self):
        """
        """
        message('Export diagram to image.', self.text_message)
        self.state = 1
        Window_export_image(self, self.diagram)

    def cmd_auto(self):
        """ Updates automaticly the positions of functions and nodes.
        """
        self.state = 1
        self.auto_resize_blocks()
        self.update_positions()
        self.draw()

    def cmd_undo(self):
        """
        """
        state_description = self.memory.undo()
        if state_description is not None:
            self.diagram = read_state(state_description)
            self.auto_resize_blocks()
            self.position_functions_nodes()
            message("Undo: "+str(self.memory.pointer)+"/" +
                    str(self.memory.size), self.text_message)
            self.draw()

    def cmd_redo(self):
        """
        """
        state_description = self.memory.redo()
        if state_description is not None:
            self.diagram = read_state(state_description)
            self.auto_resize_blocks()
            self.position_functions_nodes()
            message("Redo: "+str(self.memory.pointer)+"/" +
                    str(self.memory.size), self.text_message)
            self.draw()

    def cmd_configuration(self):
        """
        """
        pass

    def cmd_information(self):
        """
        """
        pass

    def left_click(self, event):
        Xpix = event.x
        Ypix = event.y
        if self.state == 2:  # Target to move selected
            self.state = 3  # Destination selection
        elif self.state == 3:  # Destination selected
            self.state = 2  # Choose another target to move
            self.memory.add(self.diagram.export_to_text())
        elif self.state == 4:  # Destination to erase selected
            self.erase(self.destination)
            self.memory.add(self.diagram.export_to_text())
            self.draw()
        elif self.state == 5:  # Destination to edit selected
            self.edit(self.destination)
            message('', self.text_message)
            self.draw()
            self.state = 1
        elif self.state == 6:  # Add link : Source selected
            self.origin = self.destination
            if self.origin is not None:
                message('Select the node to connect.',
                        self.text_message)
                self.state = 7  # Destination selection
        elif self.state == 7:  # Destination selected
            self.diagram.update_zones()
            compliant_nodes = False
            if self.origin.zone == self.destination.zone:
                compliant_nodes = True
            if self.origin.zone == -1 or self.destination.zone == -1:
                compliant_nodes = True
            # Manque le test si les zones permettent un rebouclage E/S d'une fonction
            if compliant_nodes:
                message('Nodes connected. Select another origin.',
                        self.text_message)
                self.diagram.nodes_connection(
                    self.origin.name, self.destination.name)
            else:
                message('Forbiden link: Output shortcut.'+str(self.origin.zone),
                        self.text_message)
            self.draw()
            self.state = 6  # Choose another target to link
            self.memory.add(self.diagram.export_to_text())
        else:
            self.state = 1  # Return to basic state

    def right_click(self, event):
        message('', self.text_message)
        self.state = 1
        self.draw()

    def mouse_movement(self, event):
        Xpix = event.x
        Ypix = event.y

    def fermer_fenêtre(self):
        self.tk.quit()
        self.tk.destroy()

    def engine(self):
        """ State management :
                1 - Basic state
                2 - Move object : Select the origin
                3 - Move object : Select destination
                4 - Erase : Select object to erase
                5 - Edit : Select object to edit
                6 - Add link : Select the origin
                7 - Add link : Select destination
        """
        if self.state == 1:  # Basic state
            self.can.config(cursor="arrow")
        if self.state == 2:  # Move object: Select the origin
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination = tl.nearest_objet(
                (mouse_x, mouse_y), self.diagram)
            self.draw()
            self.draw_destination_outine()
        elif self.state == 3 and self.destination is not None:  # Move to destination
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination.position = [mouse_x, mouse_y]
            self.position_functions_nodes()
            self.draw()
        elif self.state == 4:  # Select object to erase
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination = tl.nearest_objet(
                (mouse_x, mouse_y), self.diagram, target_types="erasable")
            self.draw()
            self.draw_destination_outine('red')
        elif self.state == 5:  # Select object to edit
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination = tl.nearest_objet(
                (mouse_x, mouse_y), self.diagram)
            self.draw()
            self.draw_destination_outine('green')
        elif self.state == 6:  # Add link : Origin selected
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination, distance = tl.nearest(
                (mouse_x, mouse_y), self.diagram.nodes.values())
            self.draw()
            self.draw_destination_outine()
        elif self.state == 7 and self.origin is not None:  # Add link : Destination selected
            mouse_x, mouse_y = tl.pointer_position(self.can)
            self.destination, distance = tl.nearest(
                (mouse_x, mouse_y), self.diagram.nodes.values())
            self.draw()
            self.draw_destination_outine()

        self.tk.after(10, self.engine)  # Restarts state management
