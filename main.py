"""
DONE:
  Rafraîchissement de l'affichage lors de la selection/deselection de Show output
  Supression des print non nécessaires
  Bugs sur les tailles des fenêtres d'édition fonction.

TODO:
Renommer le projet en functions_synoptic ?
 
GUI.py   
    _tkinter.TclError: bad window path name dans lift_window()
  Il est possible d'ouvrir une fenetre d'édition de noeud et une de fct en meme temps :[
  mettre en place .scale sur self.can ? 
    et un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?
  traduire la variable ancre par anchor
Options : permettre de paramétrer l'attribut. smooth_lines de Window
        rounded functions (up & down)
Paramètre : espace par étage (si rien, auto) => centrer le diagramme (offset)

Fenêtres Options/Settings et Infos

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
