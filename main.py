"""
DONE:


TODO:
  Fenêtres : Vérifier les mises en forme (taille des boutons)
  Fenêtre info : Minimiser hauteur
  Options : 
    Espace par étage (si rien, auto) => centrer le diagramme (offset)

  GUI.py
    mettre en place .scale sur self.can ? 
    et un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?

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
