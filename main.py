"""
DONE:
    obj.lift_window(obj.window_edition.window) dans Decorators.disable_if_editing()
    Traduction des specs et des commentaires
TODO:
Renommer le projet en functions_synoptic ?
 
GUI.py   
    Bugs sur les tailles des fenêtres d'édition fonction et noeuds.
    A partir du quatrième paramètre de fonction.
    
    Paramètre : espace par étage (si rien, auto) => centrer le diagramme (offset)
    Frame : Proposer le dessin (et enregistrement) d'objet de type encadrement (pointillés)
      Défini par un nom, les fonctions englobées et marge ou position/dimensions, couleur, épaisseur de trait
    mettre en place .scale sur self.can ? 
    et un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?
    traduire la variable ancre par anchor
Options : permettre de paramétrer l'attribut. smooth_lines de Window
        rounded functions (up & down)

Alternative : https://app.diagrams.net/
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
