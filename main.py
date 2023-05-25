"""
DONE:
  traduction de la variable ancre par anchor
  Blocage de l'ouverture simultanée de deux fenêtres d'édition (noeud et fonction)
  Correction sur l'appel de tools.distance() avec des paramètres à None
  "tools.py", line 133, in create_node_description; Détection si position est à None
  Erreur dans "GUI.py" : _tkinter.TclError: bad window path name dans lift_window() résolu par try/except

TODO:
GUI.py   
  mettre en place .scale sur self.can ? 
    et un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?

Options : permettre de paramétrer l'attribut. smooth_lines de Window
        rounded functions (up & down)
Paramètre : espace par étage (si rien, auto) => centrer le diagramme (offset)

Fenêtres Options/Settings et Infos

Alternative/Existant : https://app.diagrams.net/
"""

from diagram import *
from files import *
from GUI import *
import tkinter as tki

if __name__ == "__main__":
    #diag = open_file("diagrams/diag2.txt")
    window = Window()
    window.draw()
    window.tk.bind('<Button-1>', window.left_click)
    window.tk.bind('<Button-3>', window.right_click)
    window.tk.bind('<Escape>', window.right_click)
    window.tk.mainloop()
