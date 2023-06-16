"""
DONE:
  requirements.txt
  Fenêtre info : Redimensionner les images des boutons pour l'aide. 

TODO:
  Fenêtres : Vérifier les mises en forme (taille des boutons)
  Options : 
    Espace par étage (si rien, auto) => centrer le diagramme (offset)

  GUI.py
    mettre en place .scale sur self.can ? 
    et un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?
  OS : Vérifier si accès aux chemins correct sur Windows
Alternative/Existant : https://app.diagrams.net/
"""

import tkinter as tki
from diagram import *
from files import *
from GUI import *

if __name__ == "__main__":
    #diag = open_file("diagrams/diag2.txt")
    window = Window()
    window.draw()
    window.tk.bind('<Button-1>', window.left_click)
    window.tk.bind('<Button-3>', window.right_click)
    window.tk.bind('<Escape>', window.right_click)
    window.tk.mainloop()
