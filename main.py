"""
DONE:
    Création de la classe Design
    Gestion des étages
    Rectification des positions des étages droite/gauche
    Réparation de la MAJ des dimensions de fonctions
    window_edition: Fenêtre trop haute  
TODO:
design :
    refactoring : renommer level en floor
diagram et node:
    supprimer toutes ref à .zone (update_zones...)
    Traduire les specs  
GUI.py     
    Frame : Proposer le dessin (et enregistrement) d'objet de type encadrement (pointillés)
      Défini par un nom, les fonctions englobées et marge ou position/dimensions, couleur, épaisseur de trait
    mettre en place .scale sur self.can ? 
    et un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?
    Un message d'erreur lors de l'appel de lift_window
      _tkinter.TclError: bad window path name ".!toplevel2"
      résoudre par try/except ?
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
