"""
DONE:
  Windows_settings renommé en Windows_pattern
  Fenêtre Option scrollable et mise en forme

TODO:
  Fenêtres Options/Settings et Infos
  Options : permettre de paramétrer l'attribut. smooth_lines de Window
        rounded functions (up & down)
  Paramètre : espace par étage (si rien, auto) => centrer le diagramme (offset)

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
