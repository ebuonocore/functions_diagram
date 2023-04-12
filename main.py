"""
Output Shortcuts : 
    Détection peu fiable. Modéliser le diagramme avec networkx. 
      Digraph : Bidirectionnels entre noeuds de la même zone, directionnel au sein des fonctions.
      Recherche de chemins préexistants entre les 2 noeuds cibles de la création de lien. 
        Dans les deux sens.
GUI.py     
    Un message d'erreur lors de l'appel de lift_window
      _tkinter.TclError: bad window path name ".!toplevel2"
    Proposer le dessin (et enregistrement) d'objet de type encadrement (pointillés)
      Défini par un nom, les fonctions englobées et marge ou position/dimensions, couleur, épaisseur de trait
    mettre en place .scale sur self.can ? 
    et un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?
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
