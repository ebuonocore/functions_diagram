"""
DONE:
  Paramètre de preferences.json en str
  Ne sauvegarde pas les positions de noeuds à [0, 0]
  Bouton Default pour configuration
  Modifier main_bckground_color lorsque modifié.
  Recharger les préférences par défaut
  Les traits utilisent line_color

TODO:
  Export image :
    Supprimer choix Background et forcer bck selon preferences
  Sauvegarder après Auto
  Fenêtre info : Minimiser hauteur
  Fenêtres Options/Settings
  colorchooser ne sert à rien pour l'instant : ne pointe pas vers la bonne cellule
  Options : 
    Boutons Default_light & Default_dark (Utf_8)
    smooth_lines & rounded functions (up & down) avec des box
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
