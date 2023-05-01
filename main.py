"""
DONE:
    Création de la sous-classe Decorators dans GUI.Window.
    Décorateur disable_if_editing : Permet de bloquer les actions sur les boutons si la fenêtre d'édition est ouverte.

TODO:
bugs:
    Blocage partiel du programme si opération interdite pendant l'édition d'un element.
    Opération sur Nonetype dans tl.nearest(mouse_position, targets) si un élément supprimé entre temps.
    Ajout d'entrée dans une fonction / Fenetre d'édition ouverte / Déplacement de la fonction / Création de lien
    Un message d'erreur lors de l'appel de lift_window
      _tkinter.TclError: bad window path name ".!toplevel2"
      résoudre par try/except ? ou vérifier si la fenêtre n'a pas déjà été fermée.
          Dans GUI, si self.edition_in_progress, mémoriser la fenetre ouverte et cancel la fenetre si autre action demandée.
diagram et node:
    Traduire les specs  
GUI.py   
    Bugs sur les tailles des fenêtres d'édition fonction et noeuds.
    
    Paramètre : espace par étage ( si rien, auto) => centrer le diagramme (offset)
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
