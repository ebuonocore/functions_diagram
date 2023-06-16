from PIL import Image, ImageTk
import tkinter as tki
from diagram import *
import tools as tl


class Window_information():
    def __init__(self, parent_window, images):
        self.parent = parent_window
        self.tk = parent_window.tk
        self.window = tki.Toplevel(self.tk)
        self.window.title('Informations')
        self.window.resizable(height=True, width=True)
        self.window.bind("<Return>", lambda event: self.cmd_commit())
        self.parent.tk.update_idletasks()
        self.MARGE = 4
        rootx = self.parent.can.winfo_rootx()
        rooty = self.parent.can.winfo_rooty()
        can_height = self.parent.can.winfo_height()
        win_width, win_height = self.window_dimension(
            self.parent.tk.geometry())
        self.window.geometry(
            "400x{}+{}+{}".format(can_height-2*self.MARGE-40, rootx+win_width-400-self.MARGE, rooty+self.MARGE))
        self.images = images
        self.show_informations()

    def show_informations(self):
        help_grid = []
        frame = tl.ScrollableFrame(self.window)
        help_grid.append(('new', "Create a new file"))
        help_grid.append(('open', "Open a file"))
        help_grid.append(('save', "Save file"))
        help_grid.append(('export', "Export diagram to image (.SVG)"))
        help_grid.append(('move', "Move function or node"))
        help_grid.append(('add_function', "Add a function"))
        help_grid.append(('add_node', "Add a free node"))
        help_grid.append(('add_link', "Connect two nodes"))
        help_grid.append(('edit', "Edit element (node or function)"))
        help_grid.append(
            ('erase', "Delete element (node, function or connexion)"))
        help_grid.append(('undo', "Undo"))
        help_grid.append(('redo', "Redo"))
        help_grid.append(
            ('auto', "Place automaticly the objects on the screen"))
        help_grid.append(('configuration', "Edit settings"))
        help_grid.append(('information', "Show informations"))

        for name, description in help_grid:
            line = tki.Frame(frame.scrollable_frame)
            lbl_img = tki.Label(line, image=self.images[name])
            lbl_txt = tki.Label(line, text=description, justify=tki.LEFT,
                                anchor='w')
            lbl_img.pack(side=tki.LEFT, fill='both')
            lbl_txt.pack(fill='both')
            line.pack(fill='both', expand=False)
        title = tki.Label(frame.scrollable_frame,
                          text="function_diagram by Eric Buonocore\n2023",
                          anchor='w')
        title.pack(side=tki.BOTTOM)
        image_licence = Image.open('images/licence-by-nc-sa.png')
        image_licence_tk = ImageTk.PhotoImage(image_licence)
        label_image = tki.Label(frame.scrollable_frame,
                                image=image_licence_tk)
        # Keep a reference to avoid having it erased by the garbage-collector
        label_image.image = image_licence_tk
        label_image.pack(side=tki.BOTTOM)
        frame.pack(fill=tki.BOTH, expand=True)

    def cmd_commit(self):
        self.window.destroy()

    def window_dimension(self, geometry: str) -> tuple:
        """ Takes the geometry string as a parameter.
            Returns the tuple (width, height) corresponding to the dimension of the window.
            Returns (0, 0) if the the dimension is not find.
        """
        settings = geometry.split('+')
        if len(settings) == 3:
            dimensions = settings[0].split('x')
            if len(dimensions) == 2:
                if dimensions[0].isdigit() and dimensions[1].isdigit():
                    return (int(dimensions[0]), int(dimensions[1]))
        return (0, 0)
